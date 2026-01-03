import os
import requests
import datetime
import random
import time

# 1. Setup Config
API_KEY = os.environ["GEMINI_API_KEY"]

# List of models to try (in order of preference)
# Since it is 2026, we prioritize 2.0, but keep 1.5 as fallback
MODELS_TO_TRY = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-pro"
]

def generate_content_with_retry(prompt):
    """Tries multiple models until one works"""
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
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status() # Raises error for 404/500
            
            # If successful, return the text
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            print(f"Failed with {model}: {e}")
            last_error = str(e)
            if response.status_code == 404:
                continue # Try next model
            else:
                # If it's a permission/quota error (403/429), waiting might help, 
                # but for now we just try the next model.
                continue
                
    # If all models fail
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
    text = generate_content_with_retry(prompt)
    
    # 4. Parse the response
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    # Fallback content so the file is still created (helpful for debugging)
    question = f"Bot failed to generate content today.\nError details: {e}"
    solution = "# No solution available"
    explanation = "Check GitHub Actions logs."

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
