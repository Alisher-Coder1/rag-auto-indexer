import os
import json
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader

KNOWLEDGE_BASE_PATH = "knowledge_base.txt"
INDEX_DIR = "faiss_index"
HASH_STORE_PATH = "kb_hash.json"
INDEX_FILE_NAME = "index.faiss"
DOCSTORE_FILE_NAME = "index.pkl"


def compute_file_hash(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_kb_hash(hash_path: str = HASH_STORE_PATH) -> str | None:
    if not os.path.exists(hash_path):
        return None
    try:
        with open(hash_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("hash")
    except (json.JSONDecodeError, OSError):
        print("[WARN] Failed to read kb_hash.json, will rebuild.")
        return None


def save_kb_hash(hash_value: str, hash_path: str = HASH_STORE_PATH) -> None:
    import datetime

    data = {"hash": hash_value, "last_updated": datetime.datetime.now().isoformat()}
    tmp_path = hash_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, hash_path)


def faiss_index_exists() -> bool:
    index_path = os.path.join(INDEX_DIR, INDEX_FILE_NAME)
    docstore_path = os.path.join(INDEX_DIR, DOCSTORE_FILE_NAME)
    return os.path.exists(index_path) and os.path.exists(docstore_path)


def build_and_save_faiss_index():
    loader = TextLoader(KNOWLEDGE_BASE_PATH, encoding="utf-8")
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    index = FAISS.from_documents(chunks, embeddings)

    os.makedirs(INDEX_DIR, exist_ok=True)
    index.save_local(INDEX_DIR)

    return index


def load_faiss_index():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    index = FAISS.load_local(
        INDEX_DIR, embeddings, allow_dangerous_deserialization=True
    )
    return index


def get_db_index():
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        raise FileNotFoundError(f"Knowledge base not found: {KNOWLEDGE_BASE_PATH}")

    current_hash = compute_file_hash(KNOWLEDGE_BASE_PATH)
    stored_hash = load_kb_hash()
    index_exists = faiss_index_exists()

    if not index_exists:
        print("[INFO] Index not found, rebuilding...")
        index = build_and_save_faiss_index()
        save_kb_hash(current_hash)
        return index

    if stored_hash is None:
        print("[WARN] Hash file missing or corrupted, rebuilding to synchronize...")
        index = build_and_save_faiss_index()
        save_kb_hash(current_hash)
        return index

    if stored_hash != current_hash:
        print("[INFO] knowledge_base.txt changed, rebuilding index...")
        index = build_and_save_faiss_index()
        save_kb_hash(current_hash)
        return index

    print("[INFO] Index is up-to-date, loading existing.")
    return load_faiss_index()


def query_index(query: str) -> list[str]:
    index = get_db_index()
    results = index.similarity_search(query, k=3)
    return [doc.page_content for doc in results]


if __name__ == "__main__":
    print(query_index("основные темы базы знаний"))
