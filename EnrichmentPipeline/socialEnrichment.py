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
            

def batchEnrichLinkedinProfiles(profiles, progress_bar, status_text, batch_size=5):
    total_profiles = len(profiles)
    for start_index in range(0, total_profiles, batch_size):
        end_index = min(start_index + batch_size, total_profiles)
        batch = profiles[start_index:end_index]
        with asyncio.TaskGroup() as tg:
            for profile in batch:
                tg.create(process_linkedin_profiles(profile))
            asyncio.run(tg)
        progress = end_index / total_profiles
        progress_bar.progress(progress)
        status_text.text(f"Processed profiles {start_index + 1} to {end_index} of {total_profiles}")