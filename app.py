import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Smart Health AI",
    page_icon="🏥",
    layout="wide"
)

import os
import json
from config import get_firestore_client, initialize_firebase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to get Google API key from different sources
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or st.secrets.get('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("Google API key not found. Please add it to your .env file or Streamlit secrets.")
    st.stop()

from auth import login_page, check_authentication, logout
from medical_ai import MedicalAI

# Initialize Firebase with proper error handling
try:
    db = initialize_firebase()
    if db is None:
        st.error("Failed to initialize Firebase. Please check your configuration.")
        st.stop()
except Exception as e:
    st.error(f"Firebase initialization error: {str(e)}")
    st.stop()

medical_ai = MedicalAI(GOOGLE_API_KEY)

def main():
    # Check authentication
    if not check_authentication():
        login_page()
        return

    # Custom CSS for responsive design
    st.markdown("""
    <style>
        .main-content {
            max-width: 1200px;
            margin: auto;
        }
        .stButton>button {
            width: 100%;
        }
        .consultation-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar with user info and history
    with st.sidebar:
        # User info section
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;'>
            <h3>👤 {st.session_state.user.email}</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        # History section in sidebar
        st.markdown("<div class='sidebar-history'>", unsafe_allow_html=True)
        st.markdown("### 📑 Recent Consultations")
        
        db = get_firestore_client()
        history = medical_ai.get_user_history(db, st.session_state.user.uid)
        
        if not history:
            st.info("📝 No consultation history yet")
        else:
            for consultation in history:
                # Use title in expander header if available, otherwise use timestamp
                title = consultation.get('title', 'Consultation')
                timestamp = consultation['timestamp'].strftime('%Y-%m-%d %H:%M')
                
                with st.expander(f"📅 {timestamp} - {title}"):
                    st.markdown("**🩺 Health Concern:**")
                    st.write(consultation.get('symptoms', ''))
                    st.markdown("**👨‍⚕️ Medical Advice:**")
                    st.markdown(consultation.get('advice', ''))

    # Main content area with Dracula theme
    st.title("🏥 Smart Health AI Assistant")
    
    # Health concern input section
    st.markdown("### 🩺 Describe Your Health Concern")
    user_input = st.text_area(
        "",  # Empty label since we already have the header
        height=150,
        placeholder="Enter your health concerns or symptoms here..."
    )
    
    # Get advice button
    if st.button("🔍 Get Medical Advice", use_container_width=True):
        if user_input:
            with st.spinner("🤔 Analyzing your health concern..."):
                advice = medical_ai.get_medical_advice(user_input)
                
                # Display advice in a card
                st.markdown("""
                <div class='consultation-card'>
                    <h3>🩺 Medical Advice</h3>
                    {}</div>
                """.format(advice), unsafe_allow_html=True)
                
                # Save to history
                try:
                    db = get_firestore_client()
                    if db:
                        medical_ai.save_consultation(db, st.session_state.user.uid, user_input, advice)
                except Exception as e:
                    st.warning("Could not save consultation to history.")
        else:
            st.warning("⚠️ Please provide more details about your health concern for a better assessment.")
    
    # New consultation form
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    # Input sections
   

...
if __name__ == "__main__":
    main()
