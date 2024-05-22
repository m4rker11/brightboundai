from scraper.scraper import scrape_website
import difflib
from AI.summarize import summarizeWebsiteHomepage, summarizeWebsitePersonal, summarizeWebsiteTeam, summarizeWebsiteServices, summarizeBlog, summarizeWebsiteReviews

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
    website_content = scrape_website(bestUrl, row['company'])
    if website_content is None:
        RuntimeError(f"Website content of {row['company']} is none")
    if website_content.get('socials', None) is not None:
        socials = website_content.pop('socials', None)
        row['socials'] = socials
    row["website_content"] = website_content
    parts = get_website_content(website_content)
    #summarize home page: 
    try:
        if len(str(parts['homepage'])) > 10:
            # Print the homepage content length to verify the condition
            print("Homepage content length:", len(str(parts['homepage'])))
            
            website_summary = summarizeWebsiteHomepage(parts['homepage'], context[row['client_id']]['summary'], context[row['client_id']]['industry'])
            
            # Print the output of summarizeWebsiteHomepage to check its structure
            print("Website summary:", website_summary)
            row['website_summary'] = {}
            row['website_summary']['summary'] = website_summary['summary']
            row['website_summary']['icp'] = website_summary['icp']
            row['website_summary']['offer'] = website_summary['offer']
        if len(str(parts['personal']))>10:
            personal_summary = summarizeWebsitePersonal(parts['personal'], row['company'])
            row['website_summary']['personal'] = personal_summary
        if len(str(parts['team']))>10:
            team_summary = summarizeWebsiteTeam(parts['team'], row['company'])
            row['website_summary']['team'] = team_summary
        if len(str(parts['services']))>10:
            services_summary = summarizeWebsiteServices(parts['services'], row['company'])
            row['website_summary']['services'] = services_summary
        if len(str(parts['reviews']))>10:
            reviews_summary = summarizeWebsiteReviews(parts['reviews'], row['company'])
            row['website_summary']['reviews'] = reviews_summary

        if len(str(parts['blog']))>10:
            blog = summarizeBlog(parts['blog'],row['company'])
            row['website_summary']['blog'] = blog
    except Exception as e:
        print("An error occurred enriching lead: ", row['_id'], " error: ", str(e))
    return row

def get_website_content(website_content):
    structure = {
        "homepage": website_content.get('home', None),
        "personal": [website_content['internal'].get('about_us', None), website_content['internal'].get('founder_story', None), website_content['internal'].get('mission', None), website_content['internal'].get('sustainability', None)],
        "team": [website_content['internal'].get('team', None), website_content['internal'].get('leadership', None), website_content['internal'].get('partnerships', None)],
        "services": [ website_content['internal'].get('services', None)],
        "reviews": [website_content['internal'].get('testimonials', None)],
        "blog": website_content['internal'].get('blog', None)
    }
    return structure