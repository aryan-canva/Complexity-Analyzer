from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    code = data.get("code", "").strip()
    language = data.get("language", "C++")

    if not code:
        return jsonify({"error": "No code provided"}),400
    
    prompt = f"""Analyze the time and space complexity of this {language} code.
 
Code:
```{language}
{code}
```
 
Respond ONLY with a JSON object, no markdown fences, no preamble. Use this exact schema:
{{
  "time_complexity": "O(...)",
  "space_complexity": "O(...)",
  "time_case": "best/average/worst",
  "short_verdict": "one sentence verdict on efficiency",
  "explanation": "2-3 sentence plain English explanation of why these complexities",
  "breakdown": [
    {{"line": "line or block description", "contribution": "what complexity it adds and why"}}
  ],
  "optimization_tip": "one concrete tip to improve complexity if possible, or Already optimal. if not"
}}"""
    
    try:
        message = client.messages.create(
            model = "claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role" : "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        clean = raw.replace("```json","").replace("```","").strip()

        import json
        parsed = json.loads(clean)
        return jsonify(parsed)
    
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response"}),500
    except Exception as e:
        return jsonify({"error": str(e)}),500
    
@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True,port=5000)
