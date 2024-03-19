
"""
lead_schema = {
    'full_name': str, both
    'first_name': str, both
    'company': str, both
    'website_url': str, neither
    'linkedIn_url': str, neither
    'email': str, csv
    'icp': str, emailWriter
    'offer': str, emailWriter
    'city': str, emailWriter
    'job_title': str, emailWriter
    'keywords': list, emailWriter
    'industry': str, emailWriter
    'company_country': str, emailWriter
    'company_state': str, emailWriter
    'company_linkedin_url': str,
    'employees': int, emailWriter
    'offer_specific': bool, 
    'website_summary': str, emailWriter
    'linkedin_summary': str, emailWriter
    'lead_valid': bool,
    'lead_status': str, 
    'email_fields': dict, CSV
    'created': str,
    'last_updated': str,
    'contacted': str,
    'campaign_context':dict, 
    'campaign_id': ObjectId,
    'ignore': bool,
    'client_id': ObjectId,
}"""
def leadForCSV(lead) -> dict:
    # Initialize the return object with fields marked both or CSV
    if lead.get('campaign_context', None) is not None:
        personalization = lead['campaign_context'].get('personalization', None)
    result = {
        "full_name": lead.get('full_name', ''),
        "first_name": lead.get('first_name', ''),
        "company": lead.get('company', ''),
        "email": lead.get('email', ''),
        "website_url": lead.get('website_url', ''),
        "linkedIn_url": lead.get('linkedIn_url', ''),
        "personalization": personalization,
    }

    # Check if 'email_fields' exists and is a dictionary, then add its key-value pairs to the result
    if 'email_fields' in lead and isinstance(lead['email_fields'], dict):
        for key, value in lead['email_fields'].items():
            result[key] = value

    return result


def leadForEmailWriter(lead) -> dict:
    # Use the get method with a default value for each key
    return {
        "first_name": lead.get('first_name', ''),
        "full_name": lead.get('full_name', ''),
        "company": lead.get('company', ''),
        "icp": lead.get('icp', ''),
        "offer": lead.get('offer', ''),
        "city": lead.get('city', ''),
        "job_title": lead.get('job_title', ''),
        "keywords": lead.get('keywords', ''),
        "industry": lead.get('industry', ''),
        "company_country": lead.get('company_country', ''),
        "company_state": lead.get('company_state', ''),
        "website_summary": lead.get('website_summary', ''),
        "linkedin_summary": lead.get('linkedin_summary', ''),
        "employees": lead.get('employees', '')
    }
