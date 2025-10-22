import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # App
    APP_ENV = os.getenv("APP_ENV", "dev")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Jira
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_AUTH_METHOD = os.getenv("JIRA_AUTH_METHOD", "token")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    
    # Data Source
    DATA_SOURCE = os.getenv("DATA_SOURCE", "mock")
    EXPORT_DIR = os.getenv("EXPORT_DIR", "./out")
    
    # Limits
    MAX_EPICS_PER_REQUEST = int(os.getenv("MAX_EPICS_PER_REQUEST", 10))
    REQUEST_TIMEOUT_SEC = int(os.getenv("REQUEST_TIMEOUT_SEC", 20))
    RETRY_COUNT = int(os.getenv("RETRY_COUNT", 2))