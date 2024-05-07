import services_and_db.leads.LeadMongo as Leads
def addLead(lead)->bool:
    """
    Adds a lead to the database
    """
    if Leads.validate_lead(lead):
        db_lead = Leads.get_lead_by_email(lead['email'])
        if db_lead!= None:
            print("Updating lead ", db_lead['_id'])
            return Leads.update_lead(db_lead['_id'], lead)
        else:
            print("Adding lead")
            return Leads.add_lead(lead)
    else:
        return False

def addLeadsFromDataFrame(df)->bool:
    """
    Adds leads from a dataframe
    """
    for _, row in df.iterrows():
        lead = row.to_dict()
        if not addLead(lead):
            print("Failed to add lead")
            pass ### TODO: handle this
    return True

def updateLead(lead)->bool:
    return Leads.update_lead(lead['_id'], lead)

def get_unenriched_leads():
    return Leads.get_leads_for_website_or_linkedin_enrichment()

def get_leads_for_linkedin_enrichment():
    return Leads.get_leads_for_linkedin_enrichment()

def get_leads_by_client_id(client_id):
    return Leads.get_leads_by_client_id(client_id)

def get_fully_enriched_leads_by_client_id(client_id):
    return Leads.get_fully_enriched_leads_by_client_id(client_id)

def get_leads_by_campaign_id(campaign_id):
    return Leads.get_leads_by_campaign_id(campaign_id)

def get_leads_by_batch_id(batch_id):
    return Leads.get_leads_by_batch_id(batch_id)

def check_if_lead_exists(email, website, client_id)->bool:
    return Leads.check_if_lead_exists(email, website, client_id)

def get_leads_without_risk():
    return Leads.get_leads_without_risk()