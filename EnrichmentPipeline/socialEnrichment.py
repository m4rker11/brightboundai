from ..linkedin.getLinkedInInfo import getLinkedInProxyCurl
from ..services_and_db.leads.leadService import get_leads_for_linkedin_enrichment, updateLead
from ..AI.summarize import summarizeProfileData
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
async def process_linkedin_profiles(profiles_to_process):
    
    for profile in profiles_to_process:
        url = profile.get('linkedin_url')
        print(url)
        if url:
            profile_info = await getLinkedInProxyCurl(url)
            profile['linkedInPage'] = profile_info
            profile['linkedInSummary'] = summarizeProfileData(profile_info)
            updateLead(profile)