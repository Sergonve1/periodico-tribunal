# Usa una imagen base oficial con Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia requirements y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la app
COPY . .

# Expone el puerto para FastAPI
EXPOSE 8000

# Comando por defecto: inicia FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

ENV PYTHONUNBUFFERED=1