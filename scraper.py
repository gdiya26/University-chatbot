"""import requests
from bs4 import BeautifulSoup
import trafilatura
import os
import time
from urllib.parse import urljoin, urlparse
import json

class NirmaWebsiteScraper:
    def __init__(self, base_url="https://www.nirmauni.ac.in"):
        self.base_url = base_url
        self.visited_urls = set()
        self.scraped_data = []
        self.data_dir = "data/raw"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def is_valid_url(self, url):
        
        parsed = urlparse(url)
        return parsed.netloc == "www.nirmauni.ac.in"
    
    def get_page_links(self, url):
    
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    links.append(full_url)
            
            return links
        except Exception as e:
            print(f"Error getting links from {url}: {e}")
            return []
    
    def scrape_page(self, url):
      
        try:
            print(f"Scraping: {url}")
            
            # Use trafilatura for clean text extraction
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, 
                                          include_comments=False,
                                          include_tables=True)
                
                if text and len(text.strip()) > 100:  # Only save meaningful content
                    return {
                        'url': url,
                        'content': text.strip(),
                        'title': self.get_page_title(url)
                    }
            return None
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def get_page_title(self, url):
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            return title.text.strip() if title else url.split('/')[-1]
        except:
            return url.split('/')[-1]
    
    def crawl(self, start_url, max_pages=100, max_depth=3):
        
        urls_to_visit = [(start_url, 0)]  # (url, depth)
        pages_scraped = 0
        
        # Priority URLs to scrape first
        priority_urls = [
            "https://www.nirmauni.ac.in/admissions",
            "https://www.nirmauni.ac.in/academics",
            "https://www.nirmauni.ac.in/placements",
            "https://www.nirmauni.ac.in/campus-life",
            "https://www.nirmauni.ac.in/about-us",
            "https://www.nirmauni.ac.in/contact-us"
        ]
        
        # Add priority URLs first
        for url in priority_urls:
            urls_to_visit.insert(0, (url, 0))
        
        while urls_to_visit and pages_scraped < max_pages:
            url, depth = urls_to_visit.pop(0)
            
            if url in self.visited_urls or depth > max_depth:
                continue
            
            self.visited_urls.add(url)
            
            # Scrape the page
            data = self.scrape_page(url)
            if data:
                self.scraped_data.append(data)
                pages_scraped += 1
                
                # Save incrementally
                self.save_data()
            
            # Get more links if not at max depth
            if depth < max_depth:
                new_links = self.get_page_links(url)
                for link in new_links[:5]:  # Limit links per page
                    urls_to_visit.append((link, depth + 1))
            
            # Be respectful - delay between requests
            time.sleep(1)
            
            print(f"Progress: {pages_scraped}/{max_pages} pages scraped")
        
        print(f"\n✅ Scraping complete! Total pages: {pages_scraped}")
        return self.scraped_data
    
    def save_data(self):
      
        # Save as individual text files
        for idx, item in enumerate(self.scraped_data):
            filename = f"{self.data_dir}/page_{idx+1}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"URL: {item['url']}\n")
                f.write(f"Title: {item['title']}\n")
                f.write(f"\n{item['content']}\n")
        
        # Save as JSON for reference
        with open(f"{self.data_dir}/all_data.json", 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(self.scraped_data)} pages to {self.data_dir}/")


if __name__ == "__main__":
    print("🕷️  Starting Nirma University Website Scraper...\n")
    
    scraper = NirmaWebsiteScraper()
    
    # Start crawling
    data = scraper.crawl(
        start_url="https://www.nirmauni.ac.in",
        max_pages=1000,  # Adjust based on needs
        max_depth=2     # How deep to crawl
    )
    
    print(f"\n✨ Scraping complete! Check the 'data/raw/' directory for results.")"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import trafilatura
import os
import time
from urllib.parse import urljoin, urlparse
import json
from xml.etree import ElementTree

# Session with retry + headers
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def safe_get(url, timeout=20):
    try:
        return session.get(url, timeout=timeout, verify=False, headers=HEADERS)
    except Exception as e:
        print(f"❌ Error requesting {url}: {e}")
        return None

class NirmaWebsiteScraper:
    def __init__(self, base_url="https://www.nirmauni.ac.in"):
        self.base_url = base_url
        self.visited_urls = set()
        self.scraped_data = []
        self.data_dir = "data/raw"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.netloc == "www.nirmauni.ac.in"
    
    def download_file(self, url):
        """Download and save non-HTML files like PDFs, DOCX, PPTX, etc."""
        try:
            file_exts = ('.pdf', '.docx', '.pptx', '.xls', '.xlsx')
            if url.lower().endswith(file_exts):
                response = safe_get(url)
                if response:
                    filename = os.path.join(self.data_dir, os.path.basename(urlparse(url).path))
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"📄 Downloaded file: {filename}")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    def get_page_links(self, url):
        """Extract all links from a page"""
        try:
            response = safe_get(url)
            if not response:
                return []
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                
                # Download documents if found
                if any(full_url.lower().endswith(ext) for ext in ['.pdf', '.docx', '.pptx', '.xls', '.xlsx']):
                    self.download_file(full_url)
                    continue
                
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    links.append(full_url)
            
            return links
        except Exception as e:
            print(f"Error getting links from {url}: {e}")
            return []
    
    def scrape_page(self, url):
        """Scrape content from a single page"""
        try:
            print(f"Scraping: {url}")
            
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
                
                if text and len(text.strip()) > 100:  # Only save meaningful content
                    return {
                        'url': url,
                        'content': text.strip(),
                        'title': self.get_page_title(url)
                    }
            return None
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def get_page_title(self, url):
        """Extract page title"""
        try:
            response = safe_get(url)
            if not response:
                return url.split('/')[-1]
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            return title.text.strip() if title else url.split('/')[-1]
        except:
            return url.split('/')[-1]
    
    def load_sitemap_urls(self):
        """Fetch URLs from sitemap.xml if available"""
        sitemap_url = urljoin(self.base_url, '/sitemap.xml')
        urls = []
        try:
            print(f"🔍 Checking for sitemap: {sitemap_url}")
            sitemap = safe_get(sitemap_url)
            if sitemap and sitemap.status_code == 200:
                tree = ElementTree.fromstring(sitemap.content)
                for loc in tree.findall(".//{*}loc"):
                    url = loc.text.strip()
                    if self.is_valid_url(url):
                        urls.append((url, 0))
                print(f"🗺️ Found {len(urls)} URLs in sitemap.")
        except Exception as e:
            print(f"No sitemap found or error: {e}")
        return urls
    
    def crawl(self, start_url, max_pages=1000, max_depth=5):
        """Crawl website starting from start_url"""
        urls_to_visit = [(start_url, 0)]
        pages_scraped = 0
        
        # Load sitemap URLs for deep coverage
        sitemap_urls = self.load_sitemap_urls()
        urls_to_visit = sitemap_urls + urls_to_visit
        
        # Priority URLs
        priority_urls = [
            "https://www.nirmauni.ac.in/admissions",
            "https://www.nirmauni.ac.in/academics",
            "https://www.nirmauni.ac.in/placements",
            "https://www.nirmauni.ac.in/campus-life",
            "https://www.nirmauni.ac.in/about-us",
            "https://www.nirmauni.ac.in/contact-us"
        ]
        
        for url in priority_urls:
            urls_to_visit.insert(0, (url, 0))
        
        while urls_to_visit and pages_scraped < max_pages:
            url, depth = urls_to_visit.pop(0)
            
            if url in self.visited_urls or depth > max_depth:
                continue
            
            self.visited_urls.add(url)
            
            data = self.scrape_page(url)
            if data:
                self.scraped_data.append(data)
                pages_scraped += 1
                self.save_page(data, pages_scraped)
            
            if depth < max_depth:
                new_links = self.get_page_links(url)
                for link in new_links:
                    if link not in self.visited_urls:
                        urls_to_visit.append((link, depth + 1))
            
            time.sleep(1)
            print(f"Progress: {pages_scraped}/{max_pages} pages scraped")
        
        print(f"\n✅ Deep scraping complete! Total pages: {pages_scraped}")
        self.save_data()
        return self.scraped_data
    
    def save_page(self, item, idx):
        """Save individual page incrementally"""
        filename = f"{self.data_dir}/page_{idx}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"URL: {item['url']}\n")
            f.write(f"Title: {item['title']}\n")
            f.write(f"\n{item['content']}\n")
        print(f"💾 Saved: {filename}")
    
    def save_data(self):
        """Save all scraped data as JSON for reference"""
        with open(f"{self.data_dir}/all_data.json", 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        print(f"📘 JSON data saved: {self.data_dir}/all_data.json")


if __name__ == "__main__":
    print("🕷️  Starting Nirma University Website Deep Scraper...\n")
    
    scraper = NirmaWebsiteScraper()
    
    data = scraper.crawl(
        start_url="https://www.nirmauni.ac.in",
        max_pages=5000,  # Deep crawl limit
        max_depth=5      # Deep recursive scan
    )
    
    print(f"\n✨ Deep scraping complete! Check 'data/raw/' for results.")
