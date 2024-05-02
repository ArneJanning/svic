from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, APIRouter, Response
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import os
import scrapetube
import faiss
from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.core import VectorStoreIndex, Settings, load_index_from_storage, VectorStoreIndex, StorageContext
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.query_engine import CitationQueryEngine
from llama_index.vector_stores.faiss import FaissVectorStore

# dimensions of ada-embedding-002
d = 1536
faiss_index = faiss.IndexFlatL2(d)

def get_transcripts():
    # "UCRgohrQBQfEx4X32ZckEoow" is the channel_id of SVIC Podcast
    videos = scrapetube.get_channel("UCRgohrQBQfEx4X32ZckEoow")

    video_ids = []

    for video in videos:
        video_id = video["videoId"]
        video_ids.append(f"https://youtu.be/{video_id}")

    loader = YoutubeTranscriptReader()
    transcripts = loader.load_data(
        # some videos have subtitles disabled, so we only take the first 50 videos
        ytlinks=video_ids[0:50]
    )
    return transcripts

llm = AzureOpenAI(
    deployment_name="gpt-4-turbo",
    api_version=os.getenv("OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

embed = AzureOpenAIEmbedding(
    deployment_name="embed",
    api_version=os.getenv("OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

Settings.llm = llm
Settings.embed_model = embed

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic before yielding
    transcripts = get_transcripts()
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        transcripts, storage_context=storage_context
    )
    # save index to disk
    index.storage_context.persist()
    global query_engine
    query_engine = CitationQueryEngine.from_args(
        index,
        similarity_top_k=5,
        citation_chunk_size=512,
    )
    yield
    # shutdown logic after yielding  

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],)

@app.post("/answer")
async def answer(question: str):
    answer = query_engine.query(question)
    return {"answer": answer}

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=9001)