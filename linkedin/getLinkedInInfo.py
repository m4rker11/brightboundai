import requests

def getLinkedInProfile(url):
    # API endpoint
    api_url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-linkedin-profile?linkedin_url=" + url
    
    # Headers required for the API request
    headers = {
        'X-RapidAPI-Key': "b2df7b458amsh113f4894bb87467p1d7a5fjsnd6d27660796d",
        'X-RapidAPI-Host': "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    # Sending a GET request to the API
    response = requests.get(api_url, headers=headers)

    # Checking if the request was successful
    if response.status_code == 200:
        # Return the JSON response if successful
        return response.json()
    else:
        # Return an error message if the request failed
        return "Error: Unable to fetch LinkedIn profile data"
    
def getProfilePosts(url):
    # API endpoint
    api_url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-profile-posts'?linkedin_url=" + url+"&type=posts"
    
    # Headers required for the API request
    headers = {
        'X-RapidAPI-Key': "b2df7b458amsh113f4894bb87467p1d7a5fjsnd6d27660796d",
        'X-RapidAPI-Host': "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    # Sending a GET request to the API
    response = requests.get(api_url, headers=headers)

    # Checking if the request was successful
    if response.status_code == 200:
        # Return the JSON response if successful
        return response.json()
    else:
        # Return an error message if the request failed
        return "Error: Unable to fetch LinkedIn profile data"
    
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
        print("ERRRRRRRRRRRRRRRROOOOOOOOOOOOOOORRRRRRRR: " + str(linkedin_profile))
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

def getLinkedInInfo(url):
    # Fetching the LinkedIn profile data
    linkedin_profile = getLinkedInProfile(url)
    if linkedin_profile == "Error: Unable to fetch LinkedIn profile data":
        return None
    processed_profile = process_linkedin_profile(linkedin_profile)
    linkedin_posts = getProfilePosts(url)
    # Extracting the required information from the response
    linkedin_data = process_linkedin_data(linkedin_posts, processed_profile)

    # Returning the extracted data
    return linkedin_data