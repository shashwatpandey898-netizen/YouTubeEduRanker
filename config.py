import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-eduranker'
    # API Key provided in project request
    GEMINI_API_KEY = "AIzaSyDTrUUAk-mVC9DAcvhuSGb1_efgyPwoaiY"
    DEBUG = True
