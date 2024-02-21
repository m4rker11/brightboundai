from linkedin.getLinkedInInfo import getLinkedInProxyCurl
from services_and_db.leads.leadService import updateLead
from AI.summarize import summarizeProfileData
def process_linkedin_profile(profile):

    url = profile.get('linkedin_url')
    print(url)
    if url:
        profile_info = getLinkedInProxyCurl(url)
        print(profile_info)
        profile['linkedInPage'] = profile_info
        profile['linkedInSummary'] = summarizeProfileData(profile_info)
        updateLead(profile)