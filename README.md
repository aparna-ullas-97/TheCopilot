# TheCopilot  
**An agent more than a chatbot**

TheCopilot is a modular, RAG-based AI assistant that combines:
- Retrieval-Augmented Generation (RAG)
- Pluggable LLM providers (Gemini / LLaMA)
- Document ingestion (PDF, DOCX, TXT)
- Conversation tracking
- Analytics layer from live blockchain dashboard

---

## Architecture

API → Orchestrator → LLM Provider → Response  
                ↘ Retrieval (Vector DB)  
                ↘ Analytics (optional)

---

## Setup

### 1. Clone the repo
git clone <https://github.com/aparna-ullas-97/TheCopilot.git>  
cd TheCopilot  

### 2. Create virtual environment
python -m venv venv  
source venv/bin/activate  

### 3. Install dependencies
pip install -r requirements.txt  

---

## Environment Configuration

### Gemini
LLM_PROVIDER=gemini  
GEMINI_API_KEY=your_api_key  
GEMINI_MODEL=gemini-2.5-flash  

### LLaMA (Ollama)
LLM_PROVIDER=llama  
LLAMA_MODEL=llama3  
LLAMA_BASE_URL=http://localhost:11434  

---

## Run

```python -m uvicorn apps.api.app.main:app --reload```

---

## Switching Models

Change LLM_PROVIDER in .env

---

## License

MIT
