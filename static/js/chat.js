// Variables globales
let currentConversationId = null;
let isLoading = false;
let modelosDisponibles = [];
let modeloActual = null;
let pdfCargado = false;

// Esperar a que cargue la página
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Chat.js cargado correctamente');
    
    cargarModelos();
    cargarConversaciones();
    cargarUltimaConversacion();
    
    // Event listeners
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const modelSelect = document.getElementById('modelSelect');
    const messageInput = document.getElementById('messageInput');
    const attachBtn = document.getElementById('attachBtn');
    const pdfUpload = document.getElementById('pdfUpload');
    
    if (sendBtn) sendBtn.addEventListener('click', enviarMensaje);
    if (newChatBtn) newChatBtn.addEventListener('click', crearNuevaConversacion);
    if (clearAllBtn) clearAllBtn.addEventListener('click', limpiarTodasConversaciones);
    if (modelSelect) modelSelect.addEventListener('change', cambiarModelo);
    
    if (attachBtn && pdfUpload) {
        attachBtn.addEventListener('click', () => pdfUpload.click());
        pdfUpload.addEventListener('change', subirPDF);
    }
    
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                enviarMensaje();
            }
        });
        
        messageInput.addEventListener('input', function() {
            ajustarAlturaTextarea();
        });
        
        messageInput.addEventListener('keyup', function() {
            if (this.value === '') {
                resetearAlturaTextarea();
            }
        });
        
        messageInput.addEventListener('paste', function() {
            setTimeout(() => {
                ajustarAlturaTextarea();
            }, 10);
        });
        
        ajustarAlturaTextarea();
    }
});

// Función para ajustar la altura del textarea
function ajustarAlturaTextarea() {
    const textarea = document.getElementById('messageInput');
    if (!textarea) return;
    
    const scrollPos = textarea.scrollTop;
    textarea.style.height = 'auto';
    
    const scrollHeight = textarea.scrollHeight;
    const minHeight = 52;
    const maxHeight = 200;
    
    let newHeight = scrollHeight;
    
    if (scrollHeight < minHeight) {
        newHeight = minHeight;
        textarea.classList.remove('scroll-visible');
    } else if (scrollHeight > maxHeight) {
        newHeight = maxHeight;
        textarea.classList.add('scroll-visible');
        setTimeout(() => {
            textarea.scrollTop = scrollPos;
        }, 0);
    } else {
        newHeight = scrollHeight;
        textarea.classList.remove('scroll-visible');
    }
    
    textarea.style.height = newHeight + 'px';
}

function resetearAlturaTextarea() {
    const textarea = document.getElementById('messageInput');
    if (!textarea) return;
    
    textarea.style.height = '52px';
    textarea.classList.remove('scroll-visible');
    textarea.style.overflowY = 'hidden';
}

