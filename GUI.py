import streamlit as st
import pandas as pd
import json
import os
import enrichmentPipeline as ep
import services_and_db.clients.clientMongo as Clients
import services_and_db.leads.leadService as Leads
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
    page = st.sidebar.selectbox("Choose your task", ["Leads", "Generate Emails"])

    if page == "Leads":
        enrich_csv_page()
    elif page == "Generate Emails": 
        email_generation_page()

def leads_page():
    st.title("Lead Management Tool")   
        
    # Layout
    col1, col2 = st.columns([1, 1])
    # Upload CSV in the left column
    with col1:
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        if uploaded_file is not None:
            column_names = data.columns.tolist()
            st.write("Modify column names if necessary:")
            new_column_names = [st.text_input(f"Column {i+1}", column_names[i]) for i in range(len(column_names))]
            if st.button("Update Column Names or save to relevant foulder"):
                data.columns = new_column_names
                st.success("Column names updated and changes saved!")
        

    # Column name modification in the middle column
    with col2:
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            st.write("First 5 entries of the uploaded file:")
            st.dataframe(data.head())
            clients = Clients.get_all_clients()
            client_names = [client['name'] for client in clients]
            client_name = st.selectbox("Select Client", client_names)
            if st.button("Add Leads to Client"):
                # add client_id to each row
                client_id = Clients.get_client_by_name(client_name)['_id']
                data = data.assign(client_id=client_id)
                # add leads to mongo    
                Leads.addLeadsFromDataFrame(data)
                st.success("Leads added to client!")
    # the rest should be one column not two
    #            enrich all unenriched leads
    # client_context_dictionary should be {client_id: context, client_id: context}
    if st.button("Enrich ALL Leads"):
        progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Initializing enrichment process...")
            ep.enrichMongoDB(progress_bar, status_text)
            status_text.text("Enrichment Completed!")
            # Setup for progress bar and status text
    else:
        # Inform the user to provide the context
        st.warning("Please enter the context for summarization to start enrichment.")


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
