
# Chatbot de WhatsApp con **Gemini** + **Google Drive**
Servidor **Flask** que integra:
- **WhatsApp Business Platform (Cloud API)** para recibir/enviar mensajes.
- **Google Generative AI (Gemini)** para IA conversacional y clasificación de intención.
- **Google Drive API** para **buscar** y **enviar** documentos solicitados por los usuarios.

> Usa **tu propio número** si lo registras/migras en **WhatsApp Business Platform**. No se usa Twilio.

---

## 🚧 ¿Qué puede hacer?
1) Chat general con Gemini (respuesta breve y útil).  
2) **Detección de intención de documento** (por ej. “mándame el contrato de alquiler”).  
3) Búsqueda en tu **carpeta de Google Drive** (por nombre/keywords) y envío del **documento por WhatsApp** (link/adjunto).  
4) **Cuestionario** opcional para captación de leads (editable).  
5) Registro básico de estados en SQLite.

---

## 🔐 Credenciales & Requisitos
- **OpenAI NO se usa**; aquí usamos **Gemini** (Google).  
- **Credenciales de Google**: recomendamos **Service Account** con acceso a la carpeta de Drive.
  - Crea una Service Account en Google Cloud, genera una clave JSON y descarga el archivo.
  - **Comparte** la carpeta de Drive (o unidad compartida) con el **correo** de la Service Account con permiso de lector (o editor si permitirás crear enlaces públicos).
- **Meta WhatsApp Cloud API**:
  - `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`.
  - Configura el **Webhook URL** y suscribe `messages`.

---

## 🧩 Variables (.env)
Copia `.env.example` a `.env` y edítalo:
```
# Gemini (Google AI Studio)
GEMINI_API_KEY=AIza...

# Google Drive API (Service Account)
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/mi-service-account.json
DRIVE_FOLDER_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# WhatsApp Cloud API
WHATSAPP_ACCESS_TOKEN=EAAG...
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=mi-token-verificacion

# App
BUSINESS_NAME="Tu Empresa"
DATABASE_URL=sqlite:///data/bot.db
HOST=0.0.0.0
PORT=5000
DEBUG=true
```

> **Nota:** Si tu organización limita enlaces públicos, puedes optar por **enviar solo el link de `webViewLink`** (requiere login) o crear un proxy de descarga autenticado. Por simplicidad, el ejemplo puede crear permiso `anyoneReader` temporal y enviará `webViewLink`/`webContentLink` cuando esté disponible.

---

## ▶️ Instalación y ejecución
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edita .env con tus claves reales

python app.py
```
Para exponerlo públicamente en pruebas:  
```bash
ngrok http 5000
```
Configura en el dashboard de Meta el **Webhook URL** `https://<tu-ngrok>/whatsapp/webhook` y el **verify token**.

---

## 📁 Estructura
```
whatsapp_gemini_drive_bot/
├─ app.py
├─ gemini_handler.py
├─ drive_client.py
├─ meta_whatsapp.py
├─ questionnaire.py
├─ state_store.py
├─ requirements.txt
├─ .env.example
├─ README.md
└─ tests/sample_inbound.json
```

---

## 🧠 ¿Cómo detecta solicitudes de documentos?
`gemini_handler.classify_intent()` recibe el texto y devuelve JSON:
```json
{ "intent": "doc_request" | "chat", "keywords": ["contrato", "alquiler"] }
```
Si `doc_request`, se buscan archivos en Drive dentro de `DRIVE_FOLDER_ID` usando los keywords.

---

## 📤 Envío por WhatsApp
- **Texto**: `meta_whatsapp.send_text(...)`
- **Documento por link**: `meta_whatsapp.send_document_url(..., link, filename)`

Puedes extender a **plantillas**, **botones**, **imágenes**, etc.

---

## ⚠️ Seguridad
- No expongas tu Service Account JSON públicamente.
- Considera remover los permisos `anyoneReader` creados tras el envío (puedes programarlo).
- Limita el tamaño/Tipo de archivo si es necesario.
