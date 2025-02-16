import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Firebase Web SDK configuration
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyASTXsdfOiPGNdtYR1b3nQTuLDrARLNk0E",
    "authDomain": "smarthealtai.firebaseapp.com",
    "projectId": "smarthealtai",
    "storageBucket": "smarthealtai.firebasestorage.app",
    "messagingSenderId": "825283462916",
    "appId": "1:825283462916:web:83afc7d2fdfcc09e8c7251",
    "measurementId": "G-Y2BQQ3NCJ3",
    # Social login configurations
    "googleClientId": os.getenv('GOOGLE_CLIENT_ID'),
    "facebookAppId": os.getenv('FACEBOOK_APP_ID')
}

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            # Load and validate service account key
            service_account_info = load_service_account()
            if service_account_info is None:
                st.markdown("""### How to get serviceAccountKey.json:
                1. Go to [Firebase Console](https://console.firebase.google.com)
                2. Select project 'smarthealtai'
                3. Click ⚙️ (Settings) -> Project Settings
                4. Go to 'Service accounts' tab
                5. Click 'Generate New Private Key'
                6. Save the file as 'serviceAccountKey.json' in the project directory""")
                return None
            
            try:
                # Initialize Firebase with the loaded credentials
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred, {
                    'projectId': FIREBASE_CONFIG['projectId'],
                    'storageBucket': FIREBASE_CONFIG['storageBucket']
                })
                return firestore.client()
            except Exception as e:
                st.error(f"Error initializing Firebase: {str(e)}")
                return None
        else:
            return firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {str(e)}")
        return None

def get_firestore_client():
    """Get Firestore client instance"""
    if 'db' not in st.session_state:
        st.session_state.db = initialize_firebase()
    return st.session_state.db

def load_service_account():
    """Load and validate the service account key file"""
    try:
        service_account_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
        with open(service_account_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as je:
        st.error(f"Error parsing serviceAccountKey.json: {str(je)}")
        return None
    except IOError as io_err:
        st.error(f"Error reading serviceAccountKey.json: {str(io_err)}")
        return None


