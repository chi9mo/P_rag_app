from pathlib import Path

import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_PATH = BASE_DIR / "medicine-package-insert.pdf"
QDRANT_PATH = str(BASE_DIR / "qdrant_storage")
COLLECTION_NAME = "medicine"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"
VECTOR_SIZE = 1024


def _load_pdf() -> list[Document]:
    docs = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                docs.append(Document(
                    page_content=text,
                    metadata={"page": page.page_number},
                ))
    return docs


def _split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(docs)


def _collection_exists(client: QdrantClient) -> bool:
    return any(c.name == COLLECTION_NAME for c in client.get_collections().collections)


def build_index() -> QdrantVectorStore:
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    client = QdrantClient(path=QDRANT_PATH)

    if _collection_exists(client):
        print("インデックスが既に存在します。スキップします。")
        return QdrantVectorStore(client=client, collection_name=COLLECTION_NAME, embedding=embeddings)

    print("インデックスを構築中...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    docs = _load_pdf()
    chunks = _split_documents(docs)

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    vectorstore.add_documents(chunks)
    print(f"インデックス構築完了: {len(chunks)} チャンク")
    return vectorstore
