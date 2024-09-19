import os
from dotenv import load_dotenv
import ollama, toml
from app.logger_config import app_logger

class OllamaModel:
    def __init__(self, config_path='config.toml'):
        load_dotenv()
        self.model_name = os.getenv('MODEL_NAME')
        self.truncate_at = int(os.getenv('TRUNCATE_AT'))

        # Absolut dir
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Build the route
        self.config_path = os.path.join(base_path, config_path)
        self.config = self.load_config()

        self.prompt_template = self.config['prompt']['template']
        self.inference_options = ollama.Options(
            temperature=self.config['inference']['temperature'],
            top_p=self.config['inference']['top_p'],
            top_k=self.config['inference']['top_k']
        )

    def load_config(self):
        try:
            return toml.load(self.config_path)
        except Exception as e:
            app_logger.error(f"Error loading config: {e}")
            raise

    def summarize(self, title_post, link_text_post, article_text):
        full_prompt = self.prompt_template.format(
            title_post=title_post,
            link_text_post=link_text_post,
            article_text=article_text.replace("\\", " ").replace("\n\n", " ")
        )

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options=self.inference_options
            )['response'].strip()
            return response[:self.truncate_at]
        except Exception as err:
            app_logger.error(f"Error on inference: {err}")
            return ""