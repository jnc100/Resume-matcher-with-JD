import os
import requests
from dotenv import load_dotenv
load_dotenv()
HF_Token=os.getenv('HF_API_KEY')
def llm_match_resume(resume_text,job_description):
   prompt=f"""
Compare the resume below with the job description.
Provide:
1. A macth score (0-100)
2.Mtached Skills 
3. Missing Skills
4.Suggestions

Resume:
{resume_text}

Job Description:
{job_description}
"""

   headers={
      "Authorization":f"Bearer{HF_Token}",
      "Content-type":"application/json"
   }
   response=requests.post(
      "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
      headers=headers,
      json={"inputs":prompt}
      )
    
   try:
     return response.json()[0]["generated_text"]
   except:
      return str(response.json())
   
     
    

