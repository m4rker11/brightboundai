import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import time

#FOR LATER USE



def validated(email, name, website):
    # Implement validation logic here
    # Return True if validated, else False
    pass

def addToMongo(entry):
    # MongoDB connection and insertion logic here
    pass

def find_email_address(page_source):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, page_source)

def filter_emails(emails, excluded_domain):
    filtered = [email for email in emails if not email.endswith(excluded_domain)]
    return filtered[:2]

def split_name(name):
    parts = name.split()
    first_name = parts[0] if parts else ''
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return first_name, last_name


def scrape_and_save_leads(user_data_dir, chrome_driver_path, apollo_link):
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(apollo_link)

    time.sleep(2)

    # Rest of the helper functions like find_email_address, filter_emails, split_name go here

    while True:
        try:
            loaded_section_selector = "[data-cy-loaded='true']"
            loaded_section = driver.find_element(By.CSS_SELECTOR, loaded_section_selector)

            tbodies = loaded_section.find_elements(By.TAG_NAME, 'tbody')
            if not tbodies:
                break

            for tbody in tbodies:
                first_anchor_text = tbody.find_element(By.TAG_NAME, 'a').text
                first_name, last_name = split_name(first_anchor_text)

                linkedin_url = ''
                for link in tbody.find_elements(By.TAG_NAME, 'a'):
                    href = link.get_attribute('href')
                    if 'linkedin.com' in href:
                        linkedin_url = href
                        break

                job_title_element = tbody.find_element(By.CLASS_NAME, 'zp_Y6y8d')
                job_title = job_title_element.text if job_title_element else ''

                company_name = ''
                for link in tbody.find_elements(By.TAG_NAME, 'a'):
                    if 'accounts' in link.get_attribute('href'):
                        company_name = link.text
                        break

                phone_number = tbody.find_elements(By.TAG_NAME, 'a')[-1].text

                location = tbody.find_element(By.CLASS_NAME, 'zp_1XZ9r').text

                button_classes = ["zp-button", "zp_zUY3r", "zp_hLUWg", "zp_n9QPr", "zp_B5hnZ", "zp_MCSwB", "zp_IYteB"]
                
                try:
                    button = tbody.find_element(By.CSS_SELECTOR, "." + ".".join(button_classes))
                    if button:
                        button.click()
                        email_addresses = find_email_address(driver.page_source)
                        filtered_emails = filter_emails(email_addresses, 'sentry.io')

                        if len(filtered_emails) > 0 and validated(filtered_emails[0], first_name + " " + last_name, linkedin_url):
                            entry = {
                                "first_name": first_name,
                                "last_name": last_name,
                                "job_title": job_title,
                                "company_name": company_name,
                                "email": filtered_emails[0],
                                "linkedin_url": linkedin_url,
                                "phone_number": phone_number
                            }
                            addToMongo(entry)

                        button.click()
                        tbody_height = driver.execute_script("return arguments[0].offsetHeight;", tbody)
                        driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", loaded_section, tbody_height)
                except NoSuchElementException:
                    continue

            # Pagination Logic
            next_button_selector = ".zp-button.zp_zUY3r.zp_MCSwB.zp_xCVC8[aria-label='right-arrow']"
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
                next_button.click()
                time.sleep(1)
            except NoSuchElementException:
                print("No more pages to navigate.")
                break

        except Exception as e:
            error_message = str(e)
            if "element click intercepted" in error_message:
                print("Your leads are ready!")
                break
            else:
                print(f"An error occurred: {error_message}")
                break

    driver.quit()

# Example usage of the function
user_data_dir = r'C:\Users\YOUR_USERNAME\AppData\Local\Google\Chrome\User Data\Default'
chrome_driver_path = './chromedriver.exe'
apollo_link = "YOUR_APOLLO_IO_LINK"

scrape_and_save_leads(user_data_dir, chrome_driver_path, apollo_link)
