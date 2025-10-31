# Nirma University Chatbot

An intelligent AI-powered chatbot for Nirma University that provides comprehensive information about admissions, courses, campus life, placements, and more. Built with RAG (Retrieval-Augmented Generation) architecture using LangChain, FAISS, and OpenAI.

## 🎯 Overview

This chatbot scrapes and indexes content from the Nirma University website to answer student queries accurately. It uses:
- **LangChain** for building RAG pipelines
- **FAISS** for vector storage and similarity search
- **HuggingFace Embeddings** for text vectorization
- **OpenAI GPT** for natural language responses
- **Flask** for backend API
- **Beautiful Soup & Scrapy** for web scraping

## ✨ Features

- 🤖 **Smart Q&A**: Answers questions about admissions, courses, campus, placements, and more
- 🔍 **Context-Aware**: Retrieves relevant information from university website data
- 💬 **Modern UI**: Clean, responsive chat interface
- 🎨 **Widget Support**: Embeddable chatbot widget for any website
- 📊 **Multiple Scraping Methods**: Supports BeautifulSoup, Scrapy, and custom crawlers
- 🔗 **Quick Actions**: Pre-defined buttons for common questions

## 🏗️ Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│      Flask Backend (app.py)      │
│  ┌────────────────────────────┐  │
│  │   Retrieval QA Chain       │  │
│  └────────┬───────────────────┘  │
│           │                       │
│  ┌────────▼───────────────────┐  │
│  │  FAISS Vector Store        │  │
│  │  (Similarity Search)       │  │
│  └────────┬───────────────────┘  │
│           │                       │
│  ┌────────▼───────────────────┐  │
│  │  OpenAI LLM                │  │
│  │  (GPT-4o-mini)             │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  AI Response    │
└─────────────────┘
```

## 📁 Project Structure

```
University-chatbot/
├── app.py                      # Main Flask application
├── embeddings.py               # Vector store builder
├── scraper.py                  # BeautifulSoup-based web scraper
├── crawl.py                    # Advanced crawling script
├── test_ollama.py              # Ollama LLM testing
├── requirements.txt            # Python dependencies
├── widget-embed.html           # Chatbot widget for embedding
│
├── frontend/                   # Frontend interface
│   ├── index.html             # Main chatbot UI
│   ├── chatbot.js             # Client-side JavaScript
│   └── chatbot.css            # Styling
│
├── nirma_crawl/               # Scrapy spider project
│   ├── nirma_crawl/
│   │   ├── spiders/
│   │   │   └── nirma_spider.py
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   └── settings.py
│   └── scrapy.cfg
│
├── data/                      # Generated data (created during setup)
│   ├── raw/                   # Scraped raw content
│   └── vectorstore/           # FAISS vector database
│
├── nirmauni_all_texts.txt     # Aggregated scraped text
├── nirmauni_urls.txt          # Discovered URLs
└── README.md                  # This file
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- pip
- OpenAI API key (optional, can use Ollama for local LLM)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd University-chatbot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Note**: If you don't have an OpenAI API key, you can modify `app.py` to use Ollama with a local LLM model.

### Step 4: Scrape University Website

Choose one of the scraping methods:

#### Option A: Using BeautifulSoup Scraper (Recommended for beginners)

```bash
python scraper.py
```

#### Option B: Using Advanced Crawler

```bash
python crawl.py
```

#### Option C: Using Scrapy

```bash
cd nirma_crawl
scrapy crawl nirma_txt
```

All methods will save scraped content to `data/raw/`.

### Step 5: Build Vector Database

Generate embeddings and create the FAISS vector store:

```bash
python embeddings.py
```

This will:
- Load all scraped documents
- Split them into chunks
- Generate embeddings using HuggingFace models
- Create and save a FAISS vector store to `data/vectorstore/`

### Step 6: Run the Application

```bash
python app.py
```

The chatbot will be available at:
- **API**: `http://localhost:5000`
- **Frontend**: `http://localhost:5000/`

## 🎮 Usage

