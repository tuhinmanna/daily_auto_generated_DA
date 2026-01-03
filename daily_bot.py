import os
import datetime
import google.generativeai as genai
import random

# 1. Setup API
# It will read the key from GitHub Secrets automatically
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. Define the Prompt
# We ask for JSON so it's easy to split into files
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

# 3. Call the AI
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(prompt)
text = response.text

# 4. Parse the response
try:
    question = text.split("QUESTION_START")[1].split("QUESTION_END")[0].strip()
    solution = text.split("SOLUTION_START")[1].split("SOLUTION_END")[0].strip()
    explanation = text.split("EXPLANATION_START")[1].split("EXPLANATION_END")[0].strip()
except IndexError:
    # Fallback if AI formatting breaks (rare)
    question = "Could not generate content today."
    solution = "N/A"
    explanation = "Check logs."

# 5. Create the Folder (YYYY-MM-DD)
today = datetime.date.today().strftime("%Y-%m-%d")
folder_path = os.path.join(os.getcwd(), today)
os.makedirs(folder_path, exist_ok=True)

# 6. Write the Files
# File 1: The Problem
with open(f"{folder_path}/problem.md", "w") as f:
    f.write(f"# Daily {selected_topic} Challenge - {today}\n\n")
    f.write(f"## Question\n{question}\n\n")
    f.write(f"## Explanation\n{explanation}")

# File 2: The Solution (extension depends on topic)
ext = "sql" if "SQL" in selected_topic else "py"
with open(f"{folder_path}/solution.{ext}", "w") as f:
    f.write(solution)

print(f"Successfully created content for {today}")
