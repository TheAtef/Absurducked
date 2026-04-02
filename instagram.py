from parth_dl import InstagramDownloader

class InstagramScraper:
    def __init__(self):
        self.scraper = InstagramDownloader()

    def get_info(self, url, index):
        info = self.scraper.get_info(url)
        url = info['formats'][-1]['url']
        return url
    
    
    