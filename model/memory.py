from utils.config.logger import log_memory
from dotenv import load_dotenv
from pymilvus.milvus_client import MilvusClient
from pymilvus.model.dense import SentenceTransformerEmbeddingFunction
import os
from pathlib import Path

basepath = Path(__file__).resolve().parent.parent
load_dotenv(basepath / ".env")

client = MilvusClient(
    uri = os.getenv("MILVUS-URI") or "",
    token = os.getenv("MILVUS-TOKEN") or "",
    password= os.getenv("MILVUS-PASSWORD") or ""
)

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    device = "cuda:0",
    batch_size=16,
    normalize_embeddings=True
)

