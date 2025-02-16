import google.generativeai as genai
import os
from datetime import datetime
import streamlit as st

class MedicalAI:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        st.info("Using Google's Gemini Pro model for medical advice")
        
    def is_medical_query(self, text):
        """Check if the query is medical-related"""
        medical_keywords = [
            'pain', 'ache', 'symptoms', 'fever', 'cough', 'headache', 'nausea',
            'dizzy', 'tired', 'sore', 'swelling', 'rash', 'blood', 'breathing',
            'heart', 'stomach', 'chest', 'throat', 'nose', 'ear', 'eye', 'skin',
            'doctor', 'hospital', 'medicine', 'treatment', 'health', 'medical',
            'disease', 'condition', 'diagnosis', 'sick', 'ill', 'injury'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in medical_keywords)

    def get_first_line(self, text):
        """Get the first line or sentence of the text"""
        lines = text.split('\n')
        first_line = lines[0].strip()
        # If first line is too long, truncate it
        return first_line[:100] + '...' if len(first_line) > 100 else first_line



    def get_medical_advice(self, user_input):
        """Get medical advice based on user's health concern description"""
        try:
            if not user_input.strip():
                return "⚠️ Please provide more details about your health concern for a better assessment."

            # Check if query is medical-related
            if not self.is_medical_query(user_input):
                return "⚠️ Please provide health-related concerns or questions."

            # Construct the prompt
            prompt = f"""
            You are a compassionate medical AI assistant. Analyze the following health concern and provide helpful advice.
            Use simple, everyday language and be empathetic in your response.

            Health concern: {user_input}

            Provide a structured response including:
            1. Understanding of the concern
            2. Possible explanations
            3. General recommendations
            4. When to seek medical attention
            5. Additional tips for well-being

            Remember to:
            - Be clear and easy to understand
            - Focus on practical advice
            - Emphasize the importance of professional medical consultation when needed
            """

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    candidate_count=1,
                    max_output_tokens=800
                )
            )
            
            if not response or not response.text:
                return "⚠️ I apologize, but I need more specific information about your health concern to provide helpful advice."

            # Add disclaimer
            disclaimer = """
            
            ⚠️ **Important Note**: This is AI-generated advice and should not replace professional medical consultation.
            If your symptoms are severe or persist, please consult a healthcare provider.
            """

            return response.text.strip() + disclaimer

        except Exception as e:
            return "⚠️ I need more detailed information about your health concern. Please include specific symptoms, their duration, and any relevant medical history."
            
            st.error("No response generated from the AI model")
            return None
        except Exception as e:
            st.error(f"Error generating medical advice: {str(e)}")
            return None

    def save_consultation(self, db, user_id, symptoms, advice):
        """Save consultation to Firebase"""
        if not advice:
            st.error("Cannot save consultation: No advice was generated")
            return None
            
        try:
            # Get the first line of symptoms as title
            title = self.get_first_line(symptoms)
            
            consultation_ref = db.collection('consultations').document()
            consultation_data = {
                'user_id': user_id,
                'title': title,  # Add title field
                'symptoms': symptoms.strip(),
                'advice': advice.strip(),
                'timestamp': datetime.now()
            }
            
            # Verify data before saving
            if all(consultation_data.values()):
                consultation_ref.set(consultation_data)
                st.success("Consultation saved successfully!")
                return consultation_ref.id
            else:
                st.error("Cannot save consultation: Missing required data")
                return None
        except Exception as e:
            st.error(f"Error saving consultation: {str(e)}")
            return None

    def get_user_history(self, db, user_id):
        """Get user's consultation history"""
        try:
            # First attempt: Try with ordering (requires index)
            consultations = db.collection('consultations')\
                .where('user_id', '==', user_id)\
                .order_by('timestamp', direction='DESCENDING')\
                .limit(10)\
                .stream()
            
            return [doc.to_dict() for doc in consultations]
        except Exception as e:
            if 'indexes' in str(e).lower():
                # Fallback: Get without ordering if index doesn't exist
                st.warning("⚠️ Consultation history may not be in chronological order. Creating index...")
                st.markdown("""To fix this:
                1. [Click here to create the required index](https://console.firebase.google.com/project/smarthealtai/firestore/indexes)
                2. Add a composite index for:
                   - Collection: consultations
                   - Fields: user_id (Ascending) and timestamp (Descending)""")
                
                consultations = db.collection('consultations')\
                    .where('user_id', '==', user_id)\
                    .limit(10)\
                    .stream()
                
                # Sort the results in memory
                results = [doc.to_dict() for doc in consultations]
                return sorted(results, key=lambda x: x.get('timestamp', 0), reverse=True)
            else:
                st.error(f"Error fetching consultation history: {str(e)}")
                return []
