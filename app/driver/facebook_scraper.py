from app.driver.selenium_handler import SeleniumHandler
from app.database.facebook_database import DatabaseFactory
from app.model.ollama_model import OllamaModel
from app.utils.utils import GooseExtractor, URLUtils
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from app.logger_config import app_logger

from datetime import datetime
import time
import random

class FacebookScraper:
    def __init__(self, selenium_handler: SeleniumHandler, docker_env, is_testing=False):
        self.selenium = selenium_handler
        self.is_testing = is_testing
        self.goose_extractor = GooseExtractor()
        self.url_utils = URLUtils()
        # Database // Local = SQLite, Docker = PostgreSQL
        self.db = DatabaseFactory.create_database(docker_env)
        # Ollama model
        self.ollama_model = OllamaModel()
    
    SOURCE_URL = "https://www.facebook.com/"

    CSS_SELECTOR_ALL_POSTS = 'div[data-virtualized]'
    CSS_SELECTOR_POST_ID_ELEMENT = 'span > a[target="_blank"][role="link"]'
    CSS_SELECTOR_POST_ID_ON_HOVER = 'a[href*="/posts/"][role="link"]'
    CSS_SELECTOR_POST_TEXT = 'div[data-ad-comet-preview="message"] div[dir="auto"]'
    CSS_SELECTOR_LINK_POST_TEXT = 'span.html-span[dir="auto"]'
    CSS_SELECTOR_AUTHOR_COMMENT = 'div[role="article"][aria-label][tabindex="-1"]'
    CSS_SELECTOR_AUTHOR_COMMENT_LINK = 'span[dir="auto"][lang]'
    CSS_SELECTOR_COMMENT_BOX = 'div[aria-label][contenteditable="true"]'

    CSS_SELECTOR_IMAGEPOST = 'div[class][style*="background-color"][style*="background-image"]'

    def get_fb_posts(self):
        return self.selenium.find_elements(By.CSS_SELECTOR, self.CSS_SELECTOR_ALL_POSTS)
    
    # TODO:
    """
        -   GET POST TEXT
        -   GET SECOND POST TEXT
        -   GET LINK TO THE ARTICLE

        USING EVERY CASE BY HIS OWN!!!!
    """

    def _get_post_text(self, fb_post_element):
        app_logger.info("")
        try:
            post_text_element = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_POST_TEXT)
            #if "VIDEO |" in post_text_element.text:
            #    raise Exception("Video. No article available")
            return post_text_element.text
        except:
            # Check if is that kind of post with style, example: 
            # <div class="x1yx25j4 x13crsa5 x6x52a7 x1rxj1xn xxpdul3" style="color:rgba(255,255,255,1);font-size:30px;font-style:NORMAL;font-weight:bold;text-align:CENTER" id=":Rlal5bb9l5qq9papd5aqH2:">
            try:
                # Just 1 div
                div = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_IMAGEPOST)
                return div.text.replace("\n", "").replace(self.url_utils.extract_url(div.text), "")
            except Exception as e:
                # Then is not just 1 div
                divs = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_IMAGEPOST).find_elements(By.TAG_NAME, 'div')
                
                text = ""
                for div in divs:
                    try:
                        text = div.text.replace("\n", "").replace(self.url_utils.extract_url(div.text), "")
                        return text
                    except:
                        app_logger.warning("Can't get text from specific div")

                raise Exception(f"Error extracting post text: {e}")

    def _get_link_post_text(self, fb_post_element):
        app_logger.info("")
        try:
            link_text_element = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_LINK_POST_TEXT)
            return link_text_element.text
        except Exception as e:
            raise Exception(f"Error extracting link post text: {e}")
   
    # This function is a monster, help
    def _get_article_data(self, fb_post_element):
        app_logger.info("")
        try:
            # Case 1: Traditional post = text + [image and text-link]
            try:
                link_element = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_LINK_POST_TEXT)
                if not link_element.text:
                    raise Exception("No link text found")
            except:
                # Case 2: Link in comments
                try:
                    # Get the author's comment box
                    link_element = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_AUTHOR_COMMENT)
                    # Get the url element (span)
                    link_element = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_AUTHOR_COMMENT_LINK)
                except:
                    try:
                        # Case 3: Link in the content text, image without a link.
                        url = self.url_utils.extract_url(self._get_post_text(fb_post_element))
                    except:
                        # Case 4: "Image post"
                        # <div class="x1yx25j4 x13crsa5 x6x52a7 x1rxj1xn xxpdul3" style="color:rgba(255,255,255,1);font-size:30px;font-style:NORMAL;font-weight:bold;text-align:CENTER" id=":Rlal5bb9l5qq9papd5aqH2:">
                        try:
                            # Just 1 div
                            div = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_IMAGEPOST)
                            url = self.url_utils.extract_url(div.text)
                            if url == "":
                                raise
                        except:
                            # Multiple divs
                            divs = fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_IMAGEPOST).find_elements(By.TAG_NAME, 'div')

                            url = ""
                            for div in divs:
                                try:
                                    url = self.url_utils.extract_url(div.text)
                                except:
                                    print("Can't get url from specific text div")

                            if url == "":
                                raise

            # Click url and open a new tab
            try:
                app_logger.info("Case 1 and 2")
                # Case 1 and 2
                self.selenium.hover_element(link_element)
                link_element.click()
                # Switch to the new tab
                self.selenium.driver.switch_to.window(self.selenium.driver.window_handles[-1])
            except:
                app_logger.info("Case 1 and 2 weren't possible, try with case 3, 4")
                # Case 3
                self.selenium.open_new_tab(url=url)

            time.sleep(random.randint(1, 2))
            url = self.selenium.driver.current_url
            self.selenium.close_all_other_tabs()

            try:
                app_logger.info("Getting article data")
                content = self.goose_extractor.get_article_text(url)
            except Exception as err:
                raise Exception(f"Error extracting article content from {url}: {err}")

            return url, content
        
        except Exception as err:
            raise Exception(f"General error in _get_article_data: {err}")

    def _get_comment_box_element(self, fb_post_element):
        app_logger.info("")
        try:
            return fb_post_element.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_COMMENT_BOX)
        except Exception as e:
            raise Exception(f"Error extracting comment box element: {e}")

    def scrape_post(self, fb_post_element):
        app_logger.info("")
        try:
            post_text = self._get_post_text(fb_post_element)
        except Exception as e:
            post_text = "-"
            app_logger.warning(e)

        try:
            link_text = self._get_link_post_text(fb_post_element)
            if post_text == link_text: # Avoid sending same text, reduce prompt, less inference time
                link_text = "-"
        except Exception as e:
            link_text = "-"
            app_logger.warning(e)

        try:
            post_link, article_content = self._get_article_data(fb_post_element)
        except Exception as e:
            post_link = None
            article_content = None
            app_logger.warning(e)

        return [post_text, link_text, post_link, article_content]

    # This function is a monster, help
    def process_facebook_page(self, page_name, post_to_scrape=10, max_scrolls=5):
        app_logger.info(f"Loading page: {self.SOURCE_URL}{page_name}")
        self.selenium.get(f"{self.SOURCE_URL}{page_name}")
        time.sleep(2)

        fb_posts = []
        max_scrolls_i = 0
        lasts_scraped = 0

        while len(fb_posts) < post_to_scrape and max_scrolls_i < max_scrolls:
            max_scrolls_i += 1
            loaded_posts = self.get_fb_posts()

            # Example: First scroll gave me 6 post, second scroll 8, then we just have to scrape last 2.
            for post in loaded_posts[lasts_scraped:]:
                app_logger.info(">>>>>> Iterating over a new post element.")
                lasts_scraped = len(loaded_posts)

                try:
                    link_element = post.find_element(By.CSS_SELECTOR, self.CSS_SELECTOR_POST_ID_ELEMENT)               
                    self.selenium.scroll_to_element(link_element)
                    self.selenium.scroll(times=3, default_key=Keys.DOWN)
                    self.selenium.hover_element(link_element)
                except:
                    app_logger.warning("An exception ocurred while getting post_id")
                    continue

                time.sleep(random.randint(1, 2))

                # Wait for /posts/
                try:
                    post_link_element = self.selenium.find_element(post, By.CSS_SELECTOR, self.CSS_SELECTOR_POST_ID_ON_HOVER, timeout=5)
                    post_link = post_link_element.get_attribute("href")
                except:
                    post_link = ""

                post_id = self.url_utils.extract_post_id(post_link)

                if post_id != None:
                    # Check if the current fb post id is on the db

                    if self.is_testing: # If testing, dont save the post, to try as many times as we want with the same post
                        db_result = True
                    else:
                        db_result = self._insert_post(post_id, page_name)

                    if db_result:                        
                        app_logger.info(f"Procesing post: {self.SOURCE_URL}{page_name}/posts/{post_id}")

                        # Try to get the rest of the post info
                        post_data = self.scrape_post(post)

                        if None not in post_data:
                            # Delete this, is useless now... or isn't?
                            fb_posts.append([post_id] + post_data)

                            # Summarize
                            summary = self.summarize_post(fb_posts[-1])                            
                            if summary:                        
                                comment_result = self.make_comment(page_name, post_id, fb_posts[-1], summary)                        

                                if comment_result and db_result and not self.is_testing:
                                    if not self.db.update_post_success(post_id, 1):
                                        app_logger.warning(f"Wasn't possible to update database on post_id: {post_id}")
                else:
                    app_logger.error(f"No match found while looking for post id. Post link: {post_link}" )

                if len(fb_posts) >= post_to_scrape:
                    return fb_posts

            #self.selenium.scroll(times=random.randint(3, 5))

        return fb_posts
    
    def summarize_post(self, post):
        try:
            if post[4] != "" or len(post[1]) < len(post[4]) or len(post[2]) < len(post[4]):
                summary = self.ollama_model.summarize(post[1], post[1], post[4])
            else:
                app_logger.error("Not possible to summarize. Not enough data.")
                summary = None
            return summary
        except Exception as e:
            app_logger.error(f"Error while summarizing: \n{e}")
            return None
        
    def make_comment(self, page_name, post_id, post, summary):
        try:
            # Open a new tab
            self.selenium.open_new_tab(url=self.SOURCE_URL+"/"+page_name+"/posts/"+post_id)    
            time.sleep(1)
            # Logging
            app_logger.info(post[1])
            app_logger.info(post[2])
            app_logger.info("\n"+summary)
            app_logger.info("------")

            if not self.is_testing:
                # Get comment box
                box_elem = self._get_comment_box_element(self.selenium.driver)
                self.selenium.type_with_delay(box_elem, summary)
                app_logger.info(f"Testing FALSE, comment done")
            else:
                app_logger.info(f"Testing TRUE, no comment done")
        except Exception as e:
            self.selenium.close_all_other_tabs()
            app_logger.error(f"There was an error trying to make a comment: {e}")
            return False
        
        self.selenium.close_all_other_tabs()
        return True
        
    # TODO: Not related functions
    def _insert_post(self, post_id, page):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.db.insert_post(post_id, date, page, 0): # By default, no success
            app_logger.info(f"Post {post_id} saved correctly.")
            return True
        else:
            app_logger.error(f"Post {post_id} already exists on db.")
            return False