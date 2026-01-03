import os
import requests
import datetime
import random
import time

# 1. Setup Config
API_KEY = os.environ["GEMINI_API_KEY"]

# Updated Model List for 2026 Stability
# We try the newest first, but fall back to older stable ones
MODELS_TO_TRY = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro"
]

def generate_content_safe(prompt):
    """Tries multiple models with rate-limit handling"""
    last_error = ""
    
    for model in MODELS_TO_TRY:
        print(f"Trying model: {model}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        headers = {"Content-Type": "application/json"}
        
        # Try up to 3 times per model (to handle 429 rate limits)
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    # Success!
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                
                elif response.status_code == 429:
                    # Rate Limited - Wait and retry
                    wait_time = (attempt + 1) * 10 # Wait 10s, then 20s...
                    print(f"  Hit rate limit (429). Sleeping for {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    # Other error (like 404), move to next model
                    print(f"  Failed with status {response.status_code}: {response.text}")
                    last_error = f"{response.status_code} - {response.text}"
                    break # Break inner loop, try next model
                    
            except Exception as e:
                print(f"  Connection error: {e}")
                last_error = str(e)
                break
                
    # If we get here, every single model failed
    raise Exception(f"All models exhausted. Last error: {last_error}")

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
    text = generate_content_safe(prompt)
    
    # 4. Parse the response
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    # Fallback content to ensure file creation
    question = f"Bot failed to generate content today. Check logs."
    solution = "# No solution available"
    explanation = str(e)

# 5. Create the Folder
today = datetime.date.today().strftime("%Y-%m-%d")
folder_path = os.path.join(os.getcwd(), today)
os.makedirs(folder_path, exist_ok=True)

# 6. Write the Files
with open(f"{folder_path}/problem.md", "w") as f:
    f.write(f"# Daily {selected_topic} Challenge - {today}\n\n")
    f.write(f"## Question\n{question}\n\n")
    f.write(f"## Explanation\n{explanation}")

ext = "sql" if "SQL" in selected_topic else "py"
with open(f"{folder_path}/solution.{ext}", "w") as f:
    f.write(solution)

print(f"Successfully created content for {today}")
