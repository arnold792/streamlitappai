import streamlit as st
import requests
import json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from firebase_admin import auth

class SocialAuth:
    def __init__(self):
        """Initialize Google Client ID from Streamlit secrets"""
        try:
            self.google_client_id = st.secrets["google"]["GOOGLE_CLIENT_ID"]
            self.google_client_secret = st.secrets["google"]["GOOGLE_CLIENT_SECRET"]
            self.google_redirect_uri = st.secrets["google"]["GOOGLE_REDIRECT_URI"]
        except KeyError as e:
            st.error(f"Missing secret: {e}. Check your secrets.toml file.")
            raise

    def verify_google_token(self, token):
        """Verify Google ID token and extract user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), self.google_client_id
            )

            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise ValueError("Invalid token issuer.")

            return {
                "email": idinfo["email"],
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "sub": idinfo["sub"],
            }
        except Exception as e:
            st.error(f"Google token verification failed: {str(e)}")
            return None

    def create_firebase_user(self, user_info):
        """Create or retrieve a Firebase user from Google login data"""
        try:
            # Try to get an existing user
            try:
                user = auth.get_user_by_email(user_info["email"])
                return user
            except auth.UserNotFoundError:
                # Create a new user if they don't exist
                user = auth.create_user(
                    email=user_info["email"],
                    display_name=user_info["name"],
                    photo_url=user_info["picture"],
                    uid=f"google_{user_info['sub']}",
                )
                return user
        except Exception as e:
            st.error(f"Error creating Firebase user: {str(e)}")
            return None

    def handle_google_login(self, auth_code):
        """Exchange auth code for tokens and authenticate the user"""
        try:
            token_endpoint = "https://oauth2.googleapis.com/token"
            data = {
                "code": auth_code,
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "redirect_uri": self.google_redirect_uri,
                "grant_type": "authorization_code",
            }

            response = requests.post(token_endpoint, data=data)

            if response.status_code != 200:
                error_details = response.json() if response.content else "No error details available"
                raise Exception(f"Failed to get access token: {error_details}")

            tokens = response.json()
            user_info = self.verify_google_token(tokens.get("id_token"))

            if user_info:
                return self.create_firebase_user(user_info)

            return None
        except Exception as e:
            st.error(f"Unable to complete Google login: {str(e)}")
            return None
