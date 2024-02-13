from botasaurus import *
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from urllib.parse import urlparse, urljoin

def scrape_website(url, timeout=6000):
    @browser(cache=True, parallel=20, reuse_driver=True, data=[url])
    def scrape_website_task(driver: AntiDetectDriver, data):
        url = validate_url(data)
        returnObj = {}
        driver.google_get(url)
        innerHtml = driver.bs4("html")
        allLinks = extract_urls_from_html(innerHtml)
        socialUrls = ["facebook.com/",  "twitter.com/", "linkedin.com/", "instagram.com/", "youtube.com/"]
        socials = [link for link in allLinks if any(socialUrl in link for socialUrl in socialUrls)]
        returnObj["socials"] = socials
        parsed_url = urlparse(url)
        base = parsed_url.netloc

        internal_urls = []
        for link in allLinks:
            # Join relative URLs to the base URL
            link = urljoin(url, link)
            parsed_link = urlparse(link)
            link_base = parsed_link.netloc
            
            # Check if the link belongs to the same domain
            if link_base == base:
                internal_urls.append(link)

        # Remove duplicates
        internal_urls = list(set(internal_urls))
        if len(internal_urls)>1:

            for url in internal_urls:
                #find the relevant hrefs and click on it
                driver.click("a[href='" + url + "']")
                #get the text of the page
                whole = driver.text("html")
                returnObj["internal"][url] = whole


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

def extract_urls_from_html(html_content):
    
    # Find all 'a' tags, which define hyperlinks
    links = html_content.find_all('a')
    
    # Extract the 'href' attribute from each link
    urls = [link.get('href') for link in links if link.get('href') is not None]
    
    return urls


def validate_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return "http://" + url