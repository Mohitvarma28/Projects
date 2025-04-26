# EduMentor

**Your AI-Powered Personalized Learning Assistant**

---

## Overview

**EduMentor** is an AI-driven educational assistant designed to personalize learning experiences for students and support educators with adaptive quizzes, learning path generation, and real-time analytics. Built with OpenAI's GPT models, Streamlit, and SerpAPI integration, EduMentor dynamically adapts to user needs, offering tailored quizzes, topic exploration, and intelligent learning guidance.

---

## Features

- **🖊️ Chat Assistant**: GPT-powered real-time conversation to answer queries and guide learning.
- **🔢 Adaptive Quizzes**: Dynamically generated quizzes based on user-selected topics with timers and feedback.
- **💡 Topic Explorer**: Automatically fetches topic summaries and top web resources using SerpAPI.
- **🔹 Personalized Learning Path**: Concept graphs generated for weak topics with prerequisite mapping, importance scoring, and interactive visualizations.
- **🔬 Student Analytics**: Track performance trends, quiz scores, and adaptive learning metrics.

---

## Tech Stack

- **Frontend & Framework**: [Streamlit](https://streamlit.io/)
- **AI Models**: [OpenAI GPT-4](https://openai.com/)
- **Web Search**: [SerpAPI](https://serpapi.com/)
- **Visualization**: PyVis, NetworkX, Matplotlib
- **Backend Utilities**: Python, dotenv, glob, datetime

---

## Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/edumentor.git
cd edumentor
```

2. **Create and Activate Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. **Install Requirements**
```bash
pip install -r requirements.txt
```

4. **Set Up Environment Variables**

Create a `.env` file and add:
```bash
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```
5. **Create a `serviceAccountKey.json` file and add to your firebase folder**

6. **Run the Application**
```bash
python run.py
streamlit run streamlit_ui/main.py (In another terminal)
```

---

## Project Structure

```bash
|-- app.py
|-- pages/
|   |-- Chat Assistant
|   |-- Adaptive Quiz
|   |-- Topic Explorer
|   |-- Learning Path
|-- utils/
|   |-- quiz_generator.py
|   |-- concept_graph.py
|   |-- search_api.py
|-- chat_logs/
|-- Graphs/
|-- README.md
|-- requirements.txt
|-- .env (not committed)
```

---

## Demo Screenshots

| Chat Assistant | Adaptive Quiz | Learning Path |
|:---:|:---:|:---:|
| ![chat](screenshots/chat_assistant.png) | ![quiz](screenshots/adaptive_quiz.png) | ![path](screenshots/learning_path.png) |

---

## Future Improvements

- Integrate spaced repetition for quiz questions.
- Add role-based dashboards for students and teachers.
- Enable saving and downloading of personalized learning reports.
- Add multi-language support.

---


## Acknowledgments

- [OpenAI](https://openai.com/)
- [Streamlit](https://streamlit.io/)
- [SerpAPI](https://serpapi.com/)
- [PyVis](https://pyvis.readthedocs.io/en/latest/)

---

**EduMentor — Empowering Personalized Learning with AI.** 📚🔍

