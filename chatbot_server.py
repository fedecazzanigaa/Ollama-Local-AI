#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configuración
MODELO = "deepseek-coder:6.7b"  # Cambia por el modelo que tengas
PUERTO = 8000
OLLAMA_API = "http://localhost:11434/api/generate"  # API de Ollama

class ChatbotHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Maneja peticiones GET - interfaz web simple"""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            # Página HTML sencilla para el chat
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Chatbot Local con DeepSeek</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; }
                    #chat { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; background: #f9f9f9; }
                    .user { color: blue; margin: 5px 0; }
                    .bot { color: green; margin: 5px 0; }
                    #input-area { display: flex; }
                    #message { flex: 1; padding: 10px; }
                    button { padding: 10px; }
                    .loading { color: gray; font-style: italic; }
                </style>
            </head>
            <body>
                <h1>Chatbot Local con DeepSeek (via Ollama API)</h1>
                <div id="chat"></div>
                <div id="input-area">
                    <input type="text" id="message" placeholder="Escribe tu mensaje...">
                    <button onclick="enviar()">Enviar</button>
                </div>
                <script>
                    function enviar() {
                        let input = document.getElementById('message');
                        let msg = input.value.trim();
                        if (!msg) return;
                        
                        // Mostrar mensaje del usuario
                        let chat = document.getElementById('chat');
                        chat.innerHTML += '<div class="user"><strong>Tú:</strong> ' + escapeHtml(msg) + '</div>';
                        input.value = '';
                        
                        // Mostrar indicador de carga
                        let loadingId = 'loading_' + Date.now();
                        chat.innerHTML += '<div id="' + loadingId + '" class="loading"><strong>Bot:</strong> ...pensando...</div>';
                        chat.scrollTop = chat.scrollHeight;
                        
                        // Llamar al API
                        fetch('/api/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ prompt: msg })
                        })
                        .then(res => res.json())
                        .then(data => {
                            // Eliminar indicador de carga
                            document.getElementById(loadingId).remove();
                            // Mostrar respuesta
                            chat.innerHTML += '<div class="bot"><strong>Bot:</strong> ' + escapeHtml(data.response) + '</div>';
                            chat.scrollTop = chat.scrollHeight;
                        })
                        .catch(err => {
                            document.getElementById(loadingId).remove();
                            chat.innerHTML += '<div class="bot"><strong>Error:</strong> ' + err + '</div>';
                        });
                    }
                    
                    function escapeHtml(text) {
                        return text.replace(/[&<>]/g, function(m) {
                            if (m === '&') return '&amp;';
                            if (m === '<') return '&lt;';
                            if (m === '>') return '&gt;';
                            return m;
                        }).replace(/\\n/g, '<br>');
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Maneja peticiones POST - API del chatbot"""
        if self.path == "/api/chat":
            # Leer el cuerpo de la petición
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                prompt = data.get('prompt', '')
                
                if not prompt:
                    self._send_json(400, {"error": "Falta el prompt"})
                    return
                
                print(f"Procesando prompt: {prompt}")
                
                # Llamar a Ollama usando su API
                respuesta = self._llamar_ollama_api(prompt)
                
                print(f"Respuesta obtenida: {respuesta[:100]}...")
                self._send_json(200, {"response": respuesta})
            except Exception as e:
                print(f"Error: {str(e)}")
                self._send_json(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()
    
    def _llamar_ollama_api(self, prompt):
        """Usa la API REST de Ollama para generar respuesta"""
        try:
            payload = {
                "model": MODELO,
                "prompt": prompt,
                "stream": False  # Para obtener respuesta completa
            }
            
            response = requests.post(OLLAMA_API, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No se obtuvo respuesta")
            else:
                return f"Error en Ollama API: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "El modelo tardó demasiado en responder (más de 120 segundos)."
        except requests.exceptions.ConnectionError:
            return "No se pudo conectar a Ollama. ¿Está ejecutándose? (Ejecuta 'ollama serve' en otra terminal)"
        except Exception as e:
            return f"Error al llamar a Ollama: {str(e)}"
    
    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

def run_server(port=PUERTO):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChatbotHandler)
    print(f"✅ Servidor corriendo en http://localhost:{port}")
    print(f"📡 Usando modelo: {MODELO}")
    print(f"🔗 Conectando a Ollama en: {OLLAMA_API}")
    print("Presiona Ctrl+C para detener")
    httpd.serve_forever()

if __name__ == "__main__":
    # Verificar que requests esté instalado
    try:
        import requests
    except ImportError:
        print("❌ Falta la librería 'requests'. Instálala con:")
        print("   pip install requests")
        exit(1)
    
    run_server()