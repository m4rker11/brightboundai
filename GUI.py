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
    campaign_names = [campaign['name'] for campaign in campaigns]
    chosen_campaign_name = st.selectbox("Select Campaign: ", campaign_names)

    # Add Campaign Button
    if st.button("Add Campaign"):
        st.session_state['add_campaign_clicked'] = True

    # Create New Campaign Section
    if st.session_state.get('add_campaign_clicked', False):
        new_campaign_name = st.text_input("Enter Campaign CodeName: ")
        if st.button("Create new campaign"):
            new_campaign_client = client['_id']
            Campaigns.create_campaign(new_campaign_name, new_campaign_client)
            chosen_campaign_name = new_campaign_name
            st.success("Campaign added!")
            st.session_state['add_campaign_clicked'] = False  # Reset the state

    # Confirm Selection Button
    if st.button("Confirm Selections"):
        campaign = Campaigns.get_campaign_by_name(chosen_campaign_name)
        st.session_state['campaign'] = campaign

    try: 
        if st.session_state['campaign'] is not None:
        # EMAIL TEMPLATE CRAFTING
            email_count = st.number_input("How many emails should be in the campaign?", min_value=1, max_value=10, value=5, key="email_count")

            # Adjust the size of session_state.emails if the number of emails changes
            if 'emails' not in st.session_state or len(st.session_state.emails) != email_count:
                st.session_state.emails = [{'use_AI': False, 'email_objective': ''} for _ in range(email_count)]

            # Create inputs for each email
            for i in range(email_count):
                with st.container():
                    st.write(f"Email {i+1}")

                    # Unique keys for each input
                    use_AI_key = f"use_AI_{i}"
                    objective_key = f"email_objective_{i}"

                    # Radio button for AI use
                    st.session_state.emails[i]['use_AI'] = st.radio("Use hyper-personalization with AI", ("Yes", "No"), index=int(st.session_state.emails[i]['use_AI']), key=use_AI_key) == "Yes"

                    # Text input for email objective
                    st.session_state.emails[i]['email_objective'] = st.text_input("Enter Email Objective:", value=st.session_state.emails[i]['email_objective'], key=objective_key)

            # Button to generate email templates
            if st.button("Generate Email Templates"):
                for i, email_data in enumerate(st.session_state.emails):
                    email_template = generateEmailFormat(st.session_state.client['company_summary'], st.session_state.client['icp'], email_data['email_objective'])
                    st.json(email_template)
    except:
        pass

    # """ 
    # What this page needs to do:
    # - Create new campaigns
    # - Load and edit existing campaigns
    # - Assign campaign to x leads from y total leads of client z at random
    # - Add sequences to campaigns

    # """




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