### Web Interface

1. Open `http://localhost:5000` in your browser
2. Type your question in the chat input
3. Receive AI-powered responses with source citations

### API Endpoints

#### Chat Endpoint

```bash
POST /chat
Content-Type: application/json

{
    "message": "What are the admission requirements for MBA?"
}
```

Response:
```json
{
    "response": "The admission requirements for MBA...",
    "sources": [
        "https://www.nirmauni.ac.in/admissions",
        "https://www.nirmauni.ac.in/imnu"
    ],
    "status": "success"
}
```

#### Health Check

```bash
GET /health
```

#### Quick Answers

```bash
GET /quick-answer/contact
GET /quick-answer/location
```

### Embedding the Widget

Copy the content from `widget-embed.html` and embed it on any webpage. The widget will automatically connect to your chatbot API.

## 🔧 Configuration

### Adjusting Chunking Strategy

In `embeddings.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,        # Adjust chunk size
    chunk_overlap=150,     # Adjust overlap
    separators=["\n\n", "\n", " ", ""]
)
```

### Changing Number of Retrieved Contexts

In `app.py`:

```python
retriever=vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 8}  # Number of chunks to retrieve
)
```

### Switching LLM Models

#### OpenAI (default)

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.3,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)
```

#### Ollama (Local)

```python
from langchain_community.llms import Ollama

llm = Ollama(model="llama3", temperature=0.3)
```

Make sure Ollama is installed and the model is pulled:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3
```

## 🛠️ Customization

### Adding New Scraping Sources

1. Create a new scraper function in `scraper.py`
2. Save content to `data/raw/`
3. Rebuild vector store with `python embeddings.py`

### Modifying the Prompt Template

In `app.py`, customize the system prompt:

```python
template = """You are a helpful AI assistant for Nirma University. 
Use the following context from the university's website to answer the question.
If you don't know the answer based on the context, say "I don't have that information..."

Context: {context}
Question: {question}

Provide a clear, concise, and friendly answer.
Answer:"""
```

### Styling the Frontend

Modify `frontend/chatbot.css` or `frontend/index.html` to customize the chatbot appearance.

## 📊 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Flask** | Web framework for API |
| **LangChain** | RAG pipeline orchestration |
| **FAISS** | Vector similarity search |
| **HuggingFace** | Text embeddings (all-MiniLM-L6-v2) |
| **OpenAI** | Language model (GPT-4o-mini) |
| **BeautifulSoup** | HTML parsing |
| **Scrapy** | Web crawling framework |
| **Trafilatura** | Clean text extraction |
| **PyTorch** | Deep learning backend |
| **Transformers** | NLP model support |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Nirma University** for providing the public website content
- **LangChain** for the excellent RAG framework
- **OpenAI** for GPT models
- **HuggingFace** for embeddings and transformers

## 📧 Contact

For questions or support:
- **Email**: admissions@nirmauni.ac.in
- **Phone**: +91-2717-241911
- **Website**: https://www.nirmauni.ac.in

## 🐛 Troubleshooting

### Issue: "Vector store not found"

**Solution**: Run `python embeddings.py` to build the vector database first.

### Issue: "OpenAI API key not found"

**Solution**: 
1. Create a `.env` file
2. Add `OPENAI_API_KEY=your_key`
3. Or switch to Ollama for local LLM

### Issue: Import errors with langchain

**Solution**: Make sure you're using the correct versions:
```bash
pip install langchain==0.3.7 langchain-community==0.3.7
```

### Issue: Scraping doesn't find content

**Solution**:
1. Check if the website structure has changed
2. Verify robots.txt permissions
3. Try different scraping methods (scraper.py vs crawl.py)

## 🎓 Future Enhancements

- [ ] Add conversation history/memory
- [ ] Support for multi-language queries
- [ ] Integration with university databases
- [ ] Analytics dashboard for common questions
- [ ] Voice interface support
- [ ] Mobile app version
- [ ] Real-time updates from university website

---

**Made with ❤️ for Nirma University**
