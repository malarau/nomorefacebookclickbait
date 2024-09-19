import os, sys
from dotenv import find_dotenv, load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.driver.facebook_scraper import FacebookScraper
from app.driver.selenium_handler import SeleniumHandler
from app.logger_config import app_logger, cron_logger

class FacebookDriver:
    def __init__(self):
        self.ready = 1
        app_logger.info("\n")
        app_logger.info("//"*50)
        app_logger.info("//"*50)

        load_dotenv(find_dotenv())

        self.model = os.getenv('MODEL_NAME')

        # Username and password
        self.username = os.getenv('USERNAME')
        self.password = os.getenv('PASSWORD')
        if self.username == None or self.password == None:
            app_logger.error("USERNAME o PASSWORD not found in .env")
            self.ready = 0
            raise

        # Facebook scraper
        try:
            self.post_to_scrape = int(os.getenv('POST_TO_SCRAPE'))
            self.max_scrolls = int(os.getenv('MAX_SCROLLS')) 
        except Exception:
            self.ready = 0
            app_logger.error("POST_TO_SCRAPE and MAX_SCROLLS in .env must to be numbers")
            raise

        # Facebook pages
        try:
            self.pages = os.getenv('FACEBOOK_PAGES').split(',')
            if len(self.pages) == 0:
                app_logger.error("No pages found in .env (FACEBOOK_PAGES)")
                self.ready = 0
                raise
        except:
            self.ready = 0
            app_logger.error(f"There was an error trying to get FACEBOOK_PAGES in .env file")
            raise
        
        # Is testing?
        self.is_testing = os.getenv("TESTING", 'False').lower() in ('true', '1', 't')
        # Check if using Docker
        self.docker_env = os.getenv("DOCKER_ENV", False).lower() in ('true', '1', 't')
        # Check if browser is headledd
        self.headless = os.getenv("HEADLESS", False).lower() in ('true', '1', 't')        

        self.log_env()

        self.selenium = SeleniumHandler(self.docker_env, headless=self.headless)
        self.scraper = FacebookScraper(self.selenium, self.docker_env, is_testing=self.is_testing)
        self.scraped_posts = {}

    def log_env(self):
        app_logger.info(f"{'MODEL:':<20} {self.model}")
        app_logger.info(f"{'USERNAME:':<20} {self.username}")
        app_logger.info(f"{'POST_TO_SCRAPE:':<20} {self.post_to_scrape}")
        app_logger.info(f"{'MAX_SCROLLS:':<20} {self.max_scrolls}")
        app_logger.info(f"{'FACEBOOK_PAGES:':<20} {self.pages}")
        app_logger.info(f"{'TESTING:':<20} {self.is_testing}")
        app_logger.info(f"{'DOCKER ENV:':<20} {self.docker_env}")
        app_logger.info(f"{'HEADLESS:':<20} {self.headless}")
        
    def run(self):
        if self.ready:
            if self.login():
                self.summarize_posts(self.pages)
        else:
            app_logger.error(f"Not ready, there is a problem initializating FacebookDriver class.")

    def login(self):
        self.selenium.get(self.scraper.SOURCE_URL)
        return self.selenium.login(self.username, self.password, self.scraper.SOURCE_URL)

    def summarize_posts(self, pages):
        app_logger.info("Iterating over all facebook pages")
        for page in pages:
            # Scrape
            try:
                self.scraped_posts[page] = self.scraper.process_facebook_page(page, post_to_scrape=self.post_to_scrape, max_scrolls=self.max_scrolls)
            except Exception as e:
                app_logger.error(f"There was an error trying to scrape page: {page}. Error: {e}")
                self.scraped_posts[page] = []

    def close(self):
        self.selenium.close()

if __name__ == "__main__":
    import time
    try:
        start_time = time.time()
        cron_logger.info(f"---------------------- Starting app!")
        
        facebook_driver = FacebookDriver()
        cron_logger.info("FacebookDriver created, now: Running... ")
        facebook_driver.run()
        facebook_driver.close()

        end_time = time.time()
        elapsed_time = end_time - start_time
        cron_logger.info(f"App finished in {elapsed_time:.2f} seconds\n")
    except Exception as e:
        cron_logger.error(e)