async function subirPDF(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    if (!currentConversationId) {
        mostrarStatusPDF('❌ Primero crea o selecciona una conversación', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('conversacion_id', currentConversationId);
    
    mostrarStatusPDF('📤 Subiendo y procesando PDF...', 'info');
    
    try {
        const response = await fetch('/api/upload-pdf', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            pdfCargado = true;
            mostrarStatusPDF(`✅ ${data.message}`, 'success');
            agregarMensajeTemporal(`📄 PDF "${file.name}" cargado correctamente. ¡Ahora puedes hacer preguntas sobre su contenido!`);
            
            const chatTitle = document.getElementById('chatTitle');
            if (chatTitle && !chatTitle.innerHTML.includes('📄')) {
                chatTitle.innerHTML = `${chatTitle.textContent} 📄`;
            }
        } else {
            mostrarStatusPDF(`❌ ${data.error}`, 'error');
        }
    } catch (error) {
        mostrarStatusPDF(`❌ Error de conexión: ${error.message}`, 'error');
    }
    
    setTimeout(() => {
        const statusDiv = document.getElementById('pdfStatus');
        if (statusDiv) statusDiv.innerHTML = '';
    }, 5000);
    
    e.target.value = '';
}

function mostrarStatusPDF(mensaje, tipo) {
    const statusDiv = document.getElementById('pdfStatus');
    if (statusDiv) {
        statusDiv.innerHTML = mensaje;
        statusDiv.className = `pdf-status ${tipo}`;
    }
}

async function cargarModelos() {
    try {
        const response = await fetch('/api/modelos');
        const data = await response.json();
        
        modelosDisponibles = data.modelos || [];
        modeloActual = data.modelo_actual;
        
        const select = document.getElementById('modelSelect');
        const badge = document.getElementById('currentModelBadge');
        const statusText = document.getElementById('statusText');
        
        if (!select) return;
        
        if (modelosDisponibles.length === 0) {
            select.innerHTML = '<option value="">No hay modelos instalados</option>';
            if (statusText) statusText.textContent = '❌ Sin modelos';
            return;
        }
        
        const modelosChat = modelosDisponibles.filter(m => !m.includes('embed'));
        
        select.innerHTML = modelosChat.map(modelo => 
            `<option value="${modelo}" ${modelo === modeloActual ? 'selected' : ''}>
                ${modelo}
            </option>`
        ).join('');
        
        if (badge) badge.innerHTML = `🧠 ${modeloActual}`;
        if (statusText) statusText.textContent = '✅ Modelo listo';
        
        console.log('Modelos disponibles para chat:', modelosChat);
        
    } catch (error) {
        console.error('Error cargando modelos:', error);
        const statusText = document.getElementById('statusText');
        if (statusText) statusText.textContent = '❌ Error de conexión';
    }
}

async function cambiarModelo() {
    const select = document.getElementById('modelSelect');
    if (!select) return;
    
    const nuevoModelo = select.value;
    if (!nuevoModelo) return;
    
    try {
        const response = await fetch('/api/modelos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ modelo: nuevoModelo })
        });
        
        const data = await response.json();
        
        if (data.success) {
            modeloActual = nuevoModelo;
            const badge = document.getElementById('currentModelBadge');
            if (badge) badge.innerHTML = `🧠 ${modeloActual}`;
            agregarMensajeTemporal(`✅ Modelo cambiado a: ${modeloActual}`);
        }
        
    } catch (error) {
        console.error('Error cambiando modelo:', error);
        agregarMensajeTemporal('❌ Error al cambiar el modelo');
    }
}

async function cargarUltimaConversacion() {
    try {
        const response = await fetch('/api/conversaciones');
        const conversaciones = await response.json();
        
        if (conversaciones && conversaciones.length > 0) {
            const ultimaConv = conversaciones[0];
            await cargarConversacion(ultimaConv.id);
        } else {
            await crearNuevaConversacion();
        }
    } catch (error) {
        console.error('Error cargando última conversación:', error);
        await crearNuevaConversacion();
    }
}

async function cargarConversaciones() {
    try {
        const response = await fetch('/api/conversaciones');
        const conversaciones = await response.json();
        const lista = document.getElementById('conversationsList');
        
        if (!lista) return;
        
        if (!conversaciones || conversaciones.length === 0) {
            lista.innerHTML = '<div style="color: #888; padding: 20px; text-align: center;">Sin conversaciones</div>';
            return;
        }
        
        lista.innerHTML = conversaciones.map(conv => `
            <div class="conversation-item ${currentConversationId === conv.id ? 'active' : ''}" data-conv-id="${conv.id}">
                <div class="conversation-title">${escapeHtml(conv.titulo)}</div>
                <div class="conversation-preview">${escapeHtml(conv.primer_mensaje || 'Nueva conversación')}</div>
                <button class="delete-conv-btn" data-conv-id="${conv.id}">🗑️</button>
            </div>
        `).join('');
        
        document.querySelectorAll('.conversation-item').forEach(item => {
            const convId = item.getAttribute('data-conv-id');
            item.addEventListener('click', (e) => {
                if (!e.target.classList.contains('delete-conv-btn')) {
                    cargarConversacion(convId);
                }
            });
        });
        
        document.querySelectorAll('.delete-conv-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const convId = btn.getAttribute('data-conv-id');
                eliminarConversacion(convId);
            });
        });
        
    } catch (error) {
        console.error('Error cargando conversaciones:', error);
    }
}

