import dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers.boolean import BooleanOutputParser 
from langchain.schema.output_parser import StrOutputParser
from .base import invoke_chain
import os
dotenv.load_dotenv()
def summarizeProfileData(profile):
    output_format = {
        "summary": "Summary of the LinkedIn profile",
        "interestings": ["Detail 1", "Detail 2", "Detail 3"]
        }
    prompt_template = """

    {text}

    ---

    Analyze the provided LinkedIn profile of a potential prospect and create a summary of no more than 200 words. 
    The length of the summary should be appropriate to the amount of content in the profile.
    In addition to the summary, identify and list three interesting personal details or observations that can be used to personalize a cold email. 
    These details could be related to posts they made, articles they wrote, personal stories, career changes, polarizing opinions, or any other unique or relatable aspects.
    Your response must be a valid json with double quotes around the keys and values and be in the following format.
    OUTPUT FORMAT:
    {format}
    
    RESPONSE:"""

    return invoke_chain("gpt-3.5", 0.2, prompt_template, "json", {"text": profile, "format": output_format})

    
def summarizeWebsiteHomepage(content, context, field_of_interest):
        
        formatString1 = {
        "summary": "website summary",
        "icp": "Their ideal customer profile",
        "offer": "the services they are offering to the ICP",
        "challenges": f"potential challenges and opportunities in relation to {field_of_interest}"
        }
        
        prompt_template1 = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information above provide me the following:
    
        1. Give me a 150-word summary of the above website content..
    
        2. Give me a 30 word summary of the ideal customer profile that you infer from the website content. This ICP summary needs to start with either the word "Businesses" if the company is B2B or "Individuals" if the company is B2C. 
    
        3. Give me a 30 word summary of their offer to their ICP and the services they provide them.
    
        4. Provide a 30 word summary of potential challenges and opportunities.
        
        CONTEXT ABOUT MY SERVICES:
    
        {product_context}
    
        Your response MUST be in the following json format, return just the json with double quotes around the keys and values:
    
        {format}
    
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template1, "json", {"website_content": content, "product_context": context, "format": formatString1})

