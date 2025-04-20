import os
import requests
from bs4 import BeautifulSoup
import json
from serpapi import GoogleSearch
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import os
import requests

def fetch_web_links(topic):
    try:
        api_key = os.getenv("SERP_API_KEY")
        if not api_key:
            print("❌ SERPER_API_KEY not found.")
            return []

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "q": topic,
            "num": 5,
            "gl": "us"
        }

        response = requests.post("https://google.serper.dev/search", json=payload, headers=headers)
        response.raise_for_status()
        results = response.json()

        # Debug print for raw response
        print("🔍 Raw Serper response:", results)

        # Extract links
        links = []
        for r in results.get("organic", []):
            url = r.get("link")
            if url and "http" in url:
                links.append(url)
            if len(links) == 2:
                break

        return links

    except Exception as e:
        print(f"❌ Serper fetch failed: {e}")
        return []

def scrape_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join(p.get_text() for p in paragraphs[:10])
    except Exception:
        return ""

def recommend_learning_path_with_rag(student_summary, weak_topics):
    context_data = ""
    for topic in weak_topics:
        urls = fetch_web_links(topic)
        if urls:
            context_data += f"\n--- {topic.upper()} ---\n" + scrape_url(urls[0])[:1500]

    prompt = f"""
    The student has the following learning summary: {student_summary}
    Weak topics: {', '.join(weak_topics)}
    Use the web content below to suggest 3 personalized topics to study next with rationale and order:

    {context_data}
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def generate_adaptive_quiz(topics, difficulty="medium", num_questions=3):
    prompt = f"""
You are a helpful AI tutor creating a python programming quiz for students. The difficulty is {difficulty}.

Your job is to generate exactly {num_questions} well-formatted multiple-choice questions with exactly 4 options.

Rules:
- All questions must be based ONLY on these topics: {', '.join(topics)}
- Each question must have:
  - A clearly numbered line: Q1:, Q2:, etc.
  - Four answer options labeled exactly as: A. ..., B. ..., C. ..., D. ...
  - A line stating the correct answer, e.g.: Answer: A
  - A short line with explanation, e.g.: Explanation: This is correct because...
  - The questions need to be only theory based and not practical coding based.

⚠️ Do not generate fewer than four options.
⚠️ Do not use bullet points or anything other than A. B. C. D. for options.
⚠️ Do not include any images, diagrams, or code screenshots.
⚠️ Format output as plain text only. Separate each question using "---".

Output example:
Q1: What is correct file extension for Python files?
A. .exe
B. .pyth
C. .java
D. .py
Answer: D
Explanation: .py is correct because...

---

Now create the quiz below:
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