async function crearNuevaConversacion() {
    try {
        const response = await fetch('/api/conversaciones', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ titulo: 'Nueva conversación' })
        });
        const data = await response.json();
        currentConversationId = data.id;
        pdfCargado = false;
        
        const chatTitle = document.getElementById('chatTitle');
        if (chatTitle) chatTitle.textContent = 'DeepSeek';
        
        const container = document.getElementById('messagesContainer');
        if (container) {
            container.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">✨</div>
                    <h2>¿En qué puedo ayudarte?</h2>
                    <p>Tu asistente de IA completamente local y privado</p>
                    <p style="font-size: 14px; margin-top: 16px;">
                        💡 Powered by Ollama & DeepSeek
                    </p>
                </div>
            `;
        }
        
        await cargarConversaciones();
        
        const messageInput = document.getElementById('messageInput');
        if (messageInput) messageInput.focus();
        resetearAlturaTextarea();
        
    } catch (error) {
        console.error('Error creando conversación:', error);
    }
}

async function cargarConversacion(id) {
    if (isLoading) return;
    
    try {
        const response = await fetch(`/api/conversaciones/${id}`);
        if (!response.ok) throw new Error('Error al cargar la conversación');
        
        const conv = await response.json();
        currentConversationId = conv.id;
        
        const chatTitle = document.getElementById('chatTitle');
        if (chatTitle) {
            let titulo = conv.titulo;
            if (conv.documentos && conv.documentos.length > 0) {
                titulo += ' 📄';
                pdfCargado = true;
            } else {
                pdfCargado = false;
            }
            chatTitle.textContent = titulo;
        }
        
        const container = document.getElementById('messagesContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (conv.mensajes && conv.mensajes.length > 0) {
            conv.mensajes.forEach(msg => {
                const modelo = msg.modelo || null;
                agregarMensajeUI(msg.role, msg.content, modelo);
            });
        } else {
            container.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-icon">✨</div>
                    <h2>¿En qué puedo ayudarte?</h2>
                    <p>Tu asistente de IA completamente local y privado</p>
                </div>
            `;
        }
        
        await cargarConversaciones();
        container.scrollTop = container.scrollHeight;
        
    } catch (error) {
        console.error('Error cargando conversación:', error);
    }
}

async function eliminarConversacion(id) {
    if (!confirm('¿Eliminar esta conversación?')) return;
    
    try {
        await fetch(`/api/conversaciones/${id}`, { method: 'DELETE' });
        
        const response = await fetch('/api/conversaciones');
        const conversaciones = await response.json();
        
        if (conversaciones && conversaciones.length > 0) {
            await cargarConversacion(conversaciones[0].id);
        } else {
            await crearNuevaConversacion();
        }
        
        await cargarConversaciones();
        
    } catch (error) {
        console.error('Error eliminando conversación:', error);
    }
}

async function limpiarTodasConversaciones() {
    if (!confirm('⚠️ ¿Eliminar TODAS las conversaciones?')) return;
    
    try {
        const response = await fetch('/api/conversaciones');
        const conversaciones = await response.json();
        
        if (conversaciones) {
            for (const conv of conversaciones) {
                await fetch(`/api/conversaciones/${conv.id}`, { method: 'DELETE' });
            }
        }
        
        await crearNuevaConversacion();
        await cargarConversaciones();
        
    } catch (error) {
        console.error('Error limpiando conversaciones:', error);
    }
}

