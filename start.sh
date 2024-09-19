#!/bin/bash

# Inicia el servicio Ollama en segundo plano
ollama serve &

# Espera a que Ollama esté listo
while ! curl -s http://localhost:11434/api/tags >/dev/null; do
    sleep 1
done
echo "> Ollama serving OK"

# Descarga el modelo especificado
ollama pull $MODEL_NAME
echo "> Ollama model OK"

# Guarda las variables para poder ser usadas desde cron
# https://stackoverflow.com/questions/2229825/where-can-i-set-environment-variables-that-crontab-will-use#comment59720758_34492957
env >> /etc/environment

# Configura el crontab usando la variable de entorno CRON_SCHEDULE
echo "$CRON_SCHEDULE /usr/local/bin/python /app/facebook_driver.py 2>> /app/logs/cron_stderr.log" > /etc/cron.d/crontab
# Establecer permisos y añadir el crontab
chmod 0644 /etc/cron.d/crontab && crontab /etc/cron.d/crontab
touch /var/log/cron.log
echo "> Crontab OK"

# Iniciar el servicio y dejar el container corriendo
/etc/init.d/cron start && tail -f /var/log/cron.log