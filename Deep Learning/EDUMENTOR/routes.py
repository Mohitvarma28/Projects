
from flask import Blueprint, request, jsonify
from app.rag_learning_path import recommend_learning_path_with_rag, generate_adaptive_quiz

api = Blueprint("api", __name__)

@api.route("/learning-path", methods=["POST"])
def learning_path():
    data = request.get_json()
    summary = data.get("summary", "")
    topics = data.get("topics", [])
    if not summary or not topics:
        return jsonify({"error": "Missing input"}), 400
    result = recommend_learning_path_with_rag(summary, topics)
    return jsonify({"recommendation": result})

@api.route("/generate-quiz", methods=["POST"])
def quiz():
    data = request.get_json()
    topics = data.get("topics", [])
    difficulty = data.get("difficulty", "hard")
    num_questions = data.get("num_questions", 3)
    if not topics:
        return jsonify({"error": "Missing topics"}), 400
    result = generate_adaptive_quiz(topics, difficulty, num_questions)
    return jsonify({"quiz": result})
