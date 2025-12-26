# ai_engine.py
from google import genai 
import json
import os
import logging

# Configure your API Key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
def get_medical_analysis(symptoms_text):
    model_id = "gemini-2.0-flash"    
    prompt = f"""
    You are a professional Medical Assistant AI. 
    Analyze the following symptoms: "{symptoms_text}"
    
    You MUST return only a valid JSON object with this exact structure:
    {{
        "possible_conditions": [
            {{"name": "Condition Name", "confidence": "0-100%"}}
        ],
        "recommendations": "Detailed medical advice and next steps."
        "is_emergency": "true"/"false"
    }}
    
    Guidelines:
    - If symptoms include chest pain or difficulty breathing, set "is_emergency" to true.
    - Provide recommendations based on standard clinical guidelines. 
    - Do not include any text before or after the JSON.
    """
    
    try:
        # Generate content using the new SDK method
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        # The new SDK provides a clean way to handle text
        json_text = response.text.strip().replace('```json', '').replace('```', '')
        
        return json.loads(json_text)
    except Exception as e:
        logging.info()(f"AI Error: {e}")
        return {
            "error_msg": "Please try again later or consult a professional.",
        }