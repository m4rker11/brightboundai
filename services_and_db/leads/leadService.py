import csv
import LeadMongo as Leads
import pandas as pd
import campaigns.campaignMongo as Campaigns
def addLead(lead)->bool:
    """
    Adds a lead to the database
    """
    if Leads.validate_lead(lead):
        db_lead = Leads.get_lead_by_email(lead['email'])
        if db_lead!= None:
            return Leads.update_lead(db_lead['_id'], lead)
        else:
            return Leads.add_lead(lead)
    else:
        return False
    
def addLeadsFromCSV(csv_file_path)->bool:
    """
    Adds leads from a csv file
    """
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lead = dict(row)
            if not addLead(lead):
                return False
    return True

def addLeadsFromDataFrame(df)->bool:
    """
    Adds leads from a dataframe
    """
    for index, row in df.iterrows():
        lead = row.to_dict()
        if not addLead(lead):
            return False
    return True

def updateLead(lead)->bool:
    return Leads.update_lead(lead['_id'], lead)