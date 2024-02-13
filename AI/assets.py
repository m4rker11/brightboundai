# we have two types of assets in cold email: collaterals and case studies
# collaterals need to be turned into short sentences that peak the interest of the reader
# case studies need to be condensed into one or two sentences summarizing the ROI of the case study
import fitz
import docx
import csv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.schema.output_parser import StrOutputParser
def handle_file_reading_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            return "Error: The file was not found."
        except PermissionError:
            return "Error: Permission denied. Please check your access rights for this file."
        except Exception as e:
            return f"An error occurred: {str(e)}"
    return wrapper


def add_asset(type, asset, asset_format, client_id, selector = None):
    # depending on asset format we need to extract different things.
    # the options are: pdf, doc, csv
    asset_data = {}
    if asset_format == "pdf":
        asset_data["text"] = extract_pdf_content(asset)
    elif asset_format == "doc":
        asset_data["text"] = extract_docx_content(asset)
    else:
        Exception("Error: The asset format is not supported.")
    # now we need to parse the data into a more useful format.
    if type == "collateral":
        # we need to turn the text into a short sentence that peaks the interest of the reader
        # this is a placeholder
        asset_data["summary"] = "This is a placeholder for the summary of the asset"

    elif type == "case_study":
        # we need to condense the case study into one or two sentences summarizing the ROI of the case study
        # this is a placeholder
        asset_data["summary"] = "This is a placeholder for the summary of the case study"
    else:
        Exception("Error: The asset type is not supported.")

    # now we need to turn this into an angle that is useful for the client
    asset_data['client_id'] = client_id
    asset_data['angle'] = "This is a placeholder for the angle of the asset"
    asset_data['relevance'] = "This is a placeholder for the relevance of the asset"
    asset_data['embedding'] = OpenAIEmbeddings().embed_query(asset_data['relevance'])


"""
def summarizeProfileData(profile):
    prompt_template = ""

    {text}

    ---

    This is the linkedin profile of a potential prospect, summarise this person's profile and posts. 
    Focus on recent events, accomplishments or specifics, and highlight 3 of them in the summary. 
    This will be used for personalizing a cold email.
    Use no more than 200 words.
    Your output should be a json with two fields: "profile summary" and "posts summary".
    If either is missing, return "Not applicable" for that field.
    CONCISE SUMMARY JSON:""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model="gpt-3.5-turbo-1106")
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser"""


def summarizeCollateral(text, client):

    prompt_template = """
    COLLATERAL:
    {text}
    ---
    The above is a piece of content from my client {client_name}.
    Their target audience is ##{target_audience}##.
    Their main value proposition is ##{value_proposition}##.
    Summarize this collateral in no more than 200 words. 
    This summary should be highly relevant to the target audience.
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    model = ChatOpenAI(model="gpt-3.5-turbo-1106")
    output_parser = StrOutputParser()

    chain = prompt | model | output_parser
    return chain({"text": text, "client_name": client.name, "target_audience": client.target_audience, "value_proposition": client.value_proposition})




    




@handle_file_reading_exceptions
def extract_docx_content(docx_path):
    # Load the .docx file
    document = docx.Document(docx_path)
    
    # Initialize an empty list to hold paragraphs of text
    paragraphs = []
    
    # Loop through each paragraph in the document
    for para in document.paragraphs:
        # Append the text of each paragraph to the list
        paragraphs.append(para.text)
    
    # Combine the list of paragraphs into a single string
    # Each paragraph is separated by a newline character
    text_content = '\n'.join(paragraphs)
    
    # Return the combined text
    return text_content

@handle_file_reading_exceptions
def extract_pdf_content(pdf_path):
    # Open the provided PDF file
    document = fitz.open(pdf_path)
    
    # Initialize an empty string for text content
    text_content = ''
    
    # Loop through each page in the PDF
    for page_num in range(len(document)):
        # Get the page
        page = document.load_page(page_num)
        
        # Extract text from the page
        text_content += page.get_text()
    
    # Close the document
    document.close()
    
    # Return the extracted text
    return text_content



@handle_file_reading_exceptions
def extract_csv_content(csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        case_studies = [row for row in reader]
    return case_studies
