import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from analyzers import analyze_all
from ml.quality_model import predict_quality

app = Flask(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
SYSTEM_PROMPT = (
    "You are Lyra, a friendly AI from the Cognitive Code Intelligence suite. "
    "Answer coding and complexity questions clearly, concisely, and stay on topic with software analysis."
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyAiIXYYMcdr6tVfzQOSuKO3ze5dru6iEok"


def get_chat_response(conversation):
    if not GEMINI_API_KEY:
        return "Gemini API key missing. Set GEMINI_API_KEY in your environment to chat with me."

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        contents = []
        
        # Prepend system prompt as first user message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=SYSTEM_PROMPT)],
            )
        )
        
        for item in conversation:
            role = item.get("role", "user")
            content = (item.get("content") or "").strip()
            if not content:
                continue
            mapped_role = "user" if role == "user" else "model"
            contents.append(
                types.Content(
                    role=mapped_role,
                    parts=[types.Part.from_text(text=content)],
                )
            )
        
        if not contents or len(contents) == 1:
            return "Please share a message so I can help."
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents
        )
        
        return response.text if response.text else "I'm still thinking—could you rephrase that?"

    except Exception as e:
        app.logger.error("Gemini API error: %s", str(e))
        return f"Gemini error: {str(e)[:100]}"
   

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    code_input = ""
    problem_input = ""
    language = "python"

    if request.method == "POST":
        code_input = request.form.get("code", "")
        problem_input = request.form.get("problem", "")
        language = request.form.get("language", "python").lower()

        result = analyze_all(code_input, problem_statement=problem_input, language=language)

        # 🔥 ML Integration (Added Layer)
        if result:
            quality = predict_quality(result, code_input)
            result["ml_quality"] = quality

    return render_template(
        "index.html",
        result=result,
        code_input=code_input,
        problem_input=problem_input,
        language=language
    )


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    conversation = []
    for item in history:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role not in {"user", "assistant"} or not content:
            continue
        conversation.append({
            "role": role,
            "content": content
        })

    if not conversation and message:
        conversation.append({"role": "user", "content": message})

    if not conversation:
        return jsonify({"reply": "Please share a message so I can help."}), 400

    reply = get_chat_response(conversation)
    return jsonify({"reply": reply})


@app.route("/execute", methods=["POST"])
def execute():
    from executor.code_runner import run_python_code
    from executor.java_executor import run_java
    from executor.c_executor import run_c
    from executor.cpp_executor import run_cpp
    from executor.js_executor import run_js
    
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    language = (data.get("language") or "python").lower()

    if not code:
        return jsonify({"error": "No code provided"}), 400

    if language == "python":
        result = run_python_code(code)
    elif language == "java":
        result = run_java(code)
    elif language == "c":
        result = run_c(code)
    elif language == "cpp":
        result = run_cpp(code)
    elif language == "js":
        result = run_js(code)
    else:
        return jsonify({"error": f"Language '{language}' execution not supported yet. Only Python, Java, C, C++, and JavaScript are supported."}), 400
    return jsonify({
        "output": result.get("output"),
        "error": result.get("error")
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
