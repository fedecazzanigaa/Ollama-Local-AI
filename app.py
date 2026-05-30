from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

# Importaciones para PDF
import PyPDF2
import chromadb
from chromadb.config import Settings

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app)

# Configuración
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_EMBEDDINGS_API = "http://localhost:11434/api/embeddings"
OLLAMA_API_TAGS = "http://localhost:11434/api/tags"
MODELO_POR_DEFECTO = "deepseek-coder:6.7b"
MODELO_EMBEDDINGS = "nomic-embed-text:latest"  # Modelo para embeddings en Ollama
CONVERSATIONS_DIR = "conversations"
UPLOAD_FOLDER = "uploads"
VECTOR_STORES_DIR = "vector_stores"

# Crear directorios
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_STORES_DIR, exist_ok=True)

modelo_actual = MODELO_POR_DEFECTO

# Inicializar ChromaDB
chroma_client = chromadb.PersistentClient(path=VECTOR_STORES_DIR)

def obtener_embedding(texto):
    """Obtiene embedding usando Ollama"""
    try:
        response = requests.post(
            OLLAMA_EMBEDDINGS_API,
            json={"model": MODELO_EMBEDDINGS, "prompt": texto},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("embedding")
        return None
    except Exception as e:
        print(f"Error obteniendo embedding: {e}")
        return None

def obtener_modelos_disponibles():
    try:
        response = requests.get(OLLAMA_API_TAGS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            modelos = [modelo['name'] for modelo in data.get('models', [])]
            return modelos
        return []
    except:
        return []

def guardar_conversacion(conversacion_id, titulo, mensajes, modelo=None, documentos=None):
    archivo = os.path.join(CONVERSATIONS_DIR, f"{conversacion_id}.json")
    datos = {
        "id": conversacion_id,
        "titulo": titulo,
        "fecha_creacion": datetime.now().isoformat(),
        "ultima_modificacion": datetime.now().isoformat(),
        "mensajes": mensajes,
        "modelo": modelo or modelo_actual,
        "documentos": documentos or []
    }
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def cargar_conversacion(conversacion_id):
    archivo = os.path.join(CONVERSATIONS_DIR, f"{conversacion_id}.json")
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def listar_conversaciones():
    conversaciones = []
    for archivo in os.listdir(CONVERSATIONS_DIR):
        if archivo.endswith('.json'):
            with open(os.path.join(CONVERSATIONS_DIR, archivo), 'r', encoding='utf-8') as f:
                data = json.load(f)
                conversaciones.append({
                    "id": data["id"],
                    "titulo": data["titulo"],
                    "ultima_modificacion": data["ultima_modificacion"],
                    "primer_mensaje": data["mensajes"][0]["content"][:50] if data["mensajes"] else ""
                })
    conversaciones.sort(key=lambda x: x["ultima_modificacion"], reverse=True)
    return conversaciones

def extraer_texto_pdf(file_path):
    """Extrae texto de un PDF usando PyPDF2"""
    texto_completo = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                texto = page.extract_text()
                if texto:
                    texto_completo += texto + "\n"
        return texto_completo
    except Exception as e:
        print(f"Error extrayendo texto del PDF: {e}")
        return None

def dividir_texto(texto, chunk_size=500):
    """Divide el texto en fragmentos más pequeños"""
    # Dividir por párrafos
    parrafos = texto.split('\n\n')
    chunks = []
    
    for parrafo in parrafos:
        parrafo = parrafo.strip()
        if not parrafo:
            continue
        
        # Si el párrafo es muy largo, dividirlo por oraciones
        if len(parrafo) > chunk_size:
            oraciones = parrafo.replace('!', '.').replace('?', '.').split('.')
            chunk_actual = ""
            for oracion in oraciones:
                if len(chunk_actual) + len(oracion) < chunk_size:
                    chunk_actual += oracion + "."
                else:
                    if chunk_actual:
                        chunks.append(chunk_actual.strip())
                    chunk_actual = oracion + "."
            if chunk_actual:
                chunks.append(chunk_actual.strip())
        else:
            chunks.append(parrafo)
    
    return chunks

def procesar_pdf(file_path, conversacion_id):
    """Procesa un PDF y crea una colección en ChromaDB"""
    try:
        # Extraer texto del PDF
        texto = extraer_texto_pdf(file_path)
        if not texto:
            return False, "No se pudo extraer texto del PDF. ¿El PDF tiene texto (no es una imagen escaneada)?"
        
        # Dividir en fragmentos
        chunks = dividir_texto(texto)
        
        if not chunks:
            return False, "No se pudieron crear fragmentos del texto"
        
        # Crear o obtener colección en ChromaDB
        try:
            # Intentar eliminar colección existente
            try:
                chroma_client.delete_collection(conversacion_id)
            except:
                pass
            
            # Crear nueva colección
            collection = chroma_client.create_collection(
                name=conversacion_id,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error creando colección: {e}")
            collection = chroma_client.get_or_create_collection(conversacion_id)
        
        # Procesar cada fragmento
        ids = []
        embeddings = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            # Obtener embedding usando Ollama
            embedding = obtener_embedding(chunk)
            if embedding:
                embeddings.append(embedding)
                chunk_id = f"{conversacion_id}_{i}"
                ids.append(chunk_id)
                documents.append(chunk)
        
        # Agregar a la colección
        if embeddings and ids and documents:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents
            )
            return True, f"PDF procesado correctamente. {len(chunks)} fragmentos creados."
        else:
            return False, "No se pudieron generar embeddings para el texto"
        
    except Exception as e:
        return False, str(e)

def consultar_pdf(conversacion_id, pregunta):
    """Consulta el PDF y obtiene contexto relevante"""
    try:
        # Obtener la colección
        try:
            collection = chroma_client.get_collection(conversacion_id)
        except:
            return None, "No hay documentos cargados en esta conversación"
        
        # Generar embedding de la pregunta
        query_embedding = obtener_embedding(pregunta)
        if not query_embedding:
            return None, "No se pudo generar embedding para la pregunta"
        
        # Buscar documentos similares
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        if not results['documents'] or not results['documents'][0]:
            return None, "No se encontró información relevante en los documentos"
        
        # Construir contexto
        contexto = "Contexto de los documentos:\n\n"
        for i, doc in enumerate(results['documents'][0]):
            contexto += f"[Fragmento {i+1}]: {doc[:500]}\n\n"
        
        return contexto, None
        
    except Exception as e:
        print(f"Error consultando PDF: {e}")
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/modelos', methods=['GET'])
def get_modelos():
    modelos = obtener_modelos_disponibles()
    return jsonify({
        "modelos": modelos,
        "modelo_actual": modelo_actual
    })

@app.route('/api/modelos', methods=['POST'])
def set_modelo():
    global modelo_actual
    data = request.json
    nuevo_modelo = data.get('modelo')
    
    modelos_disponibles = obtener_modelos_disponibles()
    if nuevo_modelo in modelos_disponibles:
        modelo_actual = nuevo_modelo
        return jsonify({"success": True, "modelo": modelo_actual})
    else:
        return jsonify({"error": "Modelo no disponible"}), 400

@app.route('/api/conversaciones', methods=['GET'])
def obtener_conversaciones():
    return jsonify(listar_conversaciones())

@app.route('/api/conversaciones', methods=['POST'])
def crear_conversacion():
    conversacion_id = str(uuid.uuid4())
    titulo = request.json.get('titulo', 'Nueva conversación')
    guardar_conversacion(conversacion_id, titulo, [])
    return jsonify({"id": conversacion_id, "titulo": titulo})

@app.route('/api/conversaciones/<conversacion_id>', methods=['GET'])
def obtener_conversacion(conversacion_id):
    conversacion = cargar_conversacion(conversacion_id)
    if conversacion:
        return jsonify(conversacion)
    return jsonify({"error": "No encontrada"}), 404

@app.route('/api/conversaciones/<conversacion_id>', methods=['DELETE'])
def eliminar_conversacion(conversacion_id):
    archivo = os.path.join(CONVERSATIONS_DIR, f"{conversacion_id}.json")
    if os.path.exists(archivo):
        os.remove(archivo)
        try:
            chroma_client.delete_collection(conversacion_id)
        except:
            pass
        return jsonify({"success": True})
    return jsonify({"error": "No encontrada"}), 404

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    
    file = request.files['file']
    conversacion_id = request.form.get('conversacion_id')
    
    if not conversacion_id:
        return jsonify({"error": "ID de conversación no proporcionado"}), 400
    
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Solo se permiten archivos PDF"}), 400
    
    # Guardar archivo
    filename = secure_filename(f"{conversacion_id}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Procesar PDF
    success, message = procesar_pdf(filepath, conversacion_id)
    
    if success:
        conversacion = cargar_conversacion(conversacion_id)
        if conversacion:
            documentos = conversacion.get('documentos', [])
            documentos.append({
                "nombre": file.filename,
                "ruta": filename,
                "fecha": datetime.now().isoformat()
            })
            guardar_conversacion(conversacion_id, conversacion['titulo'], conversacion['mensajes'], None, documentos)
        
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"error": message}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        mensaje = data.get('mensaje', '')
        conversacion_id = data.get('conversacion_id')
        historial = data.get('historial', [])
        usar_pdf = data.get('usar_pdf', True)
        
        contexto_pdf = None
        if usar_pdf and conversacion_id:
            contexto_pdf, error = consultar_pdf(conversacion_id, mensaje)
        
        if contexto_pdf:
            prompt_completo = f"""{contexto_pdf}

Pregunta del usuario: {mensaje}

Instrucción: Responde basándote ÚNICAMENTE en el contexto proporcionado. Si la respuesta no está en el contexto, di "No encontré información sobre esto en los documentos cargados."

Respuesta:"""
        else:
            prompt_completo = ""
            for msg in historial[-10:]:
                if msg["role"] == "user":
                    prompt_completo += f"Usuario: {msg['content']}\n"
                else:
                    prompt_completo += f"Asistente: {msg['content']}\n"
            prompt_completo += f"Usuario: {mensaje}\nAsistente:"
        
        payload = {
            "model": modelo_actual,
            "prompt": prompt_completo,
            "stream": False,
            "options": {"temperature": 0.7}
        }
        
        response = requests.post(OLLAMA_API, json=payload, timeout=120)
        
        if response.status_code == 200:
            respuesta = response.json().get("response", "Sin respuesta")
            
            if conversacion_id:
                conversacion = cargar_conversacion(conversacion_id)
                if conversacion:
                    conversacion["mensajes"].append({"role": "user", "content": mensaje})
                    conversacion["mensajes"].append({
                        "role": "assistant", 
                        "content": respuesta,
                        "modelo": modelo_actual,
                        "usando_pdf": contexto_pdf is not None
                    })
                    if len(conversacion["mensajes"]) == 2:
                        conversacion["titulo"] = mensaje[:30] + "..." if len(mensaje) > 30 else mensaje
                    conversacion["ultima_modificacion"] = datetime.now().isoformat()
                    guardar_conversacion(conversacion_id, conversacion["titulo"], conversacion["mensajes"], modelo_actual)
            
            return jsonify({
                "respuesta": respuesta, 
                "conversacion_id": conversacion_id,
                "modelo_usado": modelo_actual,
                "usando_pdf": contexto_pdf is not None
            })
        else:
            return jsonify({"error": f"Error Ollama: {response.status_code}"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Servidor DeepSeek Local con soporte PDF")
    print("📡 Accede en: http://localhost:8000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=8000)