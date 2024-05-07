from botasaurus import *
from botasaurus.create_stealth_driver import create_stealth_driver
from AI.summarize import extractInterestingNestedLinks, verify_website
from urllib.parse import urlparse, urljoin
import re
def scrape_website(url, industry, company_name):
    @browser(cache=False, max_retry=5, window_size=bt.WindowSize.REAL,
             create_driver=create_stealth_driver(start_url="google.com",raise_exception=True),
             parallel=20, reuse_driver=True, data=[url], close_on_crash=True, headless=True)
    def scrape_website_task(driver: AntiDetectDriver, data):
        url = validate_url(data)
        returnObj = {}
        driver.google_get(url)
        innerHtml = driver.bs4()
        if not verify_website_correct(innerHtml, company_name, industry):
            return None
        returnObj["emails"] = find_emails(innerHtml)
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
        internal_urls = filter_urls(internal_urls)

        whole = extract_text_from_soup(innerHtml)
        returnObj["home"] = whole
        interesting_urls = extractInterestingNestedLinks(internal_urls)
        returnObj["internal"] = {} 
        for key, value in interesting_urls.items():
            if value is not None and key != "cookie_policy" and key != "privacy_policy" and key != "terms_of_service":
                driver.get(url=value)
                if driver.is_bot_detected():
                    return returnObj
                returnObj["internal"][key] = extract_text_from_soup(driver.bs4())
                returnObj['emails'] += find_emails(driver.bs4())
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
    
def filter_urls(urls):
    filters = ['privacy', 'policy', 'terms', 'conditions', 'cookies', 'legal', 'disclaimer', 'contact', 'faq', 'frequently','asked','questions', 'help', 'site','sitemap', 'accessibility']
    filtered_urls = [url for url in urls if not any(filter in url for filter in filters)]
    return filtered_urls

def verify_website_correct(bs4_content, company_name, industry):
    return verify_website(company_name, industry, bs4_content)


def find_emails(bs4_content):
    # Compile a regular expression for finding emails
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    # Set to hold unique emails
    emails = set()

    # Check each element's string content
    for element in bs4_content.find_all(text=True):
        potential_emails = re.findall(email_pattern, element)
        emails.update(potential_emails)

    # Additionally, check each 'href' attribute for 'mailto' links
    for a_tag in bs4_content.find_all('a', href=True):
        href = a_tag['href']
        if 'mailto:' in href:
            email = href.split('mailto:')[1]
            if re.match(email_pattern, email):
                emails.add(email)

    return list(emails)