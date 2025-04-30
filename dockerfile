# Imagen base de Python
FROM python:3.12-slim

# Pueden ver mi pantalla?
# No estoy en clases solo que en el campus estan haciendo mucho ruido

# Bueno basicamente como no tenemos infraestructura, estoy utilizando dos servicios gratuitos con limites
# Para poder levantar la app
# El primer es el de SUPABASE, que va a tener la Base de Datos y el Storage de los documentos
# El segundo es el de RENDER 

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    poppler-utils \
    curl \
    libgl1 \
    libglib2.0-0 && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3000
CMD ["reflex", "run"]

##correr con docker run --env-file .env -p 3000:3000 prototipo-pruebas