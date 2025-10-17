Chatbot Empresarial con IA (WhatsApp Cloud API + Flask)

Cómo correr localmente:
1) Crear entorno e instalar dependencias:  pip install -r requirements.txt
2) Definir variables de entorno (required):
   - VERIFY_TOKEN
   - META_ACCESS_TOKEN
   - PHONE_NUMBER_ID
   - GEMINI_API_KEY           (opcional si no usarás Gemini)
   - BUSINESS_NAME            (opcional, branding)
   - HOST, PORT, DEBUG        (opcional)
3) Ejecutar:  python app.py
4) Expone el webhook público con ngrok o Render y configura en Meta la URL:
   - Callback URL: https://TU_HOST/whatsapp/webhook
   - Verify Token: (igual a VERIFY_TOKEN)

Notas de compatibilidad:
- Se respeta el set de variables mostrado por el usuario.
- Unificación del uso de META_ACCESS_TOKEN en todo el proyecto.
- Gemini usa "gemini-1.5-flash" con google-generativeai 0.8.x.
