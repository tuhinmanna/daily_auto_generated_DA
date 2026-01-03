import os
import requests
import datetime
import random
import time
import json

# 1. Setup
API_KEY = os.environ["GEMINI_API_KEY"]
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def get_valid_model():
    """
    Connects to Google to find out EXACTLY which models 
    are available for this specific API Key.
    """
    url = f"{BASE_URL}/models?key={API_KEY}"
    print(f"Checking available models from: {BASE_URL}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"FATAL: Could not list models. Error: {e}")
        # Last ditch hardcoded attempt if listing fails
        return "gemini-2.0-flash-exp"

    # Filter for models that can generate content
    valid_models = []
    for m in data.get('models', []):
        name = m['name'].replace('models/', '')
        if 'generateContent' in m.get('supportedGenerationMethods', []):
            valid_models.append(name)
    
    if not valid_models:
        raise Exception("No Content Generation models found for this API Key.")
    
    print(f"SUCCESS. Found these valid models: {valid_models}")
    
    # Strategy: Pick the first one that ISN'T 'pro-vision' (which requires images)
    # We prefer 'flash' models if available.
    preferred = [m for m in valid_models if 'flash' in m]
    if preferred:
        return preferred[0]
    
    return valid_models[0]

def generate_with_patience(model, prompt):
    url = f"{BASE_URL}/models/{model}:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    # We will try 3 times, with LONG waits (Experimental models need this)
    # Wait times: 20s, 60s, 120s
    waits = [20, 60, 120]
    
    for i, wait_time in enumerate(waits):
        print(f"Attempt {i+1} with {model}...")
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            
            elif response.status_code == 429:
                print(f"  > Rate Limited (429). Server is busy.")
                print(f"  > Sleeping for {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"  > Error {response.status_code}: {response.text}")
                # If it's a 500 error (Server Error), we retry. 
                # If it's a 400 (Bad Request), we stop.
                if response.status_code >= 500:
                    time.sleep(wait_time)
                    continue
                break
                
        except Exception as e:
            print(f"  > Network Error: {e}")
            time.sleep(wait_time)
            
    raise Exception("Max retries exceeded. The model is too busy right now.")

# 2. Main Logic
topics = ["SQL", "Python", "Interview Data Analytics Question"]
selected_topic = random.choice(topics)

prompt = f"""
Act as a Senior Data Analyst Interviewer.
Generate a unique, popular interview question about {selected_topic}.
The output must be strictly in this format (no other text):

QUESTION_START
(Write the problem statement here. If it is SQL, describe the table schema. If Python, describe the input dataframe.)
QUESTION_END

SOLUTION_START
(Write the correct code query or script here.)
SOLUTION_END

EXPLANATION_START
(Briefly explain how the solution works.)
EXPLANATION_END
"""

try:
    # A. Dynamic Model Selection
    model_name = get_valid_model()
    print(f"Selected Model: {model_name}")
    
    # B. Generate
    text = generate_with_patience(model_name, prompt)
    
    # C. Parse
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    # Fallback to create files so workflow doesn't turn red
    question = f"Generation failed. Check logs for details.\nError: {e}"
    solution = "# No solution"
    explanation = "See Action logs."

# 3. Save
today = datetime.date.today().strftime("%Y-%m-%d")
folder_path = os.path.join(os.getcwd(), today)
os.makedirs(folder_path, exist_ok=True)

with open(f"{folder_path}/problem.md", "w") as f:
    f.write(f"# Daily {selected_topic} Challenge - {today}\n\n")
    f.write(f"## Question\n{question}\n\n")
    f.write(f"## Explanation\n{explanation}")

ext = "sql" if "SQL" in selected_topic else "py"
with open(f"{folder_path}/solution.{ext}", "w") as f:
    f.write(solution)

print(f"Job finished for {today}")
