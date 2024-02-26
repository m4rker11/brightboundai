import requests
from proxycurl.asyncio import Proxycurl
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv('PROXYCURL_API_KEY')
proxycurl = Proxycurl(api_key=api_key)
async def getLinkedInProxyCurl(url):
    # Fetch the person's profile
    profile_data = await proxycurl.linkedin.person.get(linkedin_profile_url=url)
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

    return result

def process_linkedin_profile(linkedin_profile):
    # Extracting and formatting the first three experiences
    try:
        experiences = [
            {
                'description': experience['description'],
                'company': experience['company'],
                'date_range': experience['date_range'],
                'title': experience['title']
            }
            for experience in linkedin_profile['data']['experiences'][:3] if len(linkedin_profile['data']['experiences']) > 0
        ]
    except:
        return linkedin_profile
    # Returning the 'about' information and formatted experiences
    return {
        'about': linkedin_profile['data']['about'],
        'experiences': experiences
    }

def process_linkedin_data(linkedin_posts, linkedin_about):
    # Filtering the list
    try:
        filtered_list = [
            json for json in linkedin_posts['response_body']['data']
            if json.get('reshared') and json.get('resharer_comment') and len(json['resharer_comment']) > 10
        ]
    except:
        filtered_list = []

    # Extracting and formatting the required information
    result_list = [
        {
            'text': json['text'],
            'resharer_comment': json.get('resharer_comment', '')
        }
        for json in filtered_list[:7] if len(filtered_list) > 0
    ]

    # Returning the formatted data
    return {
        'profile': linkedin_about,
        'posts': result_list
    }

# def getLinkedInInfo(url):
#     # Fetching the LinkedIn profile data
#     linkedin_profile = getLinkedInProfile(url)
#     if linkedin_profile == "Error: Unable to fetch LinkedIn profile data":
#         return None
#     processed_profile = process_linkedin_profile(linkedin_profile)
#     linkedin_posts = getProfilePosts(url)
#     # Extracting the required information from the response
#     linkedin_data = process_linkedin_data(linkedin_posts, processed_profile)

#     # Returning the extracted data
#     return linkedin_data