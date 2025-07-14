# https://just.systems/man/en/

# REQUIRES

uv := require("uv")

# SETTINGS

set dotenv-load

# VARIABLES

SOURCES := "*.py"

# TASKS

# benchmark a solution
bench module="VertexAIMaaS" model="gemini-2.5-flash" data="data/databricks-dolly-15k.jsonl" users="250" run-time="5m" spawn-rate="1":
	uv run locust --headless --csv results/{{module}}_{{model}} --csv-full-history {{module}} \
	--users {{users}} --run-time {{run-time}} --spawn-rate {{spawn-rate}} --model="{{model}}" --data="{{data}}"

# benchmark all solutions
benchs: (bench "VertexAIMaaS" "gemini-2.5-flash-lite-preview-06-17") (bench "VertexAIMaaS" "gemini-2.5-flash") (bench "VertexAIEndpoint" "gemma-3-12b-it") (bench "CloudRun" "gemma3:12b")

# check the source code
check:
	uv run ruff format --check {{SOURCES}}
	uv run ruff check {{SOURCES}}
	uv run ty check {{SOURCES}}

# format the source code
format:
    uv run ruff check --select=I --fix {{SOURCES}}
    uv run ruff format {{SOURCES}}

# install the project
install:
    uv sync --all-groups

# setup the cloud run model serving
setup-cloud-run model="gemma3-12b":
	gcloud run deploy {{model}} \
		--cpu=8 --max-instances=2 --memory=32Gi \
		--gpu=1 --gpu-type=nvidia-l4 --no-gpu-zonal-redundancy \
		--image=us-docker.pkg.dev/cloudrun/container/gemma/{{model}} \
		--timeout=600 --concurrency=8 --ingress=all \
		--allow-unauthenticated --no-cpu-throttling \
		--project=$PROJECT_ID --region=$LOCATION \
		--set-env-vars OLLAMA_NUM_PARALLEL=4 \
		--set-env-vars API_KEY=$API_KEY

# proxy the cloud run model serving
proxy-cloud-run model="gemma3-12b":
	gcloud run services proxy {{model}} --port=8080 --region=$LOCATION --project=$PROJECT_ID

# destroy the cloud run model serving
destroy-cloud-run model="gemma3-12b":
	gcloud run services delete {{model}} --region=$LOCATION --project=$PROJECT_ID
