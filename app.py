from flask import Flask, request, jsonify, render_template
from transformers import pipeline

app = Flask(__name__)


text_generator = pipeline("text-generation", model="gpt2")

def generate_text(prompt):
    return text_generator(prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]


@app.route("/")
def index():
    return render_template("index.html") 

# API route for generating text
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    
    result = generate_text(prompt)
    return jsonify({"generated_text": result})

if __name__ == "__main__":
    app.run(debug=True)
