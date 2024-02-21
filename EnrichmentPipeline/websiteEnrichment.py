from scraper.scraper import scrape_website
from services_and_db.leads.leadService import get_unenriched_leads, updateLead
import difflib
from ..AI.summarize import summarizeWebsiteContent

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
    
def isBtoB(icp):
    ICP_keywords = [
    "business", "industry", "enterprise", 
    "corporate", "decision-makers", "procurement", 
    "stakeholders", "partnerships", "operations", 
    "solutions", "supply chain", "integration", 
    "volume", "commercial", "wholesale",
    ]
    lowercased_icp = icp.lower()
    #check if the icp contains any of the keywords
    for keyword in ICP_keywords:
        if keyword in lowercased_icp:
            return True
    return False

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
    
    # Await the summarizeWebsiteContent function to ensure it completes before proceeding
    try:
        website_summary = summarizeWebsiteContent(website_content, context[row['client_id']])
    except:
        RuntimeError(f"Summarization of {row['company']} failed")
    if website_summary is None:
        RuntimeError(f"Website summary of {row['company']} is none")
    row['website_summary'] = website_summary['summary']
    row['icp'] = website_summary['icp']
    row['offer'] = website_summary['offer']
    if not isBtoB(website_summary['icp']):
        print(f"Website {row['company']} is not B2B")
        RuntimeError(f"Website {row['company']} is not B2B")
        
    return row

