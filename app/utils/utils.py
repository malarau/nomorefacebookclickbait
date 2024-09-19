import re

from goose3 import Goose

class GooseExtractor:
    def __init__(self):
        self.goose = Goose()
        self.goose.config.http_timeout = 10

    def get_article_text(self, url):
        try:
            article = self.goose.extract(url=url)
            return article.cleaned_text
        except Exception as err:
            raise Exception(f"Error extracting article from {url}: {err}")

class URLUtils():

    # TODO: Factorize

    def find_match(self, group, text, url_pattern):
        # Search for the first coincidence
        match = re.search(url_pattern, text)
        
        if match:
            return match.group(group)
        else:
            return ""

    def extract_url(self, text):
        url_pattern = r'https?://\S+|www\.\S+'
        return self.find_match(0, text, url_pattern)        
        
    def extract_post_id(self, post_link):
        url_pattern = r'\/posts\/(pfbid\w+)'
        # Extract fb post id if /posts/ was found in url
        return self.find_match(1, post_link, url_pattern)