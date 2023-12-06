from botasaurus import *
@browser(cache=True, 
         parallel=20,
         reuse_driver=True)
def scrape_website_task(driver: AntiDetectDriver, url):
    url = validate_url(url)
    # Navigate to the Omkar Cloud website
    driver.get(url)
    
    # Retrieve the heading element's text
    whole = driver.text("html")
    # Save the data as a JSON file in output/scrape_heading_task.json
    return {
        url: whole
    }

def validate_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return "http://" + url
