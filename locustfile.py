"""Locustfile for benchmarking model serving solutions on Google Cloud."""

# %% IMPORTS

import json
import typing as T

import dotenv as de
import google.auth as ga
import google.auth.transport.requests as gatr
import locust as lc

# %% OPTIONS


@lc.events.init_command_line_parser.add_listener
def parse(parser):
    """Add extra arguments for Locust."""
    parser.add_argument("--data", type=str)
    parser.add_argument("--model", type=str)
    parser.add_argument("--thinking", type=int, default=0)
    parser.add_argument("--api-key", type=str, env_var="API_KEY")
    parser.add_argument("--project_id", type=str, env_var="PROJECT_ID")
    parser.add_argument("--project_number", type=str, env_var="PROJECT_NUMBER")
    parser.add_argument(
        "--location", type=str, env_var="LOCATION", default="us-central1"
    )
    parser.add_argument("--endpoint_id", type=str, env_var="ENDPOINT_ID")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max_output_tokens", type=int, default=1000)


# %% ENVIRONS

ENVIRONS = de.dotenv_values()
PROJECT_NUMBER = ENVIRONS["PROJECT_NUMBER"]
ENDPOINT_ID = ENVIRONS.get("ENDPOINT_ID", None)
LOCATION = ENVIRONS.get("LOCATION", "us-central1")

# %% TASKS


class Benchmark:
    @property
    def options(self) -> T.Any:
        """Return the parsed options from the command line."""
        return self.environment.parsed_options  # type: ignore

    @property
    def bearer(self) -> str:
        """Return the bearer token for authentication."""
        credentials, _ = ga.default()
        if not credentials.valid:  # refresh if needed
            credentials.refresh(gatr.Request())
        token = credentials.token
        assert token, (
            "No bearer token found. Please authenticate with `gcloud auth application-default login`."
        )
        return token

    def iter_data(self) -> T.Generator[str, None, None]:
        """Yield instructions from the data file."""
        with open(self.options.data, "r") as reader:
            for line in reader:
                content = json.loads(line)
                instruction = content["instruction"]
                yield instruction


class VertexAIMaaS(Benchmark, lc.HttpUser):
    """Locust user for benchmarking Vertex AI Model as a Service."""

    host: str = (
        f"https://{LOCATION}-aiplatform.googleapis.com"
        if LOCATION != "global"
        else "https://aiplatform.googleapis.com"
    )

    @lc.task
    def predict(self):
        """Send a prediction request to the Vertex AI Model as a Service."""
        config = {
            "temperature": self.options.temperature,
            "thinkingConfig": {"thinkingBudget": 0},
            "maxOutputTokens": self.options.max_output_tokens,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer}",
        }
        url = f"/v1/projects/{self.options.project_id}/locations/{self.options.location}/publishers/google/models/{self.options.model}:generateContent"
        for text in self.iter_data():
            contents = [{"role": "user", "parts": [{"text": text}]}]
            body = {"contents": contents, "generationConfig": config}
            self.client.post(url=url, json=body, headers=headers)


class VertexAIEndpoint(Benchmark, lc.HttpUser):
    """Locust user for benchmarking Vertex AI Endpoint."""

    host: str = (
        f"https://{ENDPOINT_ID}.{LOCATION}-{PROJECT_NUMBER}.prediction.vertexai.goog"
    )

    @lc.task
    def predict(self):
        """Send a prediction request to the Vertex AI endpoint."""
        url = f"/v1/projects/{self.options.project_number}/locations/{self.options.location}/endpoints/{self.options.endpoint_id}:predict"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer}",
        }
        for text in self.iter_data():
            body = {
                "instances": [
                    {
                        "@requestFormat": "chatCompletions",
                        "messages": [
                            {
                                "role": "user",
                                "content": text,
                            }
                        ],
                        "max_tokens": self.options.max_output_tokens,
                        "temperature": self.options.temperature,
                    }
                ]
            }
            self.client.post(url=url, json=body, headers=headers)


class CloudRunOllama(Benchmark, lc.HttpUser):
    """Locust user for benchmarking Cloud Run Ollama."""

    host: str = "http://localhost:8080"

    @lc.task
    def predict(self):
        """Send a prediction request to the Cloud Run Ollama."""
        url = "/api/generate"
        params = {"key": self.options.api_key}
        for text in self.iter_data():
            body = {
                "prompt": text,
                "model": self.options.model,
                "options": {
                    "temperature": self.options.temperature,
                    "num_predict": self.options.max_output_tokens,
                },
            }
            self.client.post(url=url, json=body, params=params)
