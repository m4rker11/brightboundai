import streamlit as st
import pandas as pd
import json
import os
import enrichmentPipeline as ep
import services_and_db.clients.clientMongo as Clients
import services_and_db.leads.leadService as Leads
import services_and_db.campaigns.campaignMongo as Campaigns
from AI.emailWriter import generateEmailFormat
# Define the functions enrichRow and enrichCSV (already provided)

# Streamlit UI
def main():
    """ page choices: 
        add leads to mongo
            upload csv
            confirm column names
            add leads to mongo
        enrich leads by query
            enrich all unenriched leads
            enrich by client id
            enrich by campaign id
        generate emails
            generate template
                generate follow up template
            edit template
            enrich with email template by campaign id and client id
        
        client setup
            add client
                assets
                context
                offer
                guarantee
                guidelines
            create campaign
            add leads to campaign
            add email template
            edit client context
    """
    # Page selection
    page = st.sidebar.selectbox("Choose your task", ["Leads", "Generate Emails", "Client Management", "Campaign Management"])

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
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    if uploaded_file is not None:
        if 'data' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            # Load data and reset column names if a new file is uploaded
            data = pd.read_csv(uploaded_file)
            st.session_state.data = data
            st.session_state.uploaded_file_name = uploaded_file.name

        st.write("Preview of uploaded file:")
        st.dataframe(st.session_state.data.head())

        # Column Renaming
        column_names = st.session_state.data.columns.tolist()
        st.write("Mandatory column names: full_name, name, company, website_url, linkedIn_url, email")
        st.write("Modify column names if necessary:")
        new_column_names = [st.text_input(f"Column {i+1}", column_names[i]) for i in range(len(column_names))]

        if st.button("Update or Confirm Column Names"):
            column_map = {column_names[i]: new_column_names[i] for i in range(len(column_names))}
            st.session_state.data.rename(columns=column_map, inplace=True)
            st.success(st.session_state.data.columns.tolist())  # Updated Column Names
            st.success("Column names updated or confirmed!")

        clients = Clients.get_all_clients()
        client_names = [client['company_name'] for client in clients]
        if len(client_names) == 0:
            st.warning("Please add clients before adding leads.")
        st.write("Select a client to add leads to:")
        client_name = st.selectbox("Select Client", client_names)
        if st.button("Add Leads to Client"):
            # add client_id to each row
            client = Clients.get_client_by_name(client_name)
            client_id = client['_id']
            st.session_state.data = st.session_state.data.assign(client_id=client_id)
            st.dataframe(st.session_state.data.head()) #HERE THE COLUMN NAMES ARE BACK TO WHAT THEY WERE
            # add leads to mongo    
            data = st.session_state.data
            st.dataframe(data.head())
            Leads.addLeadsFromDataFrame(data)
            st.success("Leads added to client!")
    if st.button("Enrich ALL Leads"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Initializing enrichment process...")
        ep.enrichMongoDB(progress_bar, status_text)
        status_text.text("Enrichment Completed!")

def client_management_page():
    st.title("Client Management Tool")
      
    company_emails = []
    name = st.text_input("Client Name")
    email = st.text_input("Client Email")
    company_name = st.text_input("Company Name")
    company_website = st.text_input("Company Website")
    company_industry = st.text_input("Company Industry")
    company_summary = st.text_input("Company Summary")
    fees = st.text_input("Company Fees")
    company_emails_text = st.text_input("Comma separated Company Emails")
    if company_emails_text != "":
        company_emails = company_emails_text.split(',')
        company_emails = [email.strip() for email in company_emails]
    if st.button("Add Client"):
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
        Clients.create_client(client)
        st.success("Client added!")
    client_list = Clients.get_all_clients()
    client_names = [client['name'] for client in client_list]
    st.selectbox("Select Client", client_names)

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
                    main_template = email['main_template']
                    input_fields = {}
                    while "{{" in main_template:
                        start = main_template.find("{{")
                        end = main_template.find("}}", start)
                        input_field = main_template[start+2:end].strip()
                        input_fields[input_field] = ''  # Initialize each input field with an empty string
                        main_template = main_template[end+2:]
                    st.session_state.emails[i]['input_fields'] = input_fields

            # Display input fields for each template
            for i, email in enumerate(st.session_state.emails):
                if 'input_fields' in email:
                    with st.container():
                        st.write(f"Input fields for Email {i+1}")
                        for input_field in email['input_fields']:
                            input_field_key = f"email_{i}_{input_field}"  # Unique key for each input field
                            email['input_fields'][input_field] = st.text_input(f"Detailed description of {input_field}", value=email['input_fields'][input_field], key=input_field_key)

                    use_AI_key = f"use_AI_{i}"
                    objective_key = f"email_objective_{i}"
                    st.session_state.emails[i]['use_AI'] = st.radio("Use hyper-personalization with AI", ("Yes", "No"), index=int(st.session_state.emails[i].get('use_AI', False)), key=use_AI_key) == "Yes"
                    st.session_state.emails[i]['email_objective'] = st.text_input("Enter Email Objective:", value=st.session_state.emails[i].get('email_objective', ''), key=objective_key)
            
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
                print(campaign_schema)
                print(campaign_id)
                Campaigns.update_campaign_by_id(campaign_id, campaign_schema)
                st.success("Campaign saved to database.")

    except Exception as e:
        st.error(f"An error occurred: {e}")




def email_generation_page():
    st.title("Email Generation Tool")

    # Upload the enriched CSV file
    enriched_file = st.file_uploader("Upload Enriched CSV File", type=['csv'])
    if enriched_file is not None:
        data = pd.read_csv(enriched_file)
        st.write("Preview of uploaded file:")
        st.dataframe(data.head())
        #load format options
        format_options = json.load(open("emailTemplates.json", "r"))['data']
        # Input for row range selection
        if len(format_options) == 0:
            st.warning("Please upload email templates in the emailTemplates.json file.")
        newOption = st.text_input("Enter a format option: ")
        if st.button("Add format option"):
            #add format option to emailTemplates.json
            # if newOption can be parsed to json:
            try:
                json.loads(newOption)
                format_options.append(newOption)
                with open("emailTemplates.json", "w") as outfile:
                    json.dump(format_options, outfile)
            except:
                st.warning("Please enter a valid json format.")
        min_row, max_row = st.slider("Select a range of rows", 1, len(data), (1, len(data)))
        output_format = st.selectbox("Select Output Format", format_options)  # Replace with actual formats

        # Process and save the data
        if st.button("Generate Emails"):
            # Load rows from selected range
            selected_rows = data.iloc[min_row - 1:max_row]
            example_df = pd.DataFrame()
            # Generate emails for each row in the range
            for index, row in selected_rows.iterrows():
                
                row = writeEmailForEntry(row.to_dict(), 'Your Product Context', outputFormat=output_format)
                while index < 5:
                    example_df = example_df.append(row, ignore_index=True)
                if index == 5:
                    st.write("Example of generated emails:")
                    st.dataframe(example_df)
                    
            # Save the updated data to a new CSV file
            new_file_name = enriched_file.name.split('.')[0] + '_with_email_'+min_row+'_'+ max_row+'.csv'
            selected_rows.to_csv(new_file_name, index=False)
            st.success(f"Emails generated and saved to {new_file_name}!")

if __name__ == "__main__":
    main()
