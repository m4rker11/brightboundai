# Lead Enrichment and Email Campaign Management System

## Features

- 🔍 Automated lead enrichment from websites and LinkedIn
- 🤖 AI-powered email personalization
- 📊 Multi-client campaign management
- 🌐 Anti-detection web scraping
- ✉️ Email risk verification
- 📱 User-friendly Streamlit interface

## Installation

### Prerequisites

- Python 3.10+
- Node.js 16+
- MongoDB instance
- OpenAI API access
- Instantly.ai account

### Option 1: Local Development Environment with Conda

conda create -n lead-enrichment python=3.10
conda activate lead-enrichment
pip install -r requirements.txt

### Option 2: Production Deployment with Docker

docker build -t lead-enrichment .
docker run -p 8501:8501
  -e MONGO_CONNECTION_STRING=your_connection_string
  -e OPENAI_API_KEY=your_key
  -e INSTANTLY_API_KEY=your_key
  lead-enrichment

## Configuration

### Environment Variables

Create .env file in project root:

MONGO_CONNECTION_STRING=mongodb+srv://[username]:[password]@[cluster].mongodb.net/[database]
OPENAI_API_KEY=sk-...
INSTANTLY_API_KEY=inst-...

### Authentication Setup

Create credentials.yaml:

credentials:
  usernames:
    admin:
      email: admin@example.com
      name: Admin User
      password: hashed_password
cookie:
  name: auth_token
  key: random_key_string
  expiry_days: 30

## Database Structure

### Collections Schema

#### Clients Collection

{
    "name": "string",
    "email": "string",
    "company_name": "string",
    "company_website": "string",
    "company_industry": "string",
    "company_summary": "object",
    "company_emails": "array",
    "company_fees": "string"
}

## Step-by-Step Usage Guide

### 1. Client Setup

- Navigate to "Client Management"
- Click "New Client"
- Fill required fields:

  - Company Name
  - Industry
  - Website
  - Contact Information2. Lead Import
- Select "Leads" from sidebar
- Choose client
- Upload CSV or connect to Wiza
- Required CSV columns:

  - full_name
  - first_name
  - company
  - website_url
  - linkedIn_url
  - email

### 3. Campaign Creation

- Access "Campaign Management"
- Select client
- Create new campaign
- Define email sequence:
  - Subject lines
  - Email bodies
  - Personalization fields
  - AI enhancement settings

### 4. Email Generation

- Go to "Generate Emails"
- Select campaign and lead group
- Set batch size
- Monitor generation progress
- Download results and upload it to instantly

## Monitoring and Analytics

### Performance Metrics

- Lead enrichment success rate ~ 80%
- Email generation speed ~ 20-30 seconds per personalized campaign
- API usage tracking 10$ for 1000 leads at gpt-4-turbo pricing, much cheaper now
- Error rates ~ Somewhat high, but that has to mostly do with website protection, I recommend setting up proxies

### Common Issues and Solutions

#### MongoDB Connection

mongosh --eval "db.adminCommand('ping')"

# Rate limit settings in base.py

RATE_LIMIT = 60  # requests per minute

## Performance Optimization

### Batch Processing

- Optimal batch size: 10-50 leads
- Concurrent enrichment: 5 threads
- Rate limiting: 1 request/second

## This project has been abandoned

Feel free to use this for your lead generation needs. You might need to update the instantly apis to enable more recent functionality. I recommend using Wiza lists/apollo data. Good Luck!
