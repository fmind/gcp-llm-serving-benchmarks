# GCP LLM Serving Benchmarks

This project provides a comprehensive benchmark analysis of various solutions for serving Large Language Models (LLMs) on Google Cloud Platform (GCP). The goal is to evaluate the scalability, performance, and cost-effectiveness of each approach to provide clear guidance for deploying production-grade LLM applications.

This benchmark focuses on managed and performance-optimized solutions, deliberately excluding basic, non-specialized deployments.

---

## Models

### Gemini

### Gemma

https://ai.google.dev/gemma/docs/core#sizes

## 🚀 Solutions Under Review

We are evaluating the following four serving configurations to understand their trade-offs.

### 1\. Vertex AI for First-Party Models

- **Description**: This approach uses Google's fully managed, serverless AI platform, **Vertex AI**, to serve Google's own state-of-the-art models.

- **Model**: Gemini 2.5

- **Key Features**:

  - No infrastructure management required.

  - Pay-per-use pricing.

  - Seamless integration with the GCP ecosystem.

  - Built-in scalability and reliability managed by Google.

TODO:
- https://cloud.google.com/blog/products/ai-machine-learning/learn-how-to-handle-429-resource-exhaustion-errors-in-your-llms
- https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput/error-code-429
- https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas

### 2\. Vertex AI for Open Models (Optimized)

- **Description**: Leveraging **Vertex AI Model Garden and Endpoints** with pre-built, optimized containers for serving popular open-source models.

- **Model**: Gemma 3

- **Key Features**:

  - Fully managed infrastructure with GPU acceleration.

  - Simplified deployment for open models without manual container setup.

  - Benefits from Vertex AI's scaling and monitoring capabilities.

TODO:
- https://cloud.google.com/vertex-ai/docs/general/deployment
- https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemma3
- https://cloud.google.com/vertex-ai/docs/predictions/get-online-predictions
- https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/predict
- https://cloud.google.com/vertex-ai/docs/reference/rest#rest_endpoints
- https://cloud.google.com/vertex-ai/docs/general/deployment#target_utilization_and_configuration
- https://cloud.google.com/vertex-ai/pricing

### 3\. Cloud Run + GPU

- **Description**: A serverless approach where the open-source model is packaged into a container and deployed on **Cloud Run**. Cloud Run automatically scales the service up or down, even to zero, based on incoming traffic.

- **Model**: Gemma 3

- **Key Features**:

  - Combines the simplicity of serverless with the power of GPU acceleration.

  - Ideal for applications with variable or unpredictable traffic.

  - Cost-effective, as you only pay when requests are being processed.

TODO:
- https://cloud.google.com/run/docs/configuring/services/gpu
- https://ai.google.dev/gemma/docs/run#choose-a-framework
- https://cloud.google.com/run/docs/run-gemma-on-cloud-run
- https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/self-deployed-models
- https://cloud.google.com/vertex-ai/generative-ai/docs/model-garden/deploy-and-inference-tutorial
- https://codelabs.developers.google.com/codelabs/how-to-run-inference-cloud-run-gpu-vllm#0
- https://github.com/google-gemini/gemma-cookbook/blob/main/Demos/Gemma-on-Cloudrun/README.md
- https://cloud.google.com/run/docs/run-gemma-on-cloud-run#set-concurrency-for-performance

Limits:
- Limit concurrency based scaling

Solutions:
- https://github.com/GoogleCloudPlatform/generative-ai/blob/main/open-models/serving/cloud_run_vllm_gemma3_inference.ipynb

### 4\. GKE + High-Performance Serving Framework (vLLM)

- **Description**: This option involves deploying the model on a **Google Kubernetes Engine (GKE)** cluster using a specialized, high-performance serving framework. We will use **vLLM**, which optimizes inference through techniques like PagedAttention for increased throughput.

- **Model**: Gemma 3

- **Key Features**:

  - Maximum performance and throughput for open-source models.

  - Fine-grained control over the serving environment and scaling policies via GKE.

  - Represents a highly scalable, production-grade architecture for demanding workloads.

TODO:
- https://cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm
- https://cloud.google.com/kubernetes-engine/docs/integrations/ai-infra
- https://cloud.google.com/kubernetes-engine/docs/how-to/serve-llm-l4-ray
- https://cloud.google.com/kubernetes-engine/docs/tutorials/serve-gemma-gpu-vllm#gemma-3-12b-it

Limits:
- Quota

---

## ❌ Excluded Options

For this benchmark, we intentionally excluded the following options to maintain focus on managed and performance-optimized solutions:

- **Compute Engine (GCE)**: This approach requires significant manual setup and operational overhead for infrastructure and scaling, falling outside our focus on streamlined, managed solutions.
