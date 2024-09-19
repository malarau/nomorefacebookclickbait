# No + Facebook clickbait

[![en](https://img.shields.io/badge/lang-en-blue.svg)](README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](README.es.md)

Facebook Scraper and Automatic Summarizer... In Principle

## Features

- Scraping Facebook posts from specific pages
- Extracting content from linked articles using Goose3
- Generating summaries using Ollama language models
- Automatically commenting summaries on original Facebook posts
- Support for local and Docker container execution

## Setup and Configuration

### Clone repository
```
git clone https://github.com/your-username/facebook-scraper-summarizer.git
cd facebook-scraper-summarizer
```

### Configuration
- Copy the [.env.example](.env.example) file to ```.env```
- Configure as appropriate:

  * ```USERNAME```: Your Facebook email
  * ```PASSWORD```: Your Facebook password
  * ```POST_TO_SCRAPE```: Number of posts to scrape per page
  * ```MAX_SCROLLS```: Maximum number of scrolls on the page
  * ```FACEBOOK_PAGES```: List of Facebook pages to scrape, separated by commas
  * ```TESTING```: Set test mode (True/False), results will still be logged in [app\logs\app.log](app\logs\app.log)
  * ```HEADLESS```: Run the browser in headless mode, i.e., whether you can see the Chrome window or not (True/False)
  * ```MODEL_NAME```: Name of the Ollama model to use
  * ```TRUNCATE_AT```: Maximum number of characters to truncate the comment in the Facebook post
  * ```CRON_SCHEDULE```: In Docker, sets how often the execution will repeat

#### Resources

You can set the amount of resources to be used for each container. There are 2 containers, one for Selenium (the browser) and another one in charge of Scraping. To do this you must modify [docker-compose.yml](docker-compose.yml) and for each container, modify those values:

```
resources:
  limits:
    cpus: '0.5'
    memory: 1G
```
        
#### Prompt to use:

Adjust the summary prompt in the [app/model/config.toml](app/model/config.toml) file

## Execution in Docker
- Clone repository
- Configure ```.env``` (and set ```DOCKER_ENV=True```)
- Build and run container:

```
docker-compose up --build
```
- You can check the operation in real-time (if ```HEADLESS``` is ```False``` in ```.env```) at http://localhost:4444/ui/#/sessions (password: secret)

## Local Execution
- Clone repository
- Configure ```.env``` (and set ```DOCKER_ENV=False```)

1. ### Python
- Version 3.11+
- Virtual environment:
```
python -m venv venv
venv\Scripts\activate # En Linux usar `source venv/bin/activate`
pip install -r requirements.txt
```

2. ### Chromedriver
To control the Chrome browser (must be installed):

- Download [chromedriver](https://getwebdriver.com/chromedriver)
- Copy it to: ```app/driver/chromedriver/```

3. ### Ollama
The language model that will handle the summaries.
- Download and install [Ollama](https://ollama.com/download/) 
- Install the desired [model](https://ollama.com/library).

For example: ```qwen2:1.5b-instruct-q5_K_M```
```
ollama pull qwen2:1.5b-instruct-q5_K_M
```
- Set the same model for the ```MODEL_NAME``` variable in ```.env```

4. ### Execution
```
python app/facebook_driver.py
```

## TODO List

- Facebook:
  - [ ] Implement checks for account bans on pages or Facebook platform
  - [ ] Develop functionality to create Facebook accounts automatically

- Content Extraction:
  - [ ] Modularize the extractor (Goose3) function

- System Monitoring:
  - [ ] Implement a separate service/container for status monitoring
    - [ ] Migrate database to its own container
    - [ ] Implement a specific/dedicated logging tool
    - [ ] Implement a monitoring dashboard (e.g., using Flask)

- Content:
  - [ ] Image/video analysis

- Model/Prompt
  - [ ] Preprocesing to analyze if it is a kind of clickbait (last time I attempted to do it, it was always true or always false :c)

## Issues

- If the article is about or contains sensitive information, the model could decline to provide an answer:

```
Fb post (about psychopaths):
https://web.facebook.com/RadioBioBio/posts/pfbid02GXJpVgfACnsBTgePA7kZPsU5UpAKFiBWMRYjubbVWkzN5YpVyPcbyUYEjWJp3CoQl?_rdc=1&_rdr

Article (close to 3k tokens):
https://www.biobiochile.cl/noticias/salud-y-bienestar/mente/2024/08/30/relato-de-una-psicopata-me-cuesta-sentir-empatia-por-los-demas.shtml

Answer:
Lo siento, pero no puedo proporcionar la información solicitada.
```

### Docker is using all my resources in Windows :(

You can try [this manual solution](https://github.com/microsoft/WSL/issues/8725#issuecomment-1260627017):

```
in C:\Users\<yourusername>, CREATE .wslconfig file (skip if already there)

Edit the file:

[wsl2]
memory=1GB # Limits VM memory in WSL 2. If you want less than 1GB, use something like 500MB, not 0.5GB
processors=2 # Makes the WSL 2 VM use two virtual processors
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

- This project is for educational purposes only
- First incursion using Docker/Ollama