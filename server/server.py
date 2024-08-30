from flask import Flask, request, jsonify
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)

# # Check if AMD GPU is available
# if torch.backends.rocm.is_available():
#     device = torch.device("rocm")
#     print("Using AMD GPU")
# else:
#     device = torch.device("cpu")
#     print("AMD GPU not available, using CPU")
device = torch.device("cpu")

# Load pre-trained model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

def get_next_token_probabilities(input_text):
    # Tokenize input text
    input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)

    # Get model's raw output
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits

    # Get probabilities for the next token
    next_token_logits = logits[0, -1, :]
    next_token_probs = torch.softmax(next_token_logits, dim=-1)

    # Sort probabilities in descending order
    sorted_probs, sorted_indices = torch.sort(next_token_probs, descending=True)

    # Create a list of (token, probability) tuples
    token_prob_pairs = []
    for prob, idx in zip(sorted_probs, sorted_indices):
        token = tokenizer.decode([idx])
        token_prob_pairs.append((token, prob.item()))

    return token_prob_pairs

@app.route("/predict", methods=["POST"])
def api_get_next_token_probabilities():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    input_text = data.get("text", "")

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400
    
    results = get_next_token_probabilities(input_text)
    # Convert results to a list of dictionaries for JSON serialization
    response_data = [{"token": token, "probability": prob} for token, prob in results]
    return jsonify({"input_text": input_text, "next_tokens": response_data})

@app.route("/ping", methods=["GET"])
def api_ping():
    return jsonify({"response": "pong"})

if __name__ == "__main__":
    app.run(host="192.168.1.37", debug=True)