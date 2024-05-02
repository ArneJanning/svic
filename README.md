A small and simple backend downloading and indexing [SVIC Podcast](https://www.youtube.com/@svicpodcast) currently running in Azure OpenAI, Azure OpenAIs embedding model using llama-index, and a FAISS vector store, but it could run anywhere, e.g. locally on Ollama/Llama 3/Weaviate or whatever by just changing a couple of lines of code.

Exposes a simple OpenAPI in FastAPI with just one endpoint:

```curl -X 'POST' \
  'https://svic.textwork.ai/answer?question=your_question' \
  -H 'accept: application/json' \
  -d ''
```

You will need an .env file in the root directory with the following content to run this on Azure OpenAI:
```AZURE_OPENAI_API_KEY="your_azure_api_key" 
AZURE_OPENAI_ENDPOINT="https://<your_endpoint>.openai.azure.com/"
OPENAI_API_VERSION="whatever_version_is_currently_supported"```