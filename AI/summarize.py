import dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.output_parsers.boolean import BooleanOutputParser 
from langchain.schema.output_parser import StrOutputParser
from .base import invoke_chain
dotenv.load_dotenv()
def summarizeProfileData(profile):
    prompt_template = """

    {text}

    ---

    This is the linkedin profile of a potential prospect, summarise this person's profile. 
    Use no more than 200 words and use the appropriate amount depending on the size of the linkedin profile above.
    In addition to the summary, provide interesting personal details or observations that can be used to personalize a cold email.
    These details can be about a post they made, article they wrote, personal story, drastic career change, polarizing opinion, or something else unique or relatable. 
    add an additional field "interestings" with a list of 3 interesting items which highlight 3 details from the above.
    RESPONSE:"""
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"text": profile})

def summarizeWebsiteHomepage(content, context, field_of_interest):
        
        formatString1 = str({
        "summary": "targeted summary relevant to the services I offer",
        "icp": "Their ideal customer profile",
        "offer": "the services they are offering to the ICP"
        })
        
        prompt_template1 = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information above provide me the following:
    
        1. Give me a 150-word summary of the above website content. Focus on the potential challenges and opportunities this company might face in relation to {field}.
    
        2. Give me a 30 word summary of the ideal customer profile that you infer from the website content. This ICP summary needs to start with either the word "Businesses" if the company is B2B or "Individuals" if the company is B2C. 
    
        3. Give me a 30 word summary of their offer to their ICP and the services they provide them.
    
        CONTEXT ABOUT MY SERVICES:
    
        {product_context}
    
        Your response MUST be in the following json format, return just the json:
    
        {format}
    
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template1, "json", {"website_content": content, "product_context": context, "format": formatString1, "field": field_of_interest})

def summarizeWebsitePersonal(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information answer the following questions about {company_name}:
        1. What language and tone are used to describe the company?
        2. What are the main points emphasized about the company’s identity and goals?
        3. What motivated the founder to start the company?
        4. Are there personal anecdotes or challenges mentioned that shaped the company’s journey?
        5. What specific goals does the company aim to achieve?
        6. How does the company differentiate itself from its competitors?
        7. What are the key initiatives or commitments made by the company regarding sustainability?
        8. How does the company measure or report on its sustainability efforts?
    
        Rules:
        Do not include the questions in the response.
        Do not make things up, only answer based on the information provided.
        Aim to use no more than 30 words per question.
        If the information to answer a question is not present, ignore the question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeWebsiteTeam(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information answer the following questions about {company_name}:
        
        1. Who makes up the broader team?
        2. What expertise does the team collectively hold?
        3. Are there any recurring themes or values evident in team bios?
        4. What are the backgrounds of the leadership team members?
        5. What personal insights can you gather about the CEO?
        6.What leadership style is portrayed?
        7. Who are the company’s partners?
        8. What nature of partnerships do they engage in?
        9. What might these partnerships indicate about the company’s values or future directions?
    
        Rules:
        Do not include the questions in the response.
        Do not make things up, only answer based on the information provided.
        Aim to use no more than 30 words per question.
        If the information to answer a question is not present, ignore the question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeWebsiteServices(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information answer the following questions about {company_name}:
        
        1. What specific services does the company offer?
        2. How are these services unique in their market?
        3. What problems do these services solve for their clients?
        4. How does the company describe the benefits of their services?
        5. Who is the ideal client for these services?
        6. Who are the clients providing testimonials?
        7. What specific aspects of the services are highlighted in the testimonials?
        8. How do clients describe their experience with the company?
        9. Are there recurring themes or keywords in the testimonials?
        10. How does the company showcase these testimonials?
    
        Rules:
        Do not include the questions in the response.
        Do not make things up, only answer based on the information provided.
        Aim to use no more than 30 words per question.
        If the information to answer a question is not present, ignore the question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeBlog(content, company_name):
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        The above is the latest blogs from {company_name}:
        
        1. What topics are most frequently discussed in the blog?
        2. Who are the authors of the blog posts?
        3. How does the company engage with its readers and community through the blog?
        4. Are there recent posts about major achievements or milestones?
        5. What challenges or industry trends are they discussing?
    
        Rules:
        Do not include the questions in the response.
        Do not make things up, only answer based on the information provided.
        Aim to use no more than 30 words per question.
        If the information to answer a question is not present, ignore the question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})


def extractInterestingNestedLinks(allLinks):
    returnStructure = {
        "cookie_policy",
        "privacy_policy",
        "terms_of_service",
        "about_us",
        "founder_story",
        "mission",
        "team",
        "testimonials",
        "services",
        "leadership",
        "blog",
        "partnerships",
        "sustainability"
    }
    prompt_template = """
    INTERNAL LINKS:
    {internal_links}
    -----
    Above is the set of all internal links found on the website. 
    Based on the urls above return an object with the following structure:
    {return_structure}
    The value for each of the keys should be the most likely url that contains the information for that key.
    Do not output the same link twice.
    If no relevant link is found for a key, do not include the key value pair in the response.
    Only output the json.
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "json", {"internal_links": allLinks, "return_structure": returnStructure})

def verify_website(company_name, industry, bs4_content):
    prompt_template = """
    WEBSITE CONTENT:
    {website_content}
    -----
    Based on the information above, verify if the website belongs to {company_name} in the {industry} industry.
    
    If the website belongs to the company and actively represents the industry, return True.
    If the website suggests a captcha, maintenance, placeholder, being for sale, or any other indication that the website is not actively representing the company or industry, return False.
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "bool", {"website_content": bs4_content, "company_name": company_name, "industry": industry})


def summarizePersonalizationData(pd, template):
    #extract fields from the template that will require personalization.
    request = template.get('data_request', "Give me a summary of their current role, job title, company, services, and accomplishments if any.")

    prompt_template = """
    PERSONALIZATION DATA:
    {personalization_data}
    -----
    Extract the most relevant information from the personalization data to tailor a cold email campaign. 
    Focus on details that align with the criteria outlined in the request below.
    RELEVANT REQUEST:
    {request}
    -----
    Rules:
    Output the extracted information in the exact wording as it appears in the personalization data.
    Output should be no more than 150 words.
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"personalization_data": pd, "request": request})