import hashlib
import os

import msgspec

from api.types import Car
from api.scraping import CarsScraper

class InMemoryCachingCarsScraper(CarsScraper):
    def __init__(self, carsScraper: CarsScraper):
        super().__init__()
        self.carsScraper = carsScraper
        self.cache = {}
        
    def scrape(self, url):
        if url in self.cache:
            return self.cache[url]
        else:
            result = self.carsScraper.scrape(url)
            self.cache[url] = result
            return result
        
class FileCachingCarsScraper(CarsScraper):
    def __init__(self, cache_dir: str, carsScraper: CarsScraper):
        super().__init__()
        self.carsScraper = carsScraper
        self.cache_dir = cache_dir
        
    def _get_cache_filename(self, url):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.json")
    
    def scrape(self, url):
        cache_filename = self._get_cache_filename(url)
        
        if os.path.exists(cache_filename):
            with open(cache_filename, 'r') as cache_file:
                return msgspec.json.decode(cache_file.read(), type=list[Car])
        else:
            result = self.carsScraper.scrape(url)
            with open(cache_filename, 'w') as cache_file:
                cache_file.write(msgspec.json.encode(result).decode('utf-8'))
                return result