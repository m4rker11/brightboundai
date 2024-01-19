from botasaurus import *
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def scrape_website(url, timeout=60):
    @browser(cache=True, parallel=20, reuse_driver=True, data=[url])
    def scrape_website_task(driver: AntiDetectDriver, data):
        url = validate_url(data)
        print(url)
        exists = driver.exists(url)
        print(exists)
        driver.google_get(url)
        
        whole = driver.text("html")
        return {
            url: whole
        }
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(scrape_website_task)
        try:
            # Wait for the result, with timeout
            result = future.result(timeout=timeout)
            return result
        except TimeoutError:
            executor.shutdown(wait=False)
            print(f"Scraping {url} timed out after {timeout} seconds.")
            return None


def validate_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return "http://" + url