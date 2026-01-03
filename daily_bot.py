import os
import requests
import datetime
import random

# 1. Setup Config
API_KEY = os.environ["GEMINI_API_KEY"]
# We use the REST API directly to avoid library conflicts
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

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

# 3. Call the API (The "Universal" Method)
payload = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status() # Check for HTTP errors
    data = response.json()
    
    # Extract text from the complex JSON response
    text = data['candidates'][0]['content']['parts'][0]['text']

    # 4. Parse the response
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()

except Exception as e:
    # Fallback if something fails
    print(f"Error: {e}")
    if 'response' in locals():
        print(response.text)
    question = "Could not generate content today."
    solution = "N/A"
    explanation = "Check Action logs for error details."

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
