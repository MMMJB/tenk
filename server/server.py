from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

app = Flask(__name__)
CORS(app)

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
    # If there is no input, set it to BOS token
    if not input_text:
        input_text = tokenizer.bos_token

    # Tokenize input text
    input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)

    # Get model's raw output
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits

    # Get probabilities for the next token
    next_token_logits = logits[0, -1, :]
    
    return torch.softmax(next_token_logits, dim=-1)

def calculate_word_probability(word, token_probabilities):
    # Add spaces before and after the word to treat it as a complete word
    word_with_spaces = f" {word} "
    word_tokens = tokenizer.encode(word_with_spaces, add_special_tokens=False)
    
    prob = 1.0
    for token in word_tokens:
        prob *= token_probabilities[token].item()

    return prob

def predict_next_word(current_text, options):
    if len(options) is 1:
        return options[0]

    token_probabilities = get_next_token_probabilities(current_text)
    word_probabilities = {word: calculate_word_probability(word, token_probabilities) for word in options}
    return max(word_probabilities, key=word_probabilities.get)

def predict_sentence(word_options):
    current_text = ""
    predicted_sentence = []

    for options in word_options:
        next_word = predict_next_word(current_text, options)
        predicted_sentence.append(next_word)
        current_text += " " + next_word

    return " ".join(predicted_sentence)

@app.route("/predict/word", methods=["POST"])
def api_get_next_token_probabilities():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    input_text = data.get("text", "")
    options = data.get("options", "")

    if not options:
        return jsonify({"error": "No options provided"}), 400
    
    token_probabilities = get_next_token_probabilities(input_text)

    word_probabilities = {}
    for word in options:
        word_prob = calculate_word_probability(word, token_probabilities)
        word_probabilities[word] = word_prob

    # Normalize probabilities
    total_prob = sum(word_probabilities.values())
    normalized_probs = {word: prob/total_prob for word, prob in word_probabilities.items()}

    # Sort by probability in descending order
    sorted_words = sorted(normalized_probs.items(), key=lambda x: x[1], reverse=True)

    return jsonify({
        "input_text": input_text,
        "word_probabilities": sorted_words
    })

@app.route("/predict/sentence", methods=["POST"])
def api_get_sentence_probabilities():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    word_options = data.get("word_options", "")

    if not word_options:
        return jsonify({"error": "No word lists provided"}), 400
    
    predicted_sentence = predict_sentence(word_options)

    return jsonify({
        "predicted_sentence": predicted_sentence
    })


@app.route("/ping", methods=["GET"])
def api_ping():
    return jsonify({"response": "pong"})

if __name__ == "__main__":
    app.run(host="http://192.168.1.37:5000", debug=True)