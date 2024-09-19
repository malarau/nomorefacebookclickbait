# No + Facebook clickbait

[![en](https://img.shields.io/badge/lang-en-blue.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)

Facebook Scraper y Resumidor Automático... En Principio

## Características

- Scraping de posts de Facebook de páginas específicas
- Extracción de contenido de artículos vinculados usando Goose3
- Generación de resúmenes utilizando modelos de lenguaje de Ollama
- Comentario automático de los resúmenes en los posts originales de Facebook
- Soporte para ejecución local y en contenedores Docker

## Inicio y configuración

### Clonar repositorio
```
git clone https://github.com/tu-usuario/facebook-scraper-summarizer.git
cd facebook-scraper-summarizer
```

### Configuración
- Copiar el archivo [.env.example](.env.example) a ```.env```
- Configurar según corresponda:

  * ```USERNAME```: Tu correo electrónico de Facebook
  * ```PASSWORD```: Tu contraseña de Facebook
  * ```POST_TO_SCRAPE```: Número de posts a scrapear por página
  * ```MAX_SCROLLS```: Número máximo de desplazamientos en la página
  * ```FACEBOOK_PAGES```: Lista de páginas de Facebook a scrapear, separadas por comas
  * ```TESTING```: Configura el modo de prueba (True/False), igualmente los resultados quedarán registrados en [app\logs\app.log](app\logs\app.log)
  * ```HEADLESS```: Ejecuta el navegador en modo headless, o sea, si podrás ver la ventana de Chrome o no (True/False)
  * ```MODEL_NAME```: Nombre del modelo de Ollama a utilizar
  * ```TRUNCATE_AT```: Número máximo de caracteres para truncar el comentario en la publicación de Facebook (por si se vuelve loco el modelo de lenguaje)
  * ```CRON_SCHEDULE```: En Docker, establece cada cuanto tiempo se volverá a ejecutar


#### Recursos

Puede establecer la cantidad de recursos que se utilizarán para cada contenedor. Hay 2 contenedores, uno para Selenium (el navegador) y otro encargado del Scraping. Para ello debes modificar [docker-compose.yml](docker-compose.yml) y para cada contenedor, modificar esos valores:

```
resources:
  limits:
    cpus: '0.5'
    memory: 1G
```

#### Prompt a usar:

Ajusta el prompt de resumen en el archivo [app/model/config.toml](app/model/config.toml)

## Ejecución en Docker
- Clonar repositorio
- Configurar ```.env``` (y establecer ```DOCKER_ENV=True```)
- Construir y ejecutar contenedor:

```
docker-compose up --build
```
- Es posible revisar el funcionamiento en tiempo real (si ```HEADLESS``` es ``False`` en ```.env```) desde http://localhost:4444/ui/#/sessions (password: secret)

## Ejecución Local
- Clonar repositorio
- Configurar ```.env``` (y establecer ```DOCKER_ENV=False```)

1. ### Python
- Versión 3.11+
- Virtual enviroment:
```
python -m venv venv
venv\Scripts\activate # En Linux usar `source venv/bin/activate`
pip install -r requirements.txt
```

2. ### Chromedriver
Para poder controlar el navegador Chrome (debe estar instalado):

- Descargar [chromedriver](https://getwebdriver.com/chromedriver)
- Copiarlo en: ```app/driver/chromedriver/```

3. ### Ollama
El modelo de lenguaje que se encargará de realizar los resúmenes.
- Descargar e instalar [Ollama](https://ollama.com/download/) 
- Instalar el [modelo](https://ollama.com/library) deseado.

Por ejemplo: ```qwen2:1.5b-instruct-q5_K_M```
```
ollama pull qwen2:1.5b-instruct-q5_K_M
```
- Establecer el mismo modelo para la variable ```MODEL_NAME``` en ```.env```

4. ### Ejecución

```
python app/facebook_driver.py
```

## TODO list

- Facebook:
  - [ ] Implementar verificaciones de suspensión/bloqueos de cuenta en páginas o en Facebook
  - [ ] Implementar funcionalidad para crear cuentas de Facebook automáticamente

- Extracción de Contenido:
  - [ ] Modularizar la función de extractor (Goose3)

- Monitoreo del Sistema:
  - [ ] Implementar un servicio/contenedor separado para el monitoreo de estado
    - [ ] Migrar la base de datos a su propio contenedor
    - [ ] Implementar una herramienta específica/dedicada para el registro de logs
    - [ ] Implementar un panel de monitoreo (por ejemplo, usando Flask)

- Contenido:
  - [ ] Analizar imágenes/video

- Modelo/Prompt
  - [ ] Preprocesado para analizar si es una especie de clickbait (la última vez que intenté daba siempre verdadero o siempre falso)

## Issues

- Si el articulo se trata o contiene información sensible, el modelo podría negarse a responder:

```
Fb post (about psychopaths):
https://web.facebook.com/RadioBioBio/posts/pfbid02GXJpVgfACnsBTgePA7kZPsU5UpAKFiBWMRYjubbVWkzN5YpVyPcbyUYEjWJp3CoQl?_rdc=1&_rdr

Article (close to 3k tokens):
https://www.biobiochile.cl/noticias/salud-y-bienestar/mente/2024/08/30/relato-de-una-psicopata-me-cuesta-sentir-empatia-por-los-demas.shtml

Answer:
Lo siento, pero no puedo proporcionar la información solicitada.
```

### Docker está usando todos mis recursos en Windows :(

Puede probar [esta solución manual](https://github.com/microsoft/WSL/issues/8725#issuecomment-1260627017):

```
in C:\Users\<yourusername>, CREATE .wslconfig file (skip if already there)

Edit the file:

[wsl2]
memory=1GB # Limits VM memory in WSL 2. If you want less than 1GB, use something like 500MB, not 0.5GB
processors=2 # Makes the WSL 2 VM use two virtual processors
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT: [LICENSE](LICENSE).

## Descargo de responsabilidad

- Este proyecto es solo para fines educativos
- Primera incursión usando Docker/Ollama