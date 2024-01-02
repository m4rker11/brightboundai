from botasaurus import *
@browser(cache=True, 
         parallel=20,
         reuse_driver=True)
def scrape_website_task(driver: AntiDetectDriver, url):
    url = validate_url(url)
    exists = driver.exists(url)
    if exists:
        whole = driver.get_element_text("html")
        print(whole)
        return {
            url: whole
        }
    else:
        return None


def validate_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return "http://" + url

