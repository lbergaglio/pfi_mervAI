
# mervAI - Proyecto Backend sin Docker

## Instrucciones para correr localmente

### Backend Express (Node.js)
1. Entrar a la carpeta `backend`
2. Instalar dependencias: `npm install`
3. Ejecutar: `npm start`
4. API escuchando en http://localhost:3000

### Microservicio Python (Flask)
1. Entrar a la carpeta `python-modules`
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `python app.py`
4. API escuchando en http://localhost:5000

### Probar scraping y análisis de sentimiento
- Enviar POST a `http://localhost:3000/api/sentiment/reddit` con JSON:
```json
{
  "query": "MERVAL",
  "subreddit": "argentina"
}
```
- Recibirás un JSON con títulos de posts y sentimiento analizado.

### Configuración
- Configurar credenciales Reddit en `python-modules/app.py` en el objeto `reddit`.

