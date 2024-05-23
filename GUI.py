import streamlit as st
import pandas as pd
import bson
import streamlit_authenticator as stauth
from services_and_db.leads.LeadObjectConverter import *
from EnrichmentPipeline.enrichmentPipeline import createEmailsForLeadsByTemplate, async_upload_leads, upload_leads, enrichMongoDB
import services_and_db.clients.clientMongo as Clients
import services_and_db.leads.leadService as Leads
import services_and_db.campaigns.campaignMongo as Campaigns
import yaml
from yaml.loader import SafeLoader

with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Streamlit UI
def main():
    authenticator.login()
    if st.session_state["authentication_status"]:
        # authenticator.logout()
        # st.write(f'Welcome *{st.session_state["name"]}*')
        # st.title('Some content')
        page = st.sidebar.selectbox("Choose your task", ["Leads", "Generate Emails", "Client Management", "Campaign Management"])

        if page == "Leads":
            leads_page()
        elif page == "Generate Emails": 
            email_generation_page()
        elif page == "Client Management":
            client_management_page()
        elif page == "Campaign Management":
            campaign_page()
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')
        # Page selection
        

def leads_page():
    st.title("Lead Management Tool")
    client_list = Clients.get_all_clients()
    client_names = [client['company_name'] for client in client_list]
    with st.form(key='enrichment_form'):
        st.write("Enrich Leads for: ")
        client_name = st.selectbox("Select a client to enrich leads for:", client_names+["All Clients"])
        submit_button = st.form_submit_button(label='Submit')
    if submit_button or 'client_name' in st.session_state:
        if client_name != "All Clients":
            client_id = Clients.get_client_by_name(client_name)['_id']
            leads = Leads.get_unenriched_leads_by_client_id(client_id)
            st.write("This action will enrich "+str(len(leads))+" leads.")
            
            st.session_state.client_name = client_name
            if st.button("Enrich Leads"):
                st.session_state.client_id = client_id
                st.session_state.leads = leads
                st.write(f"Enriching leads for {client_name}...")
                print("Enriching leads for ", client_name)
                enrichMongoDB(client_id)
                st.write("Enrichment complete!")
        else:
            st.write("This action will enrich all leads.")
            if st.button("Enrich Leads"):
                st.write("Enriching all leads...")
                enrichMongoDB()
        
    
    with st.form(key='my_form'):
        client_name = st.selectbox("Select a client to add leads to:", client_names)
        group = st.text_input("Enter Group Name")
        submit_button = st.form_submit_button(label='Submit')
    if submit_button or 'client_name' in st.session_state:
        st.session_state.client_name = client_name
        st.session_state.group = group
        client_id = Clients.get_client_by_name(client_name)['_id']
        st.session_state.client_id = client_id

        choice = st.selectbox("Manual Upload or Direct From Wiza", ["Manual Upload", "Direct From Wiza"])

        if choice == "Manual Upload":
            uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

            if uploaded_file is not None:
                if 'data' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
                    data = pd.read_csv(uploaded_file)
                    data['client_id'] = client_id
                    data['group'] = group
                    async_upload_leads(data=data, client_name=client_name, group=group, client_id=client_id)
        elif choice == "Direct From Wiza":
            list_id = st.text_input("Enter Wiza List ID", value=None)
            if list_id and st.button("Get Leads from Wiza"):
                upload_leads(client_name=client_name, group=group, client_id=client_id)



def client_management_page():
    st.title("Client Management Tool")

    # Retrieve all clients from the database
    client_list = Clients.get_all_clients()
    client_names = ["New Client"] + [client['company_name'] for client in client_list]  # Add option for adding a new client

    # with form
    with st.form(key='client_form'):
        selected_client_name = st.selectbox("Select Client or Add New", client_names)
        submit_button = st.form_submit_button(label='Submit')
        if submit_button and selected_client_name != "New Client":
            selected_client = Clients.get_client_by_name(selected_client_name)
        else:
            selected_client = None

    # Show fields for update/create with information preloaded if updating
    st.subheader("Client Information")
    name = st.text_input("Client Name", value=selected_client.get('name', '') if selected_client else "")
    email = st.text_input("Client Email", value=selected_client.get('email', '') if selected_client else "")
    company_name = st.text_input("Company Name", value=selected_client.get('company_name', '') if selected_client else "")
    company_website = st.text_input("Company Website", value=selected_client.get('company_website', '') if selected_client else "")
    company_industry = st.text_input("Company Industry", value=selected_client.get('company_industry', '') if selected_client else "")
    company_summary = st.text_input("Company Summary", value=selected_client.get('company_summary', '') if selected_client else "")
    fees = st.text_input("Company Fees", value=selected_client.get('company_fees', '') if selected_client else "")
    company_emails_text = st.text_input("Comma separated Company Emails", value=', '.join(selected_client.get('company_emails', [])) if selected_client else "")

    company_emails = [email.strip() for email in company_emails_text.split(',')] if company_emails_text else []

    # Button to save changes
    if st.button("Save Client"):
        client = {
            "name": name,
            "email": email,
            "company_name": company_name,
            "company_website": company_website,
            "company_industry": company_industry,
            "company_summary": company_summary,
            "company_emails": company_emails,
            "company_fees": fees
        }

        if selected_client_name == "New Client":
            # Add new client
            Clients.create_client(client)
            st.success("Client added!")
        else:
            # Update existing client
            Clients.update_client(selected_client['_id'], client)
            st.success("Client updated!")


