from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
# ------------------------
# LangChain imports (0.3.7)
# ------------------------
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

vectorstore = None
qa_chain = None

def initialize_chatbot():
    global vectorstore, qa_chain

    print("🚀 Initializing Nirma University Chatbot...")

    # Embeddings
    print("📦 Loading embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    # Load vectorstore
    print("📂 Loading vector store...")
    vectorstore_path = "data/vectorstore"
    if not os.path.exists(vectorstore_path):
        print("❌ Vector store not found! Please run embeddings.py first.")
        return False

    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    # Initialize LLM (Ollama local model)
    llm = ChatOpenAI(
    model_name="gpt-4o-mini",  # or "gpt-4" / "gpt-3.5-turbo" if you prefer
    temperature=0.3,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

    # Prompt template
    template = """You are a helpful AI assistant for Nirma University. 
Use the following context from the university's website to answer the question.
If you don't know the answer based on the context, say "I don't have that information in my knowledge base. Please contact the university directly at admissions@nirmauni.ac.in or call +91-2717-241911."

Context: {context}

Question: {question}

Provide a clear, concise, and friendly answer. If relevant, include specific details like dates, requirements, or contact information.

Answer:"""

    PROMPT = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    # Create QA chain
    print("🔗 Creating QA chain...")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 8}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    print("✅ Chatbot initialized successfully!\n")
    return True

# ------------------------
# Flask endpoints
# ------------------------
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health', methods=['GET'])
def home():
    return jsonify({"status": "running", "message": "Nirma University Chatbot API", "version": "1.0"})


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message = data["message"].strip()
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Get response from QA chain
        print(f"📥 Query: {user_message}")
        result = qa_chain.invoke({"query": user_message})

        answer = result["result"]
        sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]

        print(f"📤 Response: {answer[:100]}...")
        return jsonify({"response": answer, "sources": sources[:3], "status": "success"})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": "An error occurred processing your request", "details": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "vectorstore_loaded": vectorstore is not None,
        "qa_chain_ready": qa_chain is not None
    })

QUICK_ANSWERS = {
    "contact": "You can contact Nirma University at:\n📧 Email: info@nirmauni.ac.in\n📞 Phone: +91-2717-241911\n📍 Address: Sarkhej-Gandhinagar Highway, Ahmedabad - 382481, Gujarat, India",
    "location": "Nirma University is located at Sarkhej-Gandhinagar Highway, Ahmedabad - 382481, Gujarat, India.",
}

@app.route('/quick-answer/<key>', methods=['GET'])
def quick_answer(key):
    if key in QUICK_ANSWERS:
        return jsonify({"response": QUICK_ANSWERS[key], "status": "success"})
    return jsonify({"error": "Quick answer not found"}), 404

# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    if initialize_chatbot():
        print("🌐 Starting Flask server at http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        print("❌ Failed to initialize chatbot. Exiting...")

