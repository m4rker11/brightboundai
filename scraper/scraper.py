from botasaurus import *
from AI.summarize import extractInterestingNestedLinks, extractServiceNestedLinks
from urllib.parse import urlparse, urljoin

def scrape_website(url):
    @browser(cache=False, parallel=20, reuse_driver=True, data=[url], close_on_crash=True, headless=True)
    def scrape_website_task(driver: AntiDetectDriver, data):
        url = validate_url(data)
        returnObj = {}
        driver.google_get(url)
        innerHtml = driver.bs4()
        allLinks = extract_urls_from_html(innerHtml)
        socialUrls = ["facebook.com/",  "twitter.com/", "linkedin.com/", "instagram.com/", "youtube.com/"]
        socials = list(set([link for link in allLinks if any(socialUrl in link for socialUrl in socialUrls)]))
        returnObj["socials"] = socials
        allLinks = [link for link in allLinks if not any(socialUrl in link for socialUrl in socialUrls)]
        allLinks = [link.split("#")[0] for link in allLinks]
        parsed_url = urlparse(url)
        base = parsed_url.netloc

        internal_urls = []
        linksSet = list(set(allLinks))
        if linksSet is not None:
            for link in linksSet:
                # Join relative URLs to the base URL
                link = urljoin(url, link)
                parsed_link = urlparse(link)
                link_base = parsed_link.netloc
                
                # Check if the link belongs to the same domain
                if link_base == base:
                    internal_urls.append(link)

        whole = extract_text_from_soup(innerHtml)
        returnObj["home"] = whole
        interesting_urls = extractInterestingNestedLinks(internal_urls)
        service_urls = extractServiceNestedLinks(internal_urls)
        if len(interesting_urls)>1:
            returnObj["internal"] = {}
            for url in interesting_urls:
                driver.get(url=url)
                returnObj["internal"][url] = extract_text_from_soup(driver.bs4())
        
        if len(service_urls)>1:
            returnObj["services"] = {}
            for url in service_urls:
                driver.get(url=url)
                returnObj["services"][url] = extract_text_from_soup(driver.bs4())
        return returnObj
    try:
        return scrape_website_task(url)
    except:
        return None


def extract_text_from_soup(soup):
    tags_to_remove = ['a', 'button', 'nav', 'footer', 'script', 'style']

    for tag in tags_to_remove:
        for element in soup.find_all(tag):
            element.decompose()
    text = soup.get_text(separator=' ', strip=True)
    return text


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