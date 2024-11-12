from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from transformers import pipeline
import logging
import os


app = Flask(__name__)
app.secret_key = "your_secret_key"  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    text_generator = pipeline("text-generation", model="gpt2")
except Exception as e:
    logger.error(f"Error initializing text generation model: {e}")
    text_generator = None

def generate_text(prompt):
    try:
        result = text_generator(prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]
        return result
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return None


@app.route("/")
def index():
    
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
  
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        logger.warning("No prompt provided in the request")
        return jsonify({"error": "No prompt provided"}), 400

  
    generated_text = generate_text(prompt)
    if generated_text is None:
        logger.error("Text generation failed")
        return jsonify({"error": "Text generation failed"}), 500

    logger.info(f"Generated text for prompt '{prompt}': {generated_text}")
    return jsonify({"generated_text": generated_text})

@app.route("/generate_form", methods=["POST"])
def generate_form():
    
    prompt = request.form.get("prompt")
    if not prompt:
        flash("Please enter a prompt", "error")
        return redirect(url_for("index"))

    generated_text = generate_text(prompt)
    if generated_text is None:
        flash("Error generating text, please try again later.", "error")
        return redirect(url_for("index"))

    flash("Text generated successfully!", "success")
    return render_template("index.html", generated_text=generated_text, prompt=prompt)


@app.errorhandler(404)
def page_not_found(e):
   
    logger.warning("404 error - Page not found")
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    # Custom 500 page for server errors
    logger.error("500 error - Internal server error")
    return jsonify({"error": "Internal server error"}), 500


def log_prompt_and_result(prompt, result):
    # Logs generated prompt and result to a file (for audit/logging purposes)
    with open("generation_logs.txt", "a") as log_file:
        log_file.write(f"PROMPT: {prompt}\nRESULT: {result}\n{'-'*50}\n")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
