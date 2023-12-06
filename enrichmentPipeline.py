import AI.summarize as summarizer
import AI.emailWriter as emailWriter
import scraper.scraper as scraper
import linkedin.getLinkedInInfo as linkedin
import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def enrichCSV(csv_path, context, destination, progress_bar, status_text):
    # Check if the destination file already exists and has content
    file_exists = False
    try:
        with open(destination, 'r', newline='') as f:
            file_exists = f.read(1)
    except FileNotFoundError:
        pass

    # Open the input CSV and read rows
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)

        # Define batch size
        batch_size = 10

        # Process rows in batches
        for start_index in range(0, total_rows, batch_size):
            end_index = min(start_index + batch_size, total_rows)
            batch = rows[start_index:end_index]

            # Set up the ThreadPoolExecutor for the current batch
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                # Submit tasks for the current batch
                future_to_row = {executor.submit(enrichRow, row, context): row for row in batch}

                # Initialize a list to hold processed rows for the current batch
                processed_batch = []

                # Collect results as they are completed
                for future in as_completed(future_to_row):
                    enriched_row = future.result()
                    if enriched_row is not None:
                        processed_batch.append(enriched_row)

            # Write the processed batch to the CSV file
            with open(destination, 'a', newline='') as destfile:
                fieldnames = ['full_name', 'first_name', 'website_url', 'company', 'email', 'linkedIn_url', 'city', 'linkedin_summary', 'website_summary', 'icp', 'offer']
                writer = csv.DictWriter(destfile, fieldnames=fieldnames)

                # Write the header only if the file is new/empty
                if not file_exists and start_index == 0:
                    writer.writeheader()
                    file_exists = True

                for enriched_row in processed_batch:
                    writer.writerow(enriched_row)

            # Update progress bar and status text
            progress = end_index / total_rows
            progress_bar.progress(progress)
            status_text.text(f"Processed rows {start_index + 1} to {end_index} of {total_rows}")


def enrichRow(row, context):
    #part 1: get the linkedin profile
    linkedin_profile = linkedin.getLinkedInInfo(row['linkedIn_url'])
    if linkedin_profile is None:
        return None
    #save it as a json locally
    #part 2: get the website content
    website_content = scraper.scrape_website_task(row['website_url'])
    # part 3: summarize the linkedin profile
    linkedin_summary = summarizer.summarizeProfileData(linkedin_profile)
    # part 4: summarize the website content
    website_summary = summarizer.summarizeWebsiteContent(website_content, context)
    # part 5: return the new row
    row['linkedin_summary'] = linkedin_summary['text']
    row['website_summary'] = website_summary['summary']
    row['icp'] = website_summary['icp']
    row['offer'] = website_summary['offer']
    return row


def writeEmailForEntry(row, product_context,**kwargs):
    outputFormat = kwargs.get('outputFormat', None)
    resultJson = emailWriter.writeEmail(row['first_name'], row['company'], row['linkedin_summary'], row['website_summary'], product_context, outputFormat)
    #iterate over the keys and add them to the row
    for key in resultJson.keys():
        row[key] = resultJson[key]
    return row
