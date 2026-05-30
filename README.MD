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

🎯 How to use

Chat normally
Type your message in the text area

Press Enter or click the send button

The model will respond in real time

Use with PDFs
Click the 📎 (clip) icon next to the send button

Select a PDF file

Wait for it to process (you will see a confirmation message)

Ask questions about the PDF content

The system will automatically use the PDF to answer

Change model
In the left sidebar, expand the "AI Model" selector

Select the model you prefer

All new messages will use that model

Manage conversations
New chat: "New chat" button in the sidebar

Load chat: Click on any conversation in the history

Delete chat: Hover over a conversation and click on 🗑️

Clear all: "Clear history" button at the end of the sidebar

🛠️ Personalization
Change default model
Edit app.py:

python
MODELO_POR_DEFECTO = "deepseek-r1:14b"  # Change here
Change port
python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Change port
Modify token limit
In the chat() function of app.py:

python
payload = {
    "model": modelo_actual,
    "prompt": prompt_completo,
    "stream": False,
    "options": {
        "temperature": 0.7,
        "max_tokens": 4000  # Increase or decrease as needed
    }
}
📦 Main dependencies
Package	Version	Usage
Flask	2.3.3	Web server
requests	2.31.0	Communication with Ollama
PyPDF2	3.0.0	Text extraction from PDFs
chromadb	0.4.22	Vector database
sentence-transformers	2.2.2	Embeddings for semantic search
🔧 Common troubleshooting
❌ Error: "No module named 'xxx'"
bash
pip install -r requirements.txt
❌ Error: "Ollama no responde"
Make sure Ollama is running:

bash
ollama serve
❌ Error al subir PDF: "No se pudo extraer texto"
The PDF must have selectable text (not be a scanned image). For scanned PDFs, you will need to install OCR.

❌ The model does not appear in the selector
Check the installed models:

bash
ollama list
🌐 Acceso desde otra red (Tailscale)
Install Tailscale

Log in on both computers

On the server PC, run: tailscale ip

From the other PC: http://[TAILSCALE_IP]:8000

More options in the network documentation.

🤝 Contributions
Contributions are welcome. Please:

Fork the project

Create your branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push a la rama (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License
Distributed under the MIT license. See LICENSE for more information.

🙏 Acknowledgments
Ollama - For making it possible to run LLMs locally

DeepSeek - For their incredible open-source models

Flask - Lightweight and powerful web framework

📧 Contact
Federico Cazzaniga - @fedecazzanigaa


⭐ If you liked this project, don't forget to give it a star on GitHub!
