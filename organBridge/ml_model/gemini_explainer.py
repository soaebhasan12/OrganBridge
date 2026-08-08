import urllib.request
import urllib.error
import json
from django.conf import settings


class GeminiMatchExplainer:

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def _call_groq(self, prompt):
        try:
            import requests
            response = requests.post(
                self.url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.7
                },
                timeout=15
            )
            result = response.json()
            print(f"Groq Response: {result}")  # debug line
            return result['choices'][0]['message']['content'].strip()

        except Exception as e:
            print(f"Groq Error: {type(e).__name__}: {e}")
            return None    
    
    def explain_match(self, donor, recipient, match_data):
        try:
            prompt = f"""You are a medical AI for OrganBridge organ matching platform.
Explain in 2-3 sentences why this donor-recipient pair has a {match_data['final_score']}% compatibility score. Be specific about the exact factors.

DONOR: Blood {donor.user.blood_type}, Age {donor.user.age}, City {donor.user.city}, Health {donor.health_status}, Smoking {donor.smoking_status}, Organs {', '.join(donor.organs_donating)}, BMI {donor.bmi or 'N/A'}
RECIPIENT: Blood {recipient.user.blood_type}, Age {recipient.user.age}, City {recipient.user.city}, Urgency {recipient.urgency_level}, Needs {', '.join(recipient.organs_needed)}
MATCH: Score {match_data['final_score']}%, Blood Compatible {match_data['blood_compatible']}, Same City {donor.user.city == recipient.user.city}

Give a unique, specific explanation mentioning exact values. If score is low, mention limiting factors."""

            result = self._call_groq(prompt)
            if result:
                return result
            return f"This donor shows {match_data['final_score']}% compatibility based on blood type, location, and medical factors."

        except Exception as e:
            print(f"Explainer error: {e}")
            return f"This donor shows {match_data['final_score']}% compatibility based on blood type, location, and medical factors."

    def explain_bias_report(self, audit_results):
        try:
            prompt = f"""You are an AI fairness expert. Explain this bias audit in 2-3 simple sentences for a medical administrator.

Overall Fairness: {audit_results['overall_fairness_score']}/100
Gender Bias: {audit_results['gender_bias']['fairness_score']}/100
Age Bias: {audit_results['age_bias']['fairness_score']}/100
Location Bias: {audit_results['location_bias']['fairness_score']}/100
Total Matches: {audit_results['total_matches']}"""

            result = self._call_groq(prompt)
            if result:
                return result
            return "Bias analysis complete. Review individual scores for detailed insights."

        except Exception:
            return "Bias analysis complete. Review individual scores for detailed insights."


























# import urllib.request
# import urllib.error
# import json
# from django.conf import settings


# class GeminiMatchExplainer:

#     def __init__(self):
#         self.api_key = settings.GEMINI_API_KEY
#         self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

#     def _call_gemini(self, prompt):
#         try:
#             data = json.dumps({
#                 "contents": [{"parts": [{"text": prompt}]}]
#             }).encode('utf-8')

#             req = urllib.request.Request(
#                 self.url,
#                 data=data,
#                 headers={'Content-Type': 'application/json'},
#                 method='POST'
#             )

#             with urllib.request.urlopen(req, timeout=20) as response:
#                 result = json.loads(response.read().decode('utf-8'))
#                 return result['candidates'][0]['content']['parts'][0]['text'].strip()

#         except urllib.error.HTTPError as e:
#             print(f"Gemini HTTP Error: {e.code} - {e.read().decode('utf-8')}")
#             return None
#         except urllib.error.URLError as e:
#             print(f"Gemini URL Error: {e.reason}")
#             return None
#         except Exception as e:
#             print(f"Gemini General Error: {type(e).__name__}: {e}")
#             return None

#     def explain_match(self, donor, recipient, match_data):
#         try:
#             prompt = f"""
# You are a medical AI for OrganBridge organ matching platform.
# Explain in 2-3 sentences why this donor-recipient pair has a {match_data['final_score']}% compatibility score. Be specific about the exact factors.

# DONOR: Blood {donor.user.blood_type}, Age {donor.user.age}, City {donor.user.city}, Health {donor.health_status}, Smoking {donor.smoking_status}, Organs {', '.join(donor.organs_donating)}, BMI {donor.bmi or 'N/A'}
# RECIPIENT: Blood {recipient.user.blood_type}, Age {recipient.user.age}, City {recipient.user.city}, Urgency {recipient.urgency_level}, Needs {', '.join(recipient.organs_needed)}
# MATCH: Score {match_data['final_score']}%, Blood Compatible {match_data['blood_compatible']}, Same City {donor.user.city == recipient.user.city}

# Give a unique, specific explanation mentioning exact values. If score is low, mention limiting factors.
# """
#             result = self._call_gemini(prompt)
#             if result:
#                 return result
#             return f"This donor shows {match_data['final_score']}% compatibility based on blood type, location, and medical factors."

#         except Exception as e:
#             print(f"Gemini error: {e}")
#             return f"This donor shows {match_data['final_score']}% compatibility based on blood type, location, and medical factors."

#     def explain_bias_report(self, audit_results):
#         try:
#             prompt = f"""
# You are an AI fairness expert. Explain this bias audit in 2-3 simple sentences for a medical administrator.

# Overall Fairness: {audit_results['overall_fairness_score']}/100
# Gender Bias: {audit_results['gender_bias']['fairness_score']}/100
# Age Bias: {audit_results['age_bias']['fairness_score']}/100
# Location Bias: {audit_results['location_bias']['fairness_score']}/100
# Total Matches: {audit_results['total_matches']}
# """
#             result = self._call_gemini(prompt)
#             if result:
#                 return result
#             return "Bias analysis complete. Review individual scores for detailed insights."

#         except Exception:
#             return "Bias analysis complete. Review individual scores for detailed insights."