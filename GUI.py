import streamlit as st
import pandas as pd
import json
import os
from enrichmentPipeline import enrichCSV, writeEmailForEntry
import strings 
import Persistent.leadService as Leads
# Define the functions enrichRow and enrichCSV (already provided)

# Streamlit UI
def main():

    # Page selection
    page = st.sidebar.selectbox("Choose your task", ["Enrich CSV", "Generate Emails"])

    if page == "Enrich CSV":
        enrich_csv_page()
    elif page == "Generate Emails": 
        email_generation_page()

def enrich_csv_page():
    st.title("CSV Enrichment Tool")   
        
    # Layout
    col1, col2 = st.columns([1, 1])
    # Upload CSV in the left column
    with col1:
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        if uploaded_file is not None:
            foulderName = "data/" + uploaded_file.name.split('.')[0]
            data = pd.read_csv(uploaded_file)
            st.write("First 5 entries of the uploaded file:")
            st.dataframe(data.head())
        

    # Column name modification in the middle column
    with col2:
        if uploaded_file is not None:
            column_names = data.columns.tolist()
            st.write("Modify column names if necessary:")
            new_column_names = [st.text_input(f"Column {i+1}", column_names[i]) for i in range(len(column_names))]
            if st.button("Update Column Names or save to relevant foulder"):
                data.columns = new_column_names
                Leads.addLeadsFromDataFrame(data)
                st.success("Column names updated and changes saved!")


    context = st.text_input("Enter context about your company:", strings.brightboundContext)
    # Start enrichment process
    if st.button("Start Enrichment") and context is not None:
        if uploaded_file is not None:
            
            print(context + "test2")
            if context == "":
                context = "brightbound stuff"
            # Setup for progress bar and status text
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("Initializing enrichment process...")

            # File processing setup
            destination = "enriched_data.csv"

            # Call the enrichment function
            enrichCSV(uploaded_file.name, context, destination, progress_bar, status_text)

            # Update status text after completion
            status_text.text("Enrichment Completed!")

            # Display the enriched data
            enriched_data = pd.read_csv(destination)
            st.write("Enriched File:")
            st.dataframe(enriched_data.head())
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
