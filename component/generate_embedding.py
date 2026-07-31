import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from supabase import create_client
import re


load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_ANON_KEY"],
)

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434",
    model_name="qwen3-embedding:4b",
)


def load_documents_from_directory(directory_path):
    print("====== Loading document from directory ======")
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            with open(
                os.path.join(directory_path, filename), "r", encoding="utf-8"
            ) as file:
                documents.append({"id": filename, "text": file.read()})
    return documents


def split_text(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def chunked_documents(documents):
    chunked_documents_array = []

    for doc in documents:
        chunks = split_text(doc["text"])
        print("==== Split text into chunks ====")
        for i, chunk in enumerate(chunks):
            chunked_documents_array.append(
                {"id": f"{doc['id']}_chunk{i+1}", "text": chunk}
            )

    return chunked_documents_array


def get_embedding(text):
    embedding = ollama_ef([text])[0]

    if hasattr(embedding, "tolist"):
        return embedding.tolist()
    return list(embedding)


def generate_embedding(processed_chunks):
    for doc in processed_chunks:
        print("===== Generating embedding ====")
        doc["embedding"] = get_embedding(doc["text"])
        print(f"Generated embedding for {doc['id']}")


def save_chunks_to_supabase(processed_chunks, card_id: str, table_name="card_chunks", batch_size=25):
    records_to_insert = []

    for doc in processed_chunks:
        raw_text = doc["text"]
        embedding_vector = get_embedding(raw_text)

        records_to_insert.append(
            {
                "card_id": card_id,
                "card_name": card_name, 
                "raw_text": raw_text,
                "embedding": embedding_vector,
            }
        )

    print(
        f"\n====== Uploading {len(records_to_insert)} records to Supabase in batches of {batch_size} ======"
    )

    for i in range(0, len(records_to_insert), batch_size):
        batch = records_to_insert[i : i + batch_size]
        supabase.table(table_name).insert(batch).execute()


def normalize_card_name(name: str) -> str:
    if not name:
        return ""

    cleaned = re.sub(r"[®™©]", "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned.title()


def get_or_create_card_id(card_name: str, issuer: str = "Unknown") -> str | None:
    clean_name = normalize_card_name(card_name)

    try:
        response = (
            supabase.table("credit_cards")
            .select("id")
            .ilike("card_name", clean_name)
            .execute()
        )

        if response.data and len(response.data) > 0:
            card_id = response.data[0]["id"]
            print(f" Found existing card_id for '{clean_name}': {card_id}")
            return card_id

        print(f" Creating new card entry for '{clean_name}'...")
        insert_res = (
            supabase.table("credit_cards")
            .insert({"card_name": clean_name, "issuer": issuer})
            .execute()
        )

        card_id = insert_res.data[0]["id"]
        print(f" Created new card_id: {card_id}")
        return card_id

    except Exception as e:
        print(f" Error fetching/creating card_id: {e}")
        return None


if __name__ == "__main__":
    directory_path = "./card_details"

    documents = load_documents_from_directory(directory_path)
    processed_chunks = chunked_documents(documents)

    card_name = "CHASE SAPPHIRE PREFERRED CREDIT CARD"
    card_id = get_or_create_card_id(card_name=card_name, issuer="Chase")

    if card_id:
        save_chunks_to_supabase(
            processed_chunks=processed_chunks,
            card_id=card_id,
            table_name="card_chunks",
        )
    else:
        print("Failed to get or create card_id.")