from scraper.scraper import scrape_website
from services_and_db.leads.leadService import get_unenriched_leads, updateLead
import difflib
from AI.summarize import summarizeWebsiteContent, extractInterestingThing, inferServiceInfo

def chooseBestUrl(row):
    # row is a dictionary that may or may not have a website_url and email field
    # we want to return the best url to scrape from

    email = row.get('email', None)
    website_url = row.get('website_url', None)
    company_name = row.get('company', None)  

    emailDomain = email.split('@')[1]
    if not website_url:
        return emailDomain
    elif emailDomain in website_url:
        return website_url
    else:
        return max([website_url, emailDomain], key=lambda x: compute_similarity(x, company_name))

def compute_similarity(input_string, reference_string):
        diff = difflib.ndiff(input_string, reference_string)
        diff_count = 0
        for line in diff:
            if line.startswith("-"):
                diff_count += 1
        return 1 - (diff_count / len(input_string))


def enrichWebsite(row, context):

    # part 1: get the website content
    bestUrl = chooseBestUrl(row)

    website_content = scrape_website(bestUrl)

    if website_content is None:
        RuntimeError(f"Website content of {row['company']} is none")
    socials = website_content.pop('socials', None)
    row["website_content"] = website_content
    if socials is not None:
        row['socials'] = socials

    try:
        website_summary = summarizeWebsiteContent(website_content["home"], 
                                                  context[row['client_id']]['summary'], 
                                                  context[row['client_id']]['industry'])
        interestings = {}
        for key in website_content['internal']:
            if key != "home":
                print(f"Summarizing {key}")
                item = website_content['internal'][key]
                interesting = extractInterestingThing(str(item))
                print(interesting)
                if len(interesting.keys()) == 2:
                    interestings[interesting["interesting_thing"]] = interesting["summary"]
        all_service_info = None
        if website_content['services'] is not None:
            all_service_info = inferServiceInfo(website_content['services'], context[row['client_id']]['industry'])
        
    except:
        print(f"Summarization of {row['company']} failed")
        RuntimeError(f"Summarization of {row['company']} failed")
    if website_summary is None:
        print(f"Website summary of {row['company']} is none")
        RuntimeError(f"Website summary of {row['company']} is none")
    row['website_summary'] = website_summary['summary']
    row['icp'] = website_summary['icp']
    row['offer'] = website_summary['offer']
    row['interestings'] = interestings
    row['selling_points'] = all_service_info
       
    return row

