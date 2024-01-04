import csv
import services_and_db.leads.LeadMongo as Leads
def addLead(lead)->bool:
    """
    Adds a lead to the database
    """
    if Leads.validate_lead(lead):
        db_lead = Leads.get_lead_by_email(lead['email'])
        if db_lead!= None:
            print("Updating lead")
            return Leads.update_lead(db_lead['_id'], lead)
        else:
            print("Adding lead")
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
        print(lead)
        if not addLead(lead):
            pass ### TODO: handle this
    return True

def updateLead(lead)->bool:
    return Leads.update_lead(lead['_id'], lead)

def get_unenriched_leads():
    return Leads.get_unenriched_leads()

def get_leads_by_client_id(client_id):
    return Leads.get_leads_by_client_id(client_id)

def get_leads_by_campaign_id(campaign_id):
    return Leads.get_leads_by_campaign_id(campaign_id)