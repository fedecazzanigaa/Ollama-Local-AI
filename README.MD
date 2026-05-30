# 🚀 Local AI Chatbot

> A local AI chatbot that runs entirely on your machine using Ollama. Chat with local LLMs, analyze PDFs, and keep your data private.

![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![Ollama](https://img.shields.io/badge/Ollama-Supported-green)
![License](https://img.shields.io/badge/License-MIT-red)

---

## 📸 Screenshots

> Add screenshots here

### Main Interface

```text
docs/images/main-chat.png
```

### PDF Analysis

```text
docs/images/pdf-analysis.png
```

---

## ✨ Features

| Feature | Supported |
|----------|----------|
| Local AI Chat | ✅ |
| PDF Analysis | ✅ |
| Conversation History | ✅ |
| Multiple Models | ✅ |
| Offline Operation | ✅ |
| Responsive UI | ✅ |
| Privacy Focused | ✅ |

---

## 🤔 Why This Project?

Many local AI chat applications are either:

- Difficult to install
- Resource-intensive
- Focused only on chat
- Missing document analysis capabilities

This project aims to provide:

- Simple installation
- PDF document analysis
- Persistent conversation history
- Complete privacy
- Support for multiple Ollama models
- A modern and responsive interface

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/deepseek-local-chat.git
cd deepseek-local-chat
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start Ollama

```bash
ollama serve
```

### 5. Download models

```bash
# DeepSeek
ollama pull deepseek-coder
ollama pull deepseek-r1

# Llama
ollama pull llama3

# Embeddings for PDF search
ollama pull nomic-embed-text:latest
```

### 6. Configure environment variables

```env
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-coder:6.7b
```

### 7. Run the application

```bash
python app.py
```

### 8. Open your browser

```text
http://localhost:8000
```

You're all set! 🎉

---

## 🏗️ Architecture

```text
User
 │
 ▼
Flask Application
 │
 ├── Ollama (LLM Inference)
 │
 ├── PDF Processing
 │
 ├── ChromaDB (Vector Store)
 │
 └── Conversation Storage
```

---

## 📂 Project Structure

```text
deepseek-local-chat/
├── app.py
├── requirements.txt
├── .env
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── chat.js
├── conversations/
├── uploads/
└── vector_stores/
```

---

## 📄 PDF Workflow

1. Click the 📎 attachment button.
2. Upload a PDF document.
3. Wait for processing to complete.
4. Ask questions about the document.
5. The system retrieves relevant content and generates answers using your local model.

---

## 🔧 Configuration

### Change the default model

```python
DEFAULT_MODEL = "deepseek-r1:14b"
```

### Change the application port

```python
app.run(debug=True, host="0.0.0.0", port=8080)
```

### Adjust generation parameters

```python
payload = {
    "model": current_model,
    "prompt": full_prompt,
    "stream": False,
    "options": {
        "temperature": 0.7,
        "max_tokens": 4000
    }
}
```

---

## 📦 Main Dependencies

| Package | Version | Purpose |
|----------|----------|----------|
| Flask | 2.3.3 | Web server |
| requests | 2.31.0 | Ollama communication |
| PyPDF2 | 3.0.0 | PDF text extraction |
| chromadb | 0.4.22 | Vector database |
| sentence-transformers | 2.2.2 | Semantic embeddings |

---

## 🛠️ Troubleshooting

### Module not found

```bash
pip install -r requirements.txt
```

### Ollama is not responding

```bash
ollama serve
```

### Unable to extract text from PDF

The PDF must contain selectable text. Scanned PDFs require OCR support.

### Model not appearing in the selector

```bash
ollama list
```

---

## 🌐 Remote Access (Tailscale)

1. Install Tailscale.
2. Log in on both devices.
3. On the server machine:

```bash
tailscale ip
```

4. Open:

```text
http://TAILSCALE_IP:8000
```

---

## 🗺️ Roadmap

- [x] Local chat
- [x] PDF support
- [x] Conversation history
- [x] Multiple models
- [ ] Streaming responses
- [ ] Docker deployment
- [ ] Voice input
- [ ] Dark / Light themes
- [ ] User authentication

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

GitHub: @fedecazzanigaa

---

⭐ If you found this project useful, consider giving it a star on GitHub!
