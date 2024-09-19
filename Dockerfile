# Usar la imagen base de Selenium con Chrome
FROM python:3.11.1

# Establecer el directorio de trabajo
WORKDIR /app

# Limpiar listas de paquetes duplicadas y actualizar e instalar dependencias del sistema
RUN rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y curl cron

# Copiar los archivos de requerimientos
COPY requirements.txt .
# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copiar el contenido de la aplicación al contenedor
COPY /app .
COPY start.sh .

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Crear directorio de logs y establecer permisos
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Comando para ejecutar la aplicación
CMD ["./start.sh"]
