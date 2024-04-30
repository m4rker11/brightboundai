from botasaurus import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import os

username = os.getenv("WIZA_USERNAME")
password = os.getenv("WIZA_PASSWORD")
def get_list_id(client_name, list_name):
    datatask = {"client_name": client_name, "list_name":list_name}
    
    @browser(cache=False, data=datatask)
    def scrape_website_task(driver: AntiDetectDriver, data):
        driver.google_get("https://wiza.co/app/dashboard")
        # put username

        wait(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/button")
        type(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/div/div/input",username)
        click(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/button")
        #put password
        wait(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/button")
        wait(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/div[2]/div/input")
        type(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/div[2]/div/input", password)
        #click login
        click(driver,"/html/body/div[1]/div[2]/div/div/div[3]/form/button")


        #go to lists /html/body/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[1]
        wait_and_click(driver,"/html/body/div[1]/div[2]/div[1]/div/div[1]/div[2]/a[1]")

        wait_and_click(driver,"/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[1]/div[1]/div")
        driver.prompt("Navigate to the right list")
        report_id = driver.current_url.split("report_id=")[1].split("&")[0]
        return report_id

    return scrape_website_task()

def wait(driver,xpath):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
def type(driver,xpath,text):
    driver.find_element(by= By.XPATH, value=xpath).send_keys(text)
def click(driver,xpath):
    driver.find_element(by= By.XPATH, value=xpath).click()
def find(driver,xpath):
    return driver.find_element(by= By.XPATH, value=xpath)
def wait_and_click(driver,xpath):
    wait(driver,xpath)
    click(driver,xpath)