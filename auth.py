import streamlit as st
from firebase_admin import auth
import firebase_admin
from datetime import datetime
from config import initialize_firebase, FIREBASE_CONFIG
from social_auth import SocialAuth
import json

# Initialize Firebase at module level
db = initialize_firebase()
social_auth = SocialAuth()

def handle_google_login():
    """Handle Google OAuth login"""
    try:
        import secrets
        
        # Generate a random state parameter for security
        state = secrets.token_urlsafe(32)
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?" + \
                  f"client_id={st.secrets['GOOGLE_CLIENT_ID']}&" + \
                  f"redirect_uri={st.secrets['GOOGLE_REDIRECT_URI']}&" + \
                  f"response_type=code&" + \
                  f"scope=email profile&" + \
                  f"state={state}&" + \
                  f"prompt=consent"
        
        # Store the state in session
        st.session_state.oauth_state = {
            'provider': 'google',
            'redirect_uri': st.secrets['GOOGLE_REDIRECT_URI'],
            'state': state
        }
        
        # Redirect to Google login
        st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Google login failed: {str(e)}")

def handle_oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        # Get query parameters
        query_params = st.query_params
        
        # If no code is present, this might be the initial page load
        if 'code' not in query_params:
            return
            
        # Handle Google login
        user = social_auth.handle_google_login(query_params['code'])
        if user:
            st.session_state.user = user
            st.session_state.authenticated = True
            st.success("Successfully logged in with Google!")
            time.sleep(1)  # Give time for the success message to be seen
            st.rerun()
        else:
            st.error("Unable to complete login. Please try again.")
                
    except Exception as e:
        st.error("An error occurred during login. Please try again.")
    finally:
        # Clear OAuth state
        if 'oauth_state' in st.session_state:
            del st.session_state.oauth_state

def login_page():
    # Handle OAuth callback if present
    handle_oauth_callback()
    
    # Center the content using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Add some spacing
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Centered title with custom styling
        st.markdown("""
        <h1 style='text-align: center; color: #2E4057; margin-bottom: 40px;'>
            🏥 Smart Health AI
        </h1>
        """, unsafe_allow_html=True)
        
        # Add social login buttons
        st.markdown("""
        <style>
            .social-btn {
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                border: 1px solid #ddd;
                cursor: pointer;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .google-btn {
                background-color: white;
                color: #757575;
            }
            .facebook-btn {
                background-color: #1877f2;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Google login button with custom styling
        st.markdown("""
        <style>
            .google-btn {
                background-color: white;
                color: #757575;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
                width: 100%;
            }
            .google-btn:hover {
                background-color: #f8f8f8;
            }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Continue with Google", use_container_width=True, key="google_login"):
            handle_google_login()
        
        # Divider
        st.markdown("""
        <div style='text-align: center; position: relative; margin: 20px 0;'>
            <hr style='margin: 10px 0;'>
            <span style='position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: white; padding: 0 10px;'>
                OR
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a card-like container for email login
        with st.container():
            st.markdown("""
            <style>
                div[data-testid="stForm"] {
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                div[data-testid="stVerticalBlock"] {
                    gap: 20px !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Use a form for better organization
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="Enter your email")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                # Add some space between inputs and buttons
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Create two columns for buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    login_button = st.form_submit_button("🔐 Login", 
                        use_container_width=True,
                        type="primary")
                
                with col2:
                    register_button = st.form_submit_button("📝 Register",
                        use_container_width=True)
                
                if login_button and email and password:
                    try:
                        user = auth.get_user_by_email(email)
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.success("Login successful!")
                        st.rerun()
                    except Exception as e:
                        st.error("Login failed. Please check your credentials.")
                
                if register_button and email and password:
                    try:
                        if len(password) < 6:
                            st.error("Password must be at least 6 characters long.")
                        else:
                            user = auth.create_user(
                                email=email,
                                password=password
                            )
                            st.success("Registration successful! You can now login.")
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
        
        # Add footer with information
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; color: #666666; font-size: 0.8em;'>
            🔒 Your data is secure and encrypted<br>
            ⚕️ AI-powered health assistance
        </div>
        """, unsafe_allow_html=True)

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None
    return st.session_state.authenticated

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()
