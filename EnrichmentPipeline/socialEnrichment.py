import asyncio
from proxycurl.asyncio import Proxycurl
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv(override=True)

# Fetch the API key from environment variables
api_key = os.getenv('PROXYCURL_API_KEY')
abstract_api_key = os.getenv('ABSTRACT_API_KEY')
proxycurl = Proxycurl(api_key=api_key, timeout=30)
def getLinkedInProxyCurl(url):
    print(api_key)

    profile_data = asyncio.run(proxycurl.linkedin.person.get(linkedin_profile_url=str(url)))
    return extract_profile_info(profile_data)

def extract_profile_info(data):
    # Extracting the profile summary
    profile_summary = data.get('summary', '')

    # Extracting the occupation
    occupation = data.get('occupation', '')

    # Extracting the latest 3 experiences
    experiences = data.get('experiences', [])
    latest_three_experiences = experiences[:3] if len(experiences) >= 3 else experiences

    # Extracting activities
    activities = data.get('activities', [])

    # Extracting interests
    interests = data.get('interests', [])

    # Extracting certifications
    certifications = data.get('certifications', [])

    # Consolidating accomplishments
    accomplishments = {
        'organisations': data.get('accomplishment_organisations', []),
        'publications': data.get('accomplishment_publications', []),
        'honors_awards': data.get('accomplishment_honors_awards', []),
        'patents': data.get('accomplishment_patents', []),
        'courses': data.get('accomplishment_courses', []),
        'projects': data.get('accomplishment_projects', []),
        'test_scores': data.get('accomplishment_test_scores', []),
    }

    # Creating a result dictionary
    result = {
        'profile_summary': profile_summary,
        'occupation': occupation,
        'latest_3_experiences': latest_three_experiences,
        'activities': activities,
        'interests': interests,
        'certifications': certifications,
        'accomplishments': accomplishments,
    }
    print("magic")
    return result

def verify_email(email): 
    response = requests.get("https://emailvalidation.abstractapi.com/v1/?api_key="+abstract_api_key+"&email="+email)
    print(response.json())
    return response.json()["deliverability"]=="DELIVERABLE"