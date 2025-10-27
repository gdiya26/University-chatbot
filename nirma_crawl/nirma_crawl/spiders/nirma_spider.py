import scrapy
from urllib.parse import urljoin
import os
import re


class NirmaTextSpider(scrapy.Spider):
    name = "nirma_txt"
    allowed_domains = ["nirmauni.ac.in"]
    start_urls = ["https://nirmauni.ac.in/"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1.5,
        "AUTOTHROTTLE_ENABLED": True,
        "FEED_EXPORT_ENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
    }

    def parse(self, response):
        # --- Extract visible text ---
        text_parts = response.css("body *::text").getall()
        text = " ".join(text_parts)
        text = re.sub(r"\s+", " ", text).strip()

        # --- Determine file path ---
        path = response.url.replace("https://", "").replace("http://", "")
        if path.endswith("/"):
            path += "index"
        path = re.sub(r"[^\w\-_/\.]", "_", path)
        txt_path = os.path.join("texts", f"{path}.txt")

        # --- Save as .txt file ---
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"URL: {response.url}\n\n{text}")
        self.log(f"Saved text file {txt_path}")

        # --- YIELD data for CSV export ---
        yield {
            "url": response.url,
            "title": response.css("title::text").get(default="").strip(),
            "text_file": txt_path,
        }

        # --- Follow internal links ---
        for link in response.css("a::attr(href)").getall():
            absolute_url = urljoin(response.url, link)
            if "nirmauni.ac.in" in absolute_url:
                yield response.follow(absolute_url, callback=self.parse)
