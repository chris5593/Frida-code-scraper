import time
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def scrape_codeshare_selenium(start_url, visited=None, headless=False):
    if visited is None:
        visited = set()
    if start_url in visited:
        return
    visited.add(start_url)

    # Configure Chrome options
    options = webdriver.ChromeOptions()
    # 1. For debugging, set headless=False (show browser window)
    if headless:
        options.add_argument("--headless")
    # 2. Add user-agent to reduce blocking
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set up the ChromeDriver service
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Increase page load timeout
        driver.set_page_load_timeout(300)
        driver.get(start_url)

        # Wait a bit for dynamic content
        time.sleep(5)

        rendered_html = driver.page_source
        soup = BeautifulSoup(rendered_html, "html.parser")

        # Search for 'frida --codeshare' text
        snippet_strings = soup.find_all(
            string=lambda text: text and "frida --codeshare" in text
        )
        for snippet_text in snippet_strings:
            print(f"Found snippet on {start_url}:")
            print(snippet_text.strip())
            print("-" * 80)

        # Recursively explore links
        for link in soup.find_all("a", href=True):
            next_url = urljoin(start_url, link["href"])
            if "codeshare.frida.re" in next_url:
                scrape_codeshare_selenium(next_url, visited, headless=headless)

    except Exception as e:
        print(f"Error processing {start_url}: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    start_url = "https://codeshare.frida.re/"
    scrape_codeshare_selenium(start_url, headless=False)