def summarizeWebsitePersonal(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information provided, summarize the following aspects of {company_name} in one paragraph:
        1. Language and tone used to describe the company.
        2. The company's core identity and primary goals.
        3. Founder’s motivation for starting the company.
        4. Personal anecdotes or challenges that shaped the company’s journey.
        5. How the company differentiates itself from competitors.
        6. Key initiatives or commitments regarding sustainability.
        7. How the company measures or reports on its successes.

        Rules:
        - Do not include the questions in the response.
        - If specific information is missing to answer a question, Do NOT respond to that question.
        - Answer the questions by quoting information from the content; do not make up any details.
        - Limit the response to a maximum of 30 words per question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeWebsiteTeam(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information provided, summarize the following aspects of {company_name} in one paragraph:
        
        1. Composition of the broader team.
        2. Collective expertise of the team.
        3. Recurring themes or values in team bios.
        4. Backgrounds of leadership team members.
        5. Personal insights about the CEO.
        6. Portrayed leadership style.
        7. Key partners of the company.
        8. Nature of partnerships.
        9. What the partnerships indicate about the company’s values or future directions.
    
        Rules:
        - Do not include the questions in the response.
        - If specific information is missing to answer a question, Do NOT respond to that question.
        - Answer the questions by quoting information from the content; do not make up any details.
        - Limit the response to a maximum of 30 words per question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeWebsiteServices(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information provided, summarize the following aspects of {company_name} in one paragraph:
        
        1. The specific services the company offers.
        2. How these services are unique in their market.
        3. The problems these services solve for clients.
        4. The benefits of the services as described by the company.
        5. The ideal client for these services.
    
        Rules:
        - Do not include the questions in the response.
        - If specific information is missing to answer a question, Do NOT respond to that question.
        - Answer the questions by quoting information from the content; do not make up any details.
        - Limit the response to a maximum of 30 words per question.
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeWebsiteReviews(content, company_name):
        
        
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information provided, summarize the following aspects of {company_name} in one paragraph:

        1. The clients providing testimonials.
        2. Services highlighted in the testimonials.
        3. How clients describe their experience with the company.
        4. Recurring themes or keywords in the testimonials.
    
        Rules:
        - Do NOT include the questions in the response.
        - If specific information is missing to answer a question, Do NOT respond to that question.
        - Answer the questions by quoting information from the content; do not make up any details.
        - Limit the response to a maximum of 30 words per question.
        
        RESPONSE:"""
        return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"website_content": content, "company_name": company_name})

def summarizeBlog(content, company_name):
        prompt_template = """
        WEBSITE CONTENT:
        {website_content}
    
        Based on the information provided, summarize the following aspects of {company_name} in one paragraph:
        
        1. Most frequently discussed topics in the blog.
        2. The authors of the blog posts.
        3. How the company engages with its readers and community through the blog.
        4. Recent posts about major achievements or milestones.
        5. Challenges or industry trends being discussed.
    
        Rules:
        - If specific information  is missing for a question, skip it.
        - Do not include the questions in the response.
        - Answer the questions by quoting information from the content; do not make up any details.
        - Limit the response to a maximum of 30 words per question.
        
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
    The list above contains all internal links found on the website. 
    Create a JSON object with the following structure:
    {return_structure}
    Each key should have the URL that most likely contains the corresponding information.
    Ensure no URL is repeated.
    If a relevant URL is not found for a key, DO NOT include the key value pair in the output.
    Provide only the JSON object in the output with double quotes around the keys and values.
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "json", {"internal_links": allLinks, "return_structure": returnStructure})

def verify_website(company_name, bs4_content):
    prompt_template = """
    WEBSITE CONTENT:
    {website_content}
    -----
    Based on the information provided, determine if the website belongs to {company_name}.
    
    Return YES if the website actively represents the company.
    Return NO if the website shows signs of maintenance, placeholder content, under construction, being for sale, or any indication that it is not actively representing the company.
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "bool", {"website_content": bs4_content, "company_name": company_name})


def summarizePersonalizationData(pd, template):
    #extract fields from the template that will require personalization.
    request = template.get('data_request', "Provide a summary of their current role, job title, company, services, Ideal Customer Profile, and any accomplishments.")
 
    prompt_template = """
    PERSONALIZATION DATA:
    {personalization_data}
    -----
    Extract the most relevant information from the personalization data.
    Focus on details that align with the criteria outlined in the request below.
    RELEVANT REQUEST:
    {request}
    -----
    Rules:
    - Output the extracted information in the exact wording as it appears in the personalization data.
    - Do not include any information that is not explicitly mentioned in the personalization data.
    - Output should be no more than 250 words.
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.2, prompt_template, "str", {"personalization_data": pd, "request": request})


def inferFinancialGoals(pd):
    prompt_template = """
    PERSONALIZATION DATA:
    {personalization_data}
    -----
    Based on the personalization data provided, infer the financial goals of the prospect.
    Here is a list of potential financial goals:
    [
        "Revenue Growth",
        "Profitability",
        "Cash Flow Management",
        "Budget Adherence",
        "Expense Reduction",
        "Debt Management",
        "Investment Strategy",
        "Tax Optimization",
        "Financial Reporting Accuracy",
        "Risk Management",
        "Capital Allocation",
        "Compliance and Audits",
        "Liquidity Management",
        "Inventory Management",
        "Cost of Goods Sold (COGS) Optimization",
        "Gross Margin Improvement",
        "Operational Efficiency",
        "Long-term Financial Planning",
        "Shareholder Value",
        "Benchmarking and KPIs"
    ]
    Provide 2-3 most likely financial goals based on the personalization data.
    Your output should be in the form:
    "As a niche description, the company X is likely focused on Y and Z."
    RESPONSE:
    """
    return invoke_chain("gpt-3.5", 0.3, prompt_template, "str", {"personalization_data": pd})