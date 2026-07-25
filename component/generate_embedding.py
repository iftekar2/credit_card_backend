import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from supabase import create_client

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


def save_chunks_to_supabase(
    processed_chunks, table_name="embedded_data", batch_size=25
):
    records_to_insert = []

    for doc in processed_chunks:
        raw_text = doc["text"]
        card_name = doc.get("card_name", "Unknown")

        print(f"Generating embedding for chunk: {doc['id']}")
        embedding_vector = get_embedding(raw_text)

        records_to_insert.append(
            {
                "card_name": card_name,
                "raw_text": raw_text,
                "embedding": embedding_vector,
            }
        )

    print(
        f"\n====== Uploading {len(records_to_insert)} records to Supabase in batches of {batch_size} ======"
    )

    # Split records_to_insert into smaller batches
    for i in range(0, len(records_to_insert), batch_size):
        batch = records_to_insert[i : i + batch_size]
        try:
            supabase.table(table_name).insert(batch).execute()
            print(
                f" Successfully inserted batch {i // batch_size + 1} ({len(batch)} records)"
            )
        except Exception as e:
            print(f" Error saving batch {i // batch_size + 1} to Supabase: {e}")
            # Optional: Add retry logic here if needed


# --- Execution Flow ---
if __name__ == "__main__":
    directory_path = "./card_details"
    documents = load_documents_from_directory(directory_path)
    processed_chunks = chunked_documents(documents)
    save_chunks_to_supabase(processed_chunks, table_name="embedded_data")