# 📚 RepoRAG: AI-Powered Codebase Q&A

**RepoRAG** is an intelligent assistant that lets you **chat with any public GitHub repository**.  
It uses a **Retrieval-Augmented Generation (RAG)** pipeline to analyze source code and documentation,  
allowing you to ask complex questions and get accurate, context-aware answers.

> This project was built as a learning exercise to explore applying RAG to the unique challenges of understanding software projects.

---

## ✨ Key Features

- **GitHub Repository Ingestion** – Analyze any public GitHub repo by simply providing its URL.  
- **Multi-Language Code Understanding** – Intelligently chunks code by functions and classes for languages like Python, JavaScript, Java, and more.  
- **Hybrid Search** – Combines semantic and keyword search for highly relevant results.  
- **Flexible Backends** – Supports both free, local embedding models and high-performance OpenAI models via API.  
- **Interactive UI** – Clean and simple web interface built with Streamlit.  

---

## ⚙️ How It Works

1. **Clone & Parse** – RepoRAG clones the target repository.  
2. **Chunk & Embed** – Splits code & docs into logical chunks, converts them into vector embeddings using ChromaDB.  
3. **Retrieve & Answer** – Retrieves the most relevant chunks for your query and passes them as context to a Large Language Model (e.g., GPT-4o, Llama 3) to generate precise answers.  

---

## 🚀 Getting Started

### **Prerequisites**
- **Git**
- **Python 3.9+**

### **Installation & Setup**

```bash
# 1️⃣ Clone the repository
git clone https://github.com/your-username/RepoRAG.git
cd RepoRAG

# 2️⃣ Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ (Optional) Add API keys in a `.env` file
OPENAI_API_KEY="sk-..."
GROQ_API_KEY="gsk_..."