def campaign_page():
    st.title("Campaign Management Tool")
    # Get all clients
    clients = Clients.get_all_clients()
    client_names = [client['company_name'] for client in clients]
    chosen_client_name = st.selectbox("Select Client", client_names)
    
    # Get selected client
    client = Clients.get_client_by_name(chosen_client_name)
    st.session_state.client = client

    # Get campaigns for client
    campaigns = Campaigns.get_campaigns_by_client_id(client['_id'])
    campaign_names_and_ids = [(campaign['name'], campaign['_id']) for campaign in campaigns]
    if campaign_names_and_ids != []:
        with st.form(key='campaign_form'):
            chosen_campaign_name = st.selectbox("Select Campaign: ", campaign_names_and_ids, format_func=lambda x: x[0])[0]   
            if st.form_submit_button(label='Submit'):
                campaign_id = [campaign[1] for campaign in campaign_names_and_ids if campaign[0] == chosen_campaign_name][0]
                st.session_state['campaign_id'] = campaign_id
                st.session_state['campaign'] = Campaigns.get_campaign_by_id(campaign_id)
    # Add Campaign Button
    if st.button("Add Campaign"):
        st.session_state['add_campaign_clicked'] = True

    # Create New Campaign Section
    if st.session_state.get('add_campaign_clicked', False):
        new_campaign_name = st.text_input("Enter Campaign CodeName: ")
        if st.button("Create new campaign"):
            new_campaign_client = client['_id']
            campaign_id = Campaigns.create_campaign(new_campaign_name, new_campaign_client)
            chosen_campaign_name = new_campaign_name
            st.success("Campaign added!")
            st.session_state['add_campaign_clicked'] = False  # Reset the state
            st.session_state['campaign_id'] = campaign_id
            st.session_state['campaign'] = Campaigns.get_campaign_by_id(campaign_id)
            st.session_state['emails'] = Campaigns.get_campaign_by_id(campaign_id).get('emails', [])
            st.rerun()  # Rerun the script to display the new campaign

    try: 
        if 'campaign' in st.session_state:
            email_count = st.number_input("How many emails should be in the campaign?", min_value=1, max_value=10, value=len(st.session_state['campaign'].get('emails',[1])))
            # Initialize or adjust the size of session_state.emails
            if 'emails' in st.session_state['campaign']:
                st.session_state.emails = st.session_state['campaign']['emails']
            elif 'emails' not in st.session_state:
                st.session_state.emails = [{'main_template': ''} for _ in range(email_count)]
            elif len(st.session_state.emails) != email_count:
                st.session_state.emails = st.session_state.emails[:email_count] + [{'main_template': ''} for _ in range(email_count - len(st.session_state.emails))]

            # Create text areas for each email template
            for i in range(email_count):
                with st.container():
                    st.write(f"Email {i+1}")
                    email_key = f"email_template_{i}"  # Unique key for each email template
                    email_subject_key = f"email_subject_{i}"
                    if i < len(st.session_state.emails):
                        subject = st.session_state.emails[i].get('subject', '')
                        body = st.session_state.emails[i].get('body', '')
                    else:
                        st.session_state.emails.append({'subject': '', 'main_template': ''})
                    st.session_state.emails[i]['subject'] = st.text_input("Enter Email Subject:", value=subject, key = email_subject_key)
                    st.session_state.emails[i]['main_template'] = st.text_area("Please write the email template here:", value=body, key=email_key)
            # Confirm Templates Button
            if st.button("Confirm Email Templates"):
                for i, email in enumerate(st.session_state.emails):
                    main_template = email.get('subject', '')+'/n/n/n/n'+email.get('main_template', '')
                    input_fields = {}
                    while "{{" in main_template:
                        start = main_template.find("{{")
                        end = main_template.find("}}", start)
                        input_field = main_template[start+2:end].strip()
                        input_fields[input_field] = ''  # Initialize each input field with an empty string
                        main_template = main_template[end+2:]
                    st.session_state.emails[i]['input_fields'] = input_fields

            # Display input fields for each template
            unique_input_fields = set()

            # First pass: collect all unique field names from all emails
            for i, email in enumerate(st.session_state.emails):
                if 'input_fields' in email:
                    for input_field in email['input_fields']:
                        unique_input_fields.add(input_field)
            existing_input_fields = {}
            if 'emails' in st.session_state:
                for email in st.session_state['emails']:
                    if 'fields' in email:
                        for field in email['fields']:
                            existing_input_fields[field] = email['fields'][field]
            # Second pass: Display the fields
            for input_field in unique_input_fields:
                with st.container():
                    st.write(f"Input field: {input_field}")

                    # Create a single input field for the unique input field
                    input_field_key = f"unique_{input_field}"  # Unique key for each unique input field
                    input_value = st.text_input(f"Detailed description of {input_field}", key=input_field_key, value=existing_input_fields.get(input_field, ''))

                    # Set the value for the input field in each email where it appears
                    for i, email in enumerate(st.session_state.emails):
                        if 'input_fields' in email and input_field in email['input_fields']:
                            email['input_fields'][input_field] = input_value
            for i, email in enumerate(st.session_state.emails):
                with st.container():
                    st.write(f"Settings for Email {i+1}")
                    use_AI_key = f"use_AI_{i}"+str(i+1)
                    default_value = int(st.session_state.emails[i].get('use_AI', False))
                    default_index = 0 if default_value == 1 else 1
                    user_choice = st.radio(f"Use hyper-personalization with AI for Email {i+1}", 
                            ("Yes", "No"), 
                            index=default_index,
                            key=use_AI_key)
                    st.session_state.emails[i]['use_AI'] = (user_choice == "Yes")
            email_schemas = []
            for email in st.session_state.emails:
                email_schema = {
                    "subject": email['subject'] if email['subject'] != '' else None,
                    "body": email['main_template'],
                    "fields": email.get('input_fields', {}),
                    "useAI": email.get('use_AI', False),
                }
                email_schemas.append(email_schema)

            # Button to save the campaign
            st.text("IMPORTANT BEFORE YOU SAVE: What do we need to know about each lead to write a good campaign for them?")
            data_request = st.text_input("Enter that information here: ", value=None)
            if data_request and st.button("Save Campaign"):
                campaign_schema = {
                    "name": chosen_campaign_name,
                    "client_id": client['_id'],
                    "status": {},  # Add logic to set the campaign status
                    "emails": email_schemas,
                    "data_request": data_request
                }
                Campaigns.update_campaign_by_id(st.session_state['campaign_id'], campaign_schema)
                st.success("Campaign saved to database.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

def email_generation_page():
    st.title("Email Generation Tool")

    """
    choose client -> 
    choose campaign -> 
    get and select leads -> 
    generate emails -> 
    output as csv
    """
    # Get all clients
    clients = Clients.get_all_clients()
    client_names = [client['company_name'] for client in clients]
    chosen_client_name = st.selectbox("Select Client", client_names)
    chosen_client = Clients.get_client_by_name(chosen_client_name)
    st.session_state.client = chosen_client

    # Get campaigns for client
    campaigns = Campaigns.get_campaigns_by_client_id(chosen_client['_id'])
    campaign_names = [campaign['name'] for campaign in campaigns]
    chosen_campaign_name = st.selectbox("Select Campaign: ", campaign_names)
    chosen_campaign = Campaigns.get_campaign_by_name(chosen_campaign_name)
    st.session_state.campaign = chosen_campaign

    # Get leads for campaign
    leads = Leads.get_fully_enriched_leads_by_client_id(chosen_client['_id'])
    print("Leads: ", len(leads))
    with st.form(key='lead_form'):
        max_leads = st.number_input("How many leads should be in the campaign?", min_value=0, max_value=len(leads), value=min(6, len(leads)))
        submit_button = st.form_submit_button(label='Submit')
    if submit_button or 'max_leads' in st.session_state:
        st.session_state.max_leads = max_leads
        leads = leads[:max_leads]
        st.session_state.leads = leads
        if st.button("Select Groups"):
            groups = list(set([lead.get('group', '') for lead in leads]))
            selected_groups = st.checkbox("Select Group", groups)
            leads = [lead for lead in leads if lead.get('group', '') in selected_groups]
            st.session_state.leads = leads
        if st.button("Generate Emails"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("Initializing email crafting process...")
            batch_id = bson.ObjectId()
            for lead in st.session_state.leads:
                lead['batch_id'] = batch_id
            createEmailsForLeadsByTemplate(chosen_client, st.session_state.leads,chosen_campaign,progress_bar, status_text)
            status_text.text("Emails Created!")
            lead_file_name = "leads_for_campaign_"+chosen_campaign_name+"_for_"+chosen_client_name+".csv"
            final_leads = Leads.get_leads_by_batch_id(batch_id)
            final_leads = [leadForCSV(lead) for lead in final_leads]
            final_leads = pd.DataFrame(final_leads)
            st.dataframe(final_leads.head())
            st.download_button("Download Emails!", data=final_leads.to_csv(), file_name=lead_file_name, mime='text/csv')

if __name__ == "__main__":
    main()
