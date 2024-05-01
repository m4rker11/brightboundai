import streamlit as st
import pandas as pd
import bson
from services_and_db.leads.LeadObjectConverter import *
from EnrichmentPipeline.enrichmentPipeline import createEmailsForLeadsByTemplate,  async_upload_leads, upload_leads
import services_and_db.clients.clientMongo as Clients
import services_and_db.leads.leadService as Leads
import services_and_db.campaigns.campaignMongo as Campaigns
# Define the functions enrichRow and enrichCSV (already provided)

# Streamlit UI
def main():
    # Page selection
    page = st.sidebar.selectbox("Choose your task", ["Leads", "Generate Emails", "Client Management", "Campaign Management", "Perfect First Email"])

    if page == "Leads":
        leads_page()
    elif page == "Generate Emails": 
        email_generation_page()
    elif page == "Client Management":
        client_management_page()
    elif page == "Campaign Management":
        campaign_page()

def leads_page():
    st.title("Lead Management Tool")

    client_list = Clients.get_all_clients()
    client_names = [client['name'] for client in client_list]
    with st.form(key='my_form'):
        client_name = st.selectbox("Select a client to add leads to:", client_names)
        group = st.text_input("Enter Group Name")
        submit_button = st.form_submit_button(label='Submit')
    if submit_button or 'client_name' in st.session_state:
        st.session_state.client_name = client_name
        st.session_state.group = group


        choice = st.selectbox("Manual Upload or Direct From Wiza", ["Manual Upload", "Direct From Wiza"])

        if choice == "Manual Upload":
            uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

            if uploaded_file is not None:
                if 'data' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
                    data = pd.read_csv(uploaded_file)
                    data['client_id'] = client_id
                    data['group'] = group
                    async_upload_leads(data=data, streamlit=st)
        elif choice == "Direct From Wiza":
            if st.button("Get Leads from Wiza"):
                client_id = Clients.get_client_by_name(client_name)['_id']
                upload_leads(client_name=client_name, group=group, client_id=client_id)
           
    #         Leads.addLeadsFromDataFrame(st.session_state.data)
    #         st.success("Leads added to client!")

    #     if st.button("Start Website Enrichment"):
    #         enrich_leads_with_website_info(st.session_state.data)

    #     if st.button("Enrich ALL Leads linkedIn"):
    #         progress_bar = st.progress(0)
    #         status_text = st.empty()
    #         status_text.text("Initializing Linkedin enrichment process...")
    #         profiles = Leads.get_leads_for_linkedin_enrichment()
    #         fetch_and_update_profiles(profiles, progress_bar, status_text)


def client_management_page():
    st.title("Client Management Tool")

    # Retrieve all clients from the database
    client_list = Clients.get_all_clients()
    client_names = ["New Client"] + [client['name'] for client in client_list]  # Add option for adding a new client

    selected_client_name = st.selectbox("Select Client or Add New", client_names)
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
        chosen_campaign_name = st.selectbox("Select Campaign: ", campaign_names_and_ids, format_func=lambda x: x[0])[0]
        campaign_id = [campaign[1] for campaign in campaign_names_and_ids if campaign[0] == chosen_campaign_name][0]
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

    # Confirm Selection Button
    if st.button("Confirm Selections"):
        campaign = Campaigns.get_campaign_by_id(campaign_id)
        st.session_state['campaign'] = campaign

    try: 
        if 'campaign' in st.session_state:
            recipient_count = st.number_input("Enter Recipient Count:", value=500, min_value=1)
            email_count = st.number_input("How many emails should be in the campaign?", min_value=1, max_value=10, value=5)

            # Initialize or adjust the size of session_state.emails
            if 'emails' not in st.session_state:
                st.session_state.emails = [{'main_template': ''} for _ in range(email_count)]
            elif len(st.session_state.emails) != email_count:
                st.session_state.emails = st.session_state.emails[:email_count] + [{'main_template': ''} for _ in range(email_count - len(st.session_state.emails))]

            # Create text areas for each email template
            for i in range(email_count):
                with st.container():
                    st.write(f"Email {i+1}")
                    email_key = f"email_template_{i}"  # Unique key for each email template
                    email_subject_key = f"email_subject_{i}"
                    st.session_state.emails[i]['subject'] = st.text_input("Enter Email Subject:", value=st.session_state.emails[i].get('subject', ''), key = email_subject_key)
                    st.session_state.emails[i]['main_template'] = st.text_area("Please write the email template here:", value=st.session_state.emails[i]['main_template'], key=email_key)
            # Confirm Templates Button
            if st.button("Confirm Email Templates"):
                for i, email in enumerate(st.session_state.emails):
                    main_template = email['subject']+'/n/n/n/n'+email['main_template']
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

            # Second pass: Display the fields
            for input_field in unique_input_fields:
                with st.container():
                    st.write(f"Input field: {input_field}")

                    # Create a single input field for the unique input field
                    input_field_key = f"unique_{input_field}"  # Unique key for each unique input field
                    input_value = st.text_input(f"Detailed description of {input_field}", key=input_field_key)

                    # Set the value for the input field in each email where it appears
                    for i, email in enumerate(st.session_state.emails):
                        if 'input_fields' in email and input_field in email['input_fields']:
                            email['input_fields'][input_field] = input_value
            for i, email in enumerate(st.session_state.emails):
                with st.container():
                    st.write(f"Settings for Email {i+1}")
                    use_AI_key = f"use_AI_{i}"
                    default_value = int(st.session_state.emails[i].get('use_AI', False))
                    user_choice = st.radio(f"Use hyper-personalization with AI for Email {i+1}", 
                               ("Yes", "No"), 
                               index=default_value, 
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
            if st.button("Save Campaign"):
                campaign_schema = {
                    "name": chosen_campaign_name,
                    "client_id": client['_id'],
                    "recipient_count": recipient_count,
                    "status": {},  # Add logic to set the campaign status
                    "emails": email_schemas
                }
                Campaigns.update_campaign_by_id(campaign_id, campaign_schema)
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
    leads = Leads.get_leads_by_client_id(chosen_client['_id'])
    groups = list(set([lead.get('group', '') for lead in leads]))
    group = st.selectbox("select group names", groups) 
    if st.button("Get by group"):
        leads = [lead for lead in leads if lead.get('group', '') == group]
        st.session_state.leads = leads
    if st.button("Generate Emails"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Initializing email crafting process...")
        batch_id = bson.ObjectId()
        for lead in leads:
            lead['batch_id'] = batch_id
        createEmailsForLeadsByTemplate(chosen_client, st.session_state.leads,chosen_campaign,progress_bar, status_text)
        status_text.text("Emails Created!")
        lead_file_name = "leads_for_campaign_"+chosen_campaign_name+"_for_"+chosen_client_name+" " + group+".csv"
        final_leads = Leads.get_leads_by_batch_id(batch_id)
        final_leads = [leadForCSV(lead) for lead in final_leads]
        final_leads = pd.DataFrame(final_leads)
        st.dataframe(final_leads.head())
        st.download_button("Download Emails!", data=final_leads.to_csv(), file_name=lead_file_name, mime='text/csv')

if __name__ == "__main__":
    main()
