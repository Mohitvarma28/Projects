import streamlit as st
import requests
import random
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))
from rag_learning_path import fetch_web_links
import glob
import json 
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta
import time
import uuid
from streamlit.components.v1 import html
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_chat import message

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERPER_API_KEY = os.getenv("SERP_API_KEY")

st.set_page_config(page_title="EduMentor", layout="wide")
st.title("EduMentor – Smart Learning Assistant")

st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Choose a page", ["💬 Chat Assistant", "📘 Learning Path", "📚 Topic Explorer", "🧠 Adaptive Quiz", "📊 Student Evaluations"])

# ----------------------------
# 💬 Chat Assistant (Sidebar Panel First)
# ----------------------------
if page == "💬 Chat Assistant":
    # Show saved chats in sidebar first
    with st.sidebar.expander("💾 Saved Chat Logs", expanded=False):
        chat_files = sorted(glob.glob("chat_logs/chat_*.json"))
        if chat_files:
            for idx, file_path in enumerate(chat_files, start=1):
                fname = os.path.basename(file_path)
                dt_str = fname.replace("chat_", "").replace(".json", "")
                try:
                    ts = datetime.strptime(dt_str, "%Y%m%d_%H%M%S").strftime("%b %d, %Y %I:%M %p")
                except:
                    ts = "Unknown time"

                st.markdown(f"**🗂️ Chat {idx} ({ts})**")

                with open(file_path, "r", encoding="utf-8") as f:
                    chat_data = json.load(f)
                    preview = ""
                    for msg in chat_data[-2:]:
                        prefix = "🧑‍🎓" if msg["role"] == "user" else "🤖"
                        preview += f"{prefix} {msg['content'][:80]}...\n"
                    st.text(preview.strip())

                if st.button(f"🔁 Continue Chat {idx}", key=f"continue_{file_path}"):
                    st.session_state.chat_history = chat_data
                    st.session_state.chat_saved = False
                    st.rerun()
                st.markdown("---")

    # Main chat assistant panel
    st.session_state.chat_saved = False
    st.title("💬 Interactive AI Chat Assistant")

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_saved" not in st.session_state:
        st.session_state.chat_saved = False
    if "clear_input_next" not in st.session_state:
        st.session_state.clear_input_next = False
    if "clear_chat_triggered" not in st.session_state:
        st.session_state.clear_chat_triggered = False

    # Display chat history
    for i, msg in enumerate(st.session_state.chat_history):
        is_user = msg["role"] == "user"
        message(msg["content"], is_user=is_user, key=f"chat_msg_{i}")

    # Inline chat input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Type your question here:",
            key="chat_input_bottom",
            label_visibility="visible",
            placeholder="Ask a question..."
        )
        send_clicked = st.form_submit_button("Send")

    # Process message
    if send_clicked and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an intelligent assistant for the EduMentor app. You can answer questions about data science, machine learning, the EduMentor learning paths, quizzes, student progress, and how to use the app features."}
                    ] + st.session_state.chat_history
                )
                reply = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")
        st.session_state.clear_input_next = True
        st.rerun()

    st.markdown("---")
    # Clear chat trigger
    if st.button("🗑️ Clear Current Chat"):
        st.session_state.clear_chat_triggered = True
        st.rerun()

    if st.session_state.clear_chat_triggered:
        st.session_state.chat_history = []
        st.session_state.clear_chat_triggered = False
        st.rerun()

    if page != "💬 Chat Assistant" and st.session_state.get("chat_history") and not st.session_state.get("chat_saved", False):
        os.makedirs("chat_logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"chat_logs/chat_{timestamp}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(st.session_state.chat_history, f, indent=2)
        st.session_state.chat_saved = True

    if page != "💬 Chat Assistant" and "chat_history" in st.session_state:
        st.session_state.chat_history = []

# ----------------------------
# 📘 Learning Path
# ----------------------------
elif page == "📘 Learning Path":
    st.header("📘 Personalized Learning Path")
    summary = st.text_area("Student Summary")
    topics = st.text_input("Weak Topics (comma-separated)", placeholder="e.g., algebra basics, syntax errors")

    if st.button("Generate Learning Path"):
        if not summary or not topics:
            st.warning("Please provide both summary and topics.")
        else:
            response = requests.post(
                "http://localhost:5000/api/learning-path",
                json={"summary": summary, "topics": [t.strip() for t in topics.split(",")]}
            )
            try:
                result = response.json()
                st.markdown("### 📘 Recommended Learning Path:")
                st.markdown(result["recommendation"])
            except Exception as e:
                st.error(f"Error: {e}")
                st.code(response.text)

# ----------------------------
# 🧠 Adaptive Quiz
# ----------------------------
elif page == "🧠 Adaptive Quiz":
    st.header("🧠 Adaptive Quiz Generator")

    student_name = st.text_input("Enter your name for this quiz attempt")

    # Topic input
    st.text_input("Enter one or more quiz topics (comma-separated):", key="topic_input", placeholder="e.g., CNN, Reinforcement Learning, LSTMs")
    raw_input = st.session_state.get("topic_input", "")
    selected_topics = [t.strip() for t in raw_input.split(",") if t.strip()]

    # Initialize session state
    for key in ["quiz_confirmed", "quiz_generated", "quiz_questions", "quiz_answers", "quiz_submitted", "quiz_saved", "quiz_timer_start"]:
        if key not in st.session_state:
            st.session_state[key] = False if key != "quiz_questions" and key != "quiz_answers" else ([] if key == "quiz_questions" else {})

    # Detect JS-triggered auto-submit
    if st.session_state.quiz_confirmed and st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        if "autosubmit" in st.query_params:
            st.session_state.quiz_submitted = True
            st.session_state.quiz_saved = False

    # Confirm Topics
    if st.button("✅ Confirm Topics and Start Quiz", key="confirm_topics"):
        if not selected_topics:
            st.warning("⚠️ Please enter at least one topic before starting the quiz.")
        else:
            st.session_state.quiz_confirmed = True
            st.session_state.quiz_generated = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_saved = False

    # Generate Quiz
    if st.session_state.quiz_confirmed and selected_topics and not st.session_state.quiz_generated:
        try:
            response = requests.post(
                "http://localhost:5000/api/generate-quiz",
                json={"topics": selected_topics, "difficulty": random.choice(["Easy", "Medium", "Hard"]), "num_questions": 10}
            )
            result = response.json()
            st.session_state.raw_quiz = result["quiz"]
            st.session_state.quiz_questions = [q.strip() for q in result["quiz"].split("---") if q.strip()]
            st.session_state.quiz_generated = True
            st.session_state.quiz_timer_start = datetime.now()
        except Exception as e:
            st.error("Quiz generation failed.")
            st.exception(e)

    if st.session_state.quiz_timer_start and st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        html(f"""
        <div id="timer-container" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #000;
            color: #fff;
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            padding: 20px 0;
            z-index: 9999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.5);
            font-family: 'Segoe UI', sans-serif;">
            ⏳ Time left: <span id="time-display">10:00</span>
            <div style="margin-top: 10px; height: 14px; background: #555; width: 80%;
                        margin-left: auto; margin-right: auto; border-radius: 8px; overflow: hidden;">
                <div id="progress-bar" style="height: 100%; width: 100%; background: #ffcc00;"></div>
            </div>
        </div>

        <form id="auto-submit-form"><input type="hidden" name="autosubmit" value="1"/></form>

        <script>
            let duration = 600;
            let endTime = Date.now() + duration * 1000;

            function updateTimer() {{
                const now = Date.now();
                const timeLeft = Math.max(0, endTime - now);
                const secondsLeft = Math.floor(timeLeft / 1000);
                const minutes = Math.floor(secondsLeft / 60);
                const seconds = secondsLeft % 60;
                const formatted = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
                document.getElementById("time-display").innerText = formatted;

                const progress = Math.max(0, (timeLeft / (duration * 1000)) * 100);
                document.getElementById("progress-bar").style.width = progress + "%";

                if (timeLeft > 0) {{
                    requestAnimationFrame(updateTimer);
                }} else {{
                    document.getElementById("timer-container").innerText = "⏰ Time is up! Auto-submitting...";
                    document.forms["auto-submit-form"].submit();
                }}
            }}

            requestAnimationFrame(updateTimer);
        </script>
        """, height=100)
        st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)


    # 📝 Render Quiz
    if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
        st.markdown("### 📝 Your Adaptive Quiz:")
        for i, qblock in enumerate(st.session_state.quiz_questions, 1):
            lines = qblock.strip().split("\n")
            question_line = lines[0]
            options = lines[1:5]
            answer_line = next((l for l in lines if l.lower().startswith("answer:")), "")
            explanation_line = next((l for l in lines if l.lower().startswith("explanation:")), "")
            correct_answer = answer_line.split(":")[-1].strip()

            st.markdown(f"**Q{i}:** {question_line.replace(f'Q{i}:', '').strip()}")
            selected = st.radio("Choose your answer:", options, key=f"q{i}_option", index=None, label_visibility="collapsed")

            st.session_state.quiz_answers[f"q{i}"] = {
                "selected": selected,
                "correct": correct_answer,
                "explanation": explanation_line
            }

        if st.button("Submit Quiz", key="submit_quiz") and not st.session_state.quiz_submitted:
            if not student_name.strip():
                st.warning("Please enter your name before submitting.")
            else:
                st.session_state.quiz_submitted = True

    # ✅ Save Results
    def save_quiz_result(name, score, total, answers):
        result = {
            "name": name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score,
            "total": total,
            "answers": answers
        }
        filepath = os.path.join(os.path.dirname(__file__), "student_quiz_attempts.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(result)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    # ✅ Results
    if st.session_state.quiz_submitted and not st.session_state.quiz_saved:
        score = 0
        for i in range(1, len(st.session_state.quiz_questions) + 1):
            answer = st.session_state.quiz_answers.get(f"q{i}", {})
            selected = answer.get("selected", None)
            correct = answer.get("correct", "")
            if not selected:
                continue
            user_answer = selected.split(".")[0].strip()
            if user_answer == correct:
                score += 1
        save_quiz_result(student_name, score, len(st.session_state.quiz_questions), st.session_state.quiz_answers)
        st.session_state.quiz_saved = True

    if st.session_state.quiz_submitted:
        st.markdown("### ✅ Quiz Results")
        score = 0
        for i in range(1, len(st.session_state.quiz_questions) + 1):
            answer = st.session_state.quiz_answers.get(f"q{i}", {})
            selected = answer.get("selected", None)
            correct = answer.get("correct", "")
            explanation = answer.get("explanation", "")
            if not selected:
                st.warning(f"Q{i}: No answer selected.")
                continue
            user_answer = selected.split(".")[0].strip()
            if user_answer == correct:
                score += 1
                st.success(f"Q{i}: Correct ✅")
            else:
                st.error(f"Q{i}: Incorrect ❌ | Correct Answer: {correct}")
            st.info(explanation)

        st.markdown(f"### 🏁 Final Score: **{score} / {len(st.session_state.quiz_questions)}**")

        if st.button("Finish", key="finish_quiz"):
            for key in ["raw_quiz", "quiz_questions", "quiz_answers", "quiz_submitted", "quiz_saved", "quiz_generated", "quiz_timer_start", "quiz_confirmed"]:
                st.session_state.pop(key, None)
            st.rerun()

# ----------------------------
# 📊 Student Evaluations
# ----------------------------
elif page == "📊 Student Evaluations":
    st.header("📊 Student Quiz Attempts")

    filepath = os.path.join(os.path.dirname(__file__), "student_quiz_attempts.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        student_names = sorted(str(name) for name in df["name"].unique())
        selected_name = st.selectbox("Filter by student name:", ["All"] + student_names)

        if selected_name != "All":
            df = df[df["name"] == selected_name]

        st.dataframe(df[["name", "timestamp", "score", "total"]])

        st.subheader("📊 Score Trend Over Time")
        st.line_chart(df.set_index("timestamp")[["score"]])

        st.subheader("📊 Total Scores")
        st.bar_chart(df["score"])
    else:
        st.info("No quiz attempts found yet.")

# ----------------------------
# 📚 Topic Explorer
# ----------------------------
elif page == "📚 Topic Explorer":
    st.header("📚 Topic Explorer – Learn Before You Quiz")

    raw_input = st.text_input("Enter one or more topics to explore (comma-separated):", placeholder="e.g., Support Vector Machines, GANs, Deep Learning")

    selected = [t.strip() for t in raw_input.split(",") if t.strip()]

    def get_gpt_summary(topic):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful tutor specialised in all the technical domains."},
                    {"role": "user", "content": f"Give a 6-8 sentence description about '{topic}' in respective domain for students, including a technical and non-technical explanation."}
                ]
            )
            return response.choices[0].message.content
        except Exception:
            return "AI summary unavailable."

    for topic in selected:
        st.subheader(f"🔹 {topic}")
        with st.spinner("Generating AI summary..."):
            summary = get_gpt_summary(topic)
        st.markdown(f"**🧠 AI Summary:** {summary}")

        with st.spinner("🔗 Fetching web links..."):
            web_links = fetch_web_links(topic)
            import logging
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            logging.debug(f"🔍 Fetched links for topic '{topic}': {web_links}")

        if web_links:
            st.markdown("**📘 External Resources:**")
            for i, link in enumerate(web_links, 1):
                st.markdown(f"- **Source {i}:** [{link}]({link})")
        else:
            st.warning("⚠️ No relevant web links found.")
