import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class WebPageChecker:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.failed_urls = []
        self.checked_urls = []

    def read_urls_from_excel(self):
        """Reads URLs from the specified Excel file and returns them as a list."""
        df = pd.read_excel(self.excel_file)
        return df["URL"].tolist()

    def scrape_web_page(self, url):
        """Scrapes the content of a webpage and returns the extracted text from the <head> tag."""
        try:
            response = requests.get(url, timeout=60)  # Set timeout for requests
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.find('head').get_text()  # Extract content from the <head> tag
                if content:
                    print(f"{url}\n--------")
                self.checked_urls.append(url)  # Store URL
            else:
                print(f"Failed to retrieve {url}: Status code {response.status_code}")
                self.failed_urls.append(url)
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for {url}.")
            self.failed_urls.append(url)
        except Exception as e:
            print(f"Failed to retrieve content from {url}: {str(e)}")
            self.failed_urls.append(url)

    def url_checker(self):
        urls = self.read_urls_from_excel()
        
        # Use ThreadPoolExecutor to handle URL checking concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.scrape_web_page, url): url for url in urls}
            
            # Monitor the completion of the scraping
            for future in as_completed(futures):
                url = futures[future]
                try:
                    future.result()  # This will re-raise any exception that occurred in scrape_web_page
                except Exception as e:
                    print(f"An exception occurred for {url}: {str(e)}")

        # Save failed and checked URLs
        if self.failed_urls:
            df_failed = pd.DataFrame(self.failed_urls, columns=["Failed URLs"])
            df_failed.to_excel('failed_urls.xlsx', index=False)
            print(f"Saved failed URLs to 'failed_urls.xlsx'")
        
        if self.checked_urls:
            df_checked = pd.DataFrame(self.checked_urls, columns=["URL"])
            df_checked.to_excel('checked_urls.xlsx', index=False)
            print(f"Saved checked URLs to 'checked_urls.xlsx'")

# # Example usage
# if __name__ == "__main__":
#     excel_file = 'HelpLARebuild_Dataset.xlsx'  # Update with the actual Excel file path
#     scraper = WebPageChecker(excel_file)
#     scraper.url_checker()  # Change to url_checker()
