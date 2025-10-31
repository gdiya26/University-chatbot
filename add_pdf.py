import os
import argparse
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
# Import both PDF and Text loaders
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
VECTORSTORE_PATH = "data/vectorstore"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_embeddings():
    """Loads the HuggingFace embedding model."""
    print(f"📦 Loading embedding model: {EMBEDDING_MODEL}...")
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )

def load_documents(file_path):
    """
    Loads and splits a file (PDF or TXT) into chunks.
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return None
    
    # --- NEW: Check file extension ---
    if file_path.lower().endswith(".pdf"):
        print(f"📄 Loading PDF: {file_path}...")
        loader = PyPDFLoader(file_path)
    elif file_path.lower().endswith(".txt"):
        print(f"📄 Loading Text File: {file_path}...")
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        print(f"❌ Error: Unsupported file type: {file_path}")
        print("This script only supports .pdf and .txt files.")
        return None
    
    documents = loader.load()
    
    # --- The rest is the same ---
    print(f"Splitting {len(documents)} document(s) into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} text chunks from the file.")
    return chunks

def update_vectorstore_with_file(file_path):
    """Loads existing store, adds new file chunks, and saves."""
    
    # 1. Check if vector store exists
    if not os.path.exists(VECTORSTORE_PATH):
        print(f"❌ Error: No existing vector store found at {VECTORSTORE_PATH}.")
        print("Please run your main embedding script first to create it.")
        return

    # 2. Load embeddings and new file
    embeddings = load_embeddings()
    new_chunks = load_documents(file_path)
    
    if not new_chunks:
        return

    # 3. Load existing vector store
    print(f"📂 Loading existing vector store from {VECTORSTORE_PATH}...")
    try:
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return

    # 4. Add new documents to the store
    print(f"➕ Adding {len(new_chunks)} new chunks to the vector store...")
    vectorstore.add_documents(new_chunks)

    # 5. Save the updated vector store
    print(f"💾 Saving updated vector store back to {VECTORSTORE_PATH}...")
    vectorstore.save_local(VECTORSTORE_PATH)
    
    print(f"\n✅ Successfully added {file_path} to the vector store!")

# --- Main execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a PDF or TXT file to the FAISS vector store.")
    parser.add_argument("file_path", type=str, help="The file path of the .pdf or .txt file to add.")
    
    args = parser.parse_args()
    
    update_vectorstore_with_file(args.file_path)