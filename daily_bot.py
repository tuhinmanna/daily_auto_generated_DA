import os
import requests
import datetime
import random
import time

# 1. Setup Config
API_KEY = os.environ["GEMINI_API_KEY"]
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

def get_available_model():
    """Ask Google which models are actually available for this key."""
    url = f"{BASE_URL}/models?key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Get all model names available to you
        available_models = [
            m['name'].replace('models/', '') 
            for m in data.get('models', []) 
            if 'generateContent' in m.get('supportedGenerationMethods', [])
        ]
        
        if not available_models:
            raise Exception("No models found that support content generation.")
            
        # FIXED PRIORITY: Stable models first!
        priority_order = [
            'gemini-1.5-flash', 
            'gemini-1.5-flash-001', 
            'gemini-1.5-flash-002',
            'gemini-1.5-flash-8b',
            'gemini-pro',
            'gemini-1.0-pro',
            'gemini-2.0-flash-exp' # Last resort
        ]
        
        for priority in priority_order:
            if priority in available_models:
                print(f"Auto-selected model: {priority}")
                return priority
                
        # Fallback
        print(f"Auto-selected fallback model: {available_models[0]}")
        return available_models[0]

    except Exception as e:
        print(f"Error listing models: {e}")
        return "gemini-1.5-flash"

def generate_content(model, prompt):
    url = f"{BASE_URL}/models/{model}:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    # Retry logic
    for attempt in range(5):
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        elif response.status_code == 429:
            wait = (attempt + 1) * 10 
            print(f"  Rate limited (429) on {model}. Waiting {wait}s...")
            time.sleep(wait)
        else:
            print(f"  Error {response.status_code}: {response.text}")
            # If 404, we shouldn't retry, just fail
            if response.status_code == 404:
                raise Exception("Model not found (404)")
            time.sleep(5)
            
    raise Exception("Max retries exceeded.")

# 2. Main Logic
topics = ["SQL", "Python Pandas", "Python NumPy", "Data Visualization"]
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
    model_name = get_available_model()
    text = generate_content(model_name, prompt)
    
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    question = f"Error generating content: {e}"
    solution = "# No solution"
    explanation = "Check logs"

# 3. Save to File
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