async function enviarMensaje() {
    const input = document.getElementById('messageInput');
    if (!input) return;
    
    const mensaje = input.value.trim();
    if (!mensaje || isLoading) return;
    
    resetearAlturaTextarea();
    input.value = '';
    
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    agregarMensajeUI('user', mensaje, null);
    
    const loadingId = mostrarLoading();
    isLoading = true;
    
    const sendBtn = document.getElementById('sendBtn');
    if (sendBtn) sendBtn.disabled = true;
    
    try {
        const historial = [];
        const mensajesElements = document.querySelectorAll('.message');
        
        mensajesElements.forEach(msgElement => {
            try {
                const role = msgElement.classList.contains('user') ? 'user' : 'assistant';
                const bubble = msgElement.querySelector('.message-bubble');
                if (bubble && bubble.innerText) {
                    const content = bubble.innerText;
                    if (content && !content.includes('pensando')) {
                        historial.push({ role, content });
                    }
                }
            } catch (e) {
                console.warn('Error al procesar mensaje:', e);
            }
        });
        
        const usarPDF = pdfCargado;
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mensaje: mensaje,
                conversacion_id: currentConversationId,
                historial: historial.slice(-10),
                modelo: modeloActual,
                usar_pdf: usarPDF
            })
        });
        
        const data = await response.json();
        ocultarLoading(loadingId);
        
        if (data.error) {
            agregarMensajeUI('assistant', `❌ ${data.error}`, null);
        } else {
            let respuestaConInfo = data.respuesta;
            if (data.usando_pdf) {
                respuestaConInfo += `\n\n📄 *Respuesta basada en el documento cargado*`;
            }
            agregarMensajeUI('assistant', respuestaConInfo, data.modelo_usado);
            
            if (data.conversacion_id && data.conversacion_id !== currentConversationId) {
                currentConversationId = data.conversacion_id;
                await cargarConversaciones();
            }
        }
        
        await cargarConversaciones();
        
    } catch (error) {
        console.error('Error:', error);
        ocultarLoading(loadingId);
        agregarMensajeUI('assistant', `❌ Error de conexión: ${error.message}`, null);
    } finally {
        isLoading = false;
        if (sendBtn) sendBtn.disabled = false;
        input.focus();
    }
}

function agregarMensajeUI(role, content, modelo = null) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    let formattedContent = formatMessage(content);
    
    if (role === 'assistant' && modelo) {
        formattedContent += `<div style="font-size: 11px; color: #888; margin-top: 8px; padding-top: 8px; border-top: 1px solid #e5e7eb;">
            🤖 Modelo: ${modelo}
        </div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
        <div class="message-content">
            <div class="message-bubble">${formattedContent}</div>
        </div>
    `;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function agregarMensajeTemporal(mensaje) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;
    
    const tempDiv = document.createElement('div');
    tempDiv.className = 'message assistant';
    tempDiv.style.opacity = '0.7';
    tempDiv.innerHTML = `
        <div class="message-avatar">ℹ️</div>
        <div class="message-content">
            <div class="message-bubble">${escapeHtml(mensaje)}</div>
        </div>
    `;
    container.appendChild(tempDiv);
    container.scrollTop = container.scrollHeight;
    
    setTimeout(() => {
        if (tempDiv && tempDiv.remove) tempDiv.remove();
    }, 3000);
}

function mostrarLoading() {
    const id = 'loading_' + Date.now();
    const container = document.getElementById('messagesContainer');
    if (!container) return id;
    
    const loadingDiv = document.createElement('div');
    loadingDiv.id = id;
    loadingDiv.className = 'message bot';
    loadingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;
    return id;
}

function ocultarLoading(id) {
    const el = document.getElementById(id);
    if (el && el.remove) el.remove();
}

function formatMessage(text) {
    if (!text) return '';
    let formatted = escapeHtml(text);
    formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
    formatted = formatted.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>');
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}