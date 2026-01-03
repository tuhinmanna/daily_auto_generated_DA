import os
import requests
import datetime
import random

# 1. Setup Config
API_KEY = os.environ["GEMINI_API_KEY"]
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

# The Strategy: Try stable models first.
# If one is busy (429), we instantly skip to the next.
TARGET_MODELS = [
    "gemini-1.5-flash",          # Most stable, fast
    "gemini-1.5-flash-latest",   # Backup alias
    "gemini-1.5-flash-001",      # Specific version
    "gemini-1.5-pro",            # High intelligence backup
    "gemini-2.0-flash-exp"       # Experimental (Last resort only!)
]

def generate_content_rotator(prompt):
    last_error = ""
    
    for model in TARGET_MODELS:
        print(f"Attempting with model: {model}...")
        url = f"{BASE_URL}/models/{model}:generateContent?key={API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        try:
            # We set a timeout so it doesn't hang forever
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"  SUCCESS with {model}!")
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            
            elif response.status_code == 429:
                print(f"  > {model} is busy (Rate Limit). Switching immediately...")
                continue # Try next model in list
            
            elif response.status_code == 404:
                print(f"  > {model} not found/deprecated. Switching...")
                continue
                
            else:
                print(f"  > Error {response.status_code}: {response.text}")
                last_error = f"{response.status_code} - {response.text}"
                continue
                
        except Exception as e:
            print(f"  > Connection Failed: {e}")
            last_error = str(e)
            continue
            
    # If we loop through ALL models and none work
    raise Exception(f"All models failed. Last error: {last_error}")

# 2. Define the Prompt
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

# 3. Execution
try:
    text = generate_content_rotator(prompt)
    
    # 4. Parse the response
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    question = f"Error generating content: {e}"
    solution = "# No solution"
    explanation = "Check logs"

# 5. Save to File
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
