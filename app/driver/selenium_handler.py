from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from app.logger_config import app_logger

import platform
import os
import time
import random
import pickle

class SeleniumHandler:
    def __init__(self, docker_env, headless=False):
        self.driver = self._initialize_driver(docker_env, headless)

        # Login
    CSS_SELECTOR_LOGIN_BUTTON = 'button[data-testid="royal_login_button"]'
    
    def get_cookie_filename(self, username):
        base_path = os.path.dirname(os.path.abspath(__file__))
        cookie_directory = os.path.join(base_path, 'chromedriver')
        if not os.path.exists(cookie_directory):
            os.makedirs(cookie_directory)
        return os.path.join(cookie_directory, f"{username}.pkl")

    def _initialize_driver(self, docker_env, headless):
        # Options
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # For images
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        # Lightweight user-agent??
        #chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36')

        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument('--disable-gpu')

        if docker_env:
            app_logger.info("Initializating using Docker")
            wd = webdriver.Remote(
                command_executor='http://selenium:4444/wd/hub',
                options=chrome_options
            )
        else:
            # Service
            platform_system = platform.system()

            if platform_system == "Windows":
                app_logger.info("Initializing from local on Windows")
                chrome_path = os.path.join("app", "driver", "chromedriver", "chromedriver.exe")
            elif platform_system == "Darwin":  # macOS
                app_logger.info("Initializing from local on macOS")
                chrome_path = os.path.join("app", "driver", "chromedriver", "chromedriver_mac")
                os.chmod(chrome_path, 0o755)
            elif platform_system == "Linux":
                app_logger.info("Initializing from local on Linux")
                chrome_path = os.path.join("app", "driver", "chromedriver", "chromedriver_linux")
                os.chmod(chrome_path, 0o755)
            else:
                app_logger.error(f"Unsupported operating system: {platform_system}")
                raise OSError(f"Unsupported operating system: {platform_system}")

            if not os.path.exists(chrome_path):
                app_logger.error(f"ChromeDriver not found at {chrome_path}")
                raise FileNotFoundError(f"ChromeDriver not found at {chrome_path}")

            chrome_service = Service(chrome_path)
            wd = webdriver.Chrome(
                service=chrome_service,
                options=chrome_options
            )
        
        return wd
    
    def login(self, username, password, SOURCE_URL):
        try:
            self.load_cookies(self.get_cookie_filename(username))
            self.get(SOURCE_URL)
            time.sleep(5)

            app_logger.info("Logged in using cookies")
            return True
        except Exception as e: # No cookies
            app_logger.info(f"login() - {e}")
            self.get(SOURCE_URL)
            
            # Wait for button
            button = self.find_element(self.driver, By.CSS_SELECTOR, self.CSS_SELECTOR_LOGIN_BUTTON)
            
            try:
                # Check if Login button exists
                if button:
                    # Find and complete login fields
                    username_field = self.driver.find_element(By.ID, 'email')  
                    password_field = self.driver.find_element(By.ID, 'pass')
                
                    username_field.send_keys(username)
                    time.sleep(1.8)
                    password_field.send_keys(password)
                    time.sleep(1.8)

                    button.click()
                    time.sleep(5)
                    
                    self.save_cookies(self.COOKIE_FILENAME.format(username=username))
                    app_logger.info("Logged in correctly")
                    return True
                else:
                    app_logger.warning("Login button not found")
                    return False
            except Exception as e:
                app_logger.error(f"There was an error tyring to login: {e}")
                return False

    def get(self, url):
        self.driver.get(url)

    def find_element(self, element, by, value, timeout=10):
        return WebDriverWait(element, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def find_elements(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )

    def scroll(self, default_key=Keys.DOWN, times=1):
        body = self.driver.find_element(By.CSS_SELECTOR, "body")
        for _ in range(times):
            body.send_keys(default_key)
            time.sleep(random.randint(4, 10) / 10)

    def open_new_tab(self, url=None):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        if url:
            self.driver.get(url)

    def close_all_other_tabs(self):
        app_logger.info("Closing all other tabs")
        for tab_i in range(1, len(self.driver.window_handles)):
            self.driver.switch_to.window(self.driver.window_handles[tab_i])
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def save_cookies(self, filename):
        pickle.dump(self.driver.get_cookies(), open(filename, "wb"))

    def load_cookies(self, filename):
        cookies = pickle.load(open(filename, "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def hover_element(self, element):
        ActionChains(self.driver).move_to_element(element).perform()

    def scroll_to_element(self, element):
        ActionChains(self.driver).scroll_to_element(element).perform()

    def type_with_delay(self, comment_box, summary):
        # Simulate typing the summary into the comment box    
            for char in summary:
                # Avoid sending mutliple messages
                # Wait a brief amount of time between keys, spaces or new lines                
                if char == "\n":
                    comment_box.send_keys(Keys.SHIFT, Keys.ENTER)
                    time.sleep(random.uniform(0.2, 0.4))
                else:
                    comment_box.send_keys(char)                
                    if char == " ":
                        time.sleep(random.uniform(0.1, 0.3))  # Longer pause after a space
                    else:
                        time.sleep(random.uniform(0.02, 0.08))  # Pause between characters
            
            # ENTER
            comment_box.send_keys(Keys.ENTER)

    def close(self):
        self.driver.quit()