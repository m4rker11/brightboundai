from botasaurus import *
from AI.summarize import extractRelevantNestedLinks
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from urllib.parse import urlparse, urljoin

def scrape_website(url, timeout=60):
    @browser(cache=True, parallel=20, reuse_driver=True, data=[url], close_on_crash=True)
    def scrape_website_task(driver: AntiDetectDriver, data):
        url = validate_url(data)
        returnObj = {}
        driver.google_get(url)
        innerHtml = driver.bs4()
        allLinks = extract_urls_from_html(innerHtml)
        socialUrls = ["facebook.com/",  "twitter.com/", "linkedin.com/", "instagram.com/", "youtube.com/"]
        socials = [link for link in allLinks if any(socialUrl in link for socialUrl in socialUrls)]
        returnObj["socials"] = socials
        allLinks = [link for link in allLinks if not any(socialUrl in link for socialUrl in socialUrls)]
        allLinks = [link.split("#")[0] for link in allLinks]
        parsed_url = urlparse(url)
        base = parsed_url.netloc

        internal_urls = []
        linksSet = list(set(allLinks))
        print(linksSet)
        if linksSet is not None:
            for link in linksSet:
                # Join relative URLs to the base URL
                link = urljoin(url, link)
                parsed_link = urlparse(link)
                link_base = parsed_link.netloc
                
                # Check if the link belongs to the same domain
                if link_base == base:
                    internal_urls.append(link)
        whole = driver.text("html")
        returnObj[url] = whole
        # Remove duplicates
        internal_urls = list(set(internal_urls))
        
        internal_urls = extractRelevantNestedLinks(internal_urls)
        print(internal_urls)
        if len(internal_urls)>1:
            returnObj["internal"] = {}
            for url in internal_urls:
                # if url contains the base url redirect to the url else append the base url to the url
                driver.get(url=url)
                returnObj["internal"][url] = driver.text("html")
        return returnObj
    try:
        return scrape_website_task(url)
    except:
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