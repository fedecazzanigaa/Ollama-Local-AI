# 🚀 DeepSeek Local Clone - Chatbot IA con soporte PDF

![DeepSeek Local](https://img.shields.io/badge/DeepSeek-Local-blue)
![Ollama](https://img.shields.io/badge/Ollama-Supported-green)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![License](https://img.shields.io/badge/License-MIT-red)

A local chatbot with a DeepSeek-style interface that runs completely on your machine using Ollama. No internet required! Supports PDF uploads and multiple AI models.

## ✨ Features

- 🤖 **Local chat** with DeepSeek models (or any Ollama model)
- 📄 **PDF support** - Upload documents and ask questions about their content
- 💾 **Persistent history** - All conversations are saved automatically
- 🎨 **DeepSeek-style interface** - Modern, responsive and easy to use
- 🔄 **Multiple models** - Switch between different AI models in real time
- 🔒 **100% private** - Everything runs on your machine, zero external dependencies
- 📱 **Responsive** - Works on desktop, tablet and mobile

## 📋 Prerequisites

- **Python 3.10 or higher**
- **Ollama** installed on your system
- **AI models** downloaded in Ollama (ej: deepseek-coder, deepseek-r1, etc.)

## 🚀 step by step installation

### 1. Clone the repository

```bash
git clone https://github.com/tu-usuario/deepseek-local-chat.git
cd deepseek-local-chat

### 2. Create a virtual environment (recommended)

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Install & set up Ollama

# Windows
Download Ollama from ollama.com
Run the executable
Open a terminal and run: ollama serve

# Linux / Mac
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

### 5. Download local models

Ollama support many models:

# DeepSeek
ollama pull deepseek-coder
ollama pull deepseek-r1

# Llama3
ollama pull llama3

# Embedding model (necessary for PDFs)
ollama pull nomic-embed-text:latest

### 6. Set up environment variables

OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-coder:6.7b

### 7. Run the application

python app.py

### 8. Open the chatbot in your browser at http://localhost:8000
Ready!

### Project structure

deepseek-local-chat/
├── app.py                 # Main Flask server
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables (optional)
├── README.md             # This file
├── templates/
│   └── index.html        # User interface
├── static/
│   ├── css/
│   │   └── style.css     # Styles CSS
│   └── js/
│       └── chat.js       # Client logic
├── conversations/        # Stores the conversation history automatically
├── uploads/              # Temporary uploaded PDF files
└── vector_stores/        # Vector database for PDFs