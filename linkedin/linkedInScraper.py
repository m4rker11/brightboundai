from linkedin_scraper import Person, actions
from botasaurus import *
from bson.objectid import ObjectId
import random
import AI.summarize as summarizer
import services_and_db.leads.leadService as leadService
email = "theZarutin@gmail.com"
password = "M4rker2021"

people = leadService.get_leads_for_linkedin_enrichment()
people = [{"linkedIn_url": person['linkedIn_url'], "id": str(person['_id'])} for person in people]
print(people)


@browser(cache=False, parallel=1, reuse_driver=True, data=[people])
def scrapePeople(driver: AntiDetectDriver, data):
    # print("Data: ", data)
    actions.login(driver, email, password) # if email and password isnt given, it'll prompt in terminal
    for person in data:
        id = person['id']
        # print(person)
        try:
            person = Person(person['linkedIn_url'], driver=driver, close_on_complete=False)
            person.scrape(close_on_complete=False)
            driver.sleep(random.randint(3, 15))
            distance = random.randint(1000,10000)
            driver.execute_script(f"window.scrollTo(0, {distance})")
            driver.sleep(random.randint(5, 10))
            if (not person.about==None and not len(person.about)<10):
                summary = summarizer.summarizeProfileData({"profile": person.about, 
                                            "accomplishments": person.accomplishments, 
                                            "interests": person.interests})
            else:
                summary = "No summary available"
            # print(summary)
            # person['linkedin_summary'] = summary
            leadService.update_field_in_lead_by_id(id, "linkedin_summary", summary)
        except:
            print("Error scraping person")
            pass
    return person



