from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer, T5ForConditionalGeneration, T5Tokenizer
import re

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

# Load pre-trained base model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Load pre-trained infilling model and tokenizer
infilling_model_name = "t5-base"
infilling_model = T5ForConditionalGeneration.from_pretrained(infilling_model_name)
infilling_tokenizer = T5Tokenizer.from_pretrained(infilling_model_name)

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
    if len(options) == 1:
        return options[0]

    token_probabilities = get_next_token_probabilities(current_text)
    word_probabilities = {word: calculate_word_probability(word, token_probabilities) for word in options}
    return max(word_probabilities, key=word_probabilities.get)

def predict_sentence(word_options):
    if not all(len(sub_options) > 1 for sub_options in word_options):
        return predict_sentence_with_infilling(word_options)

    current_text = ""
    predicted_sentence = []

    for options in word_options:
        next_word = predict_next_word(current_text, options)
        predicted_sentence.append(next_word)
        current_text += " " + next_word

    return " ".join(predicted_sentence)

def generate_infilled_word_probabilities(word_options, suffix=".", max_length=512):
    # Convert word_options to a single input string
    words = []
    unknown_word_id = 0

    for sub_options in word_options:
        if len(sub_options) == 1:
            words.append(sub_options[0])
        else:
            words.append(f"<extra_id_{unknown_word_id}>")
            unknown_word_id += 1

    text = " ".join(words)
    
    # Prepare the input for T5
    input_text = f"{text}{suffix}"
    inputs = infilling_tokenizer.encode(input_text, return_tensors="pt")

    # Get model output
    with torch.no_grad():
        output = infilling_model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            output_scores=True,
            return_dict_in_generate=True,
            no_repeat_ngram_size=2
        )
        
    generated_ids = output.sequences[0].tolist()
    
    # Process token probabilities
    all_probs = []
    for logits in output.scores:
        probs = F.softmax(logits[0], dim=-1)
        all_probs.append(probs)

    aligned_probs = []
    current_part = ""
    current_probs = []
    for i, token_id in enumerate(generated_ids[1:]):
        token = infilling_tokenizer.decode([token_id])
        if token.startswith("<extra_id_"):
            if current_part:
                aligned_probs.append((current_part.strip(), current_probs))
            current_part = ""
            current_probs = []
        elif i < len(all_probs):
            current_part += token
            current_probs.append(all_probs[i])
    if current_part:
        aligned_probs.append((current_part.strip(), current_probs))

    return aligned_probs

def get_infilled_word_probability(word, probs):
    # Tokenize the word with spaces
    word_with_spaces = f" {word} "
    word_tokens = infilling_tokenizer.encode(word_with_spaces, add_special_tokens=False)

    # ! If the word is split into multiple tokens, we'll use the minimum probability
    word_prob = 1.0
    for i, token_id in enumerate(word_tokens):
        if i < len(probs):
            token_prob = probs[i][token_id].item()
            word_prob = min(word_prob, token_prob)
        else:
            return 0.0 # Return 0 if we don't have enough probability distribution
        
    return word_prob

def predict_infilled_word(options, index, probs):
    if len(options) == 1:
        return options[0]

    word_probabilities = {word: get_infilled_word_probability(word, probs[index][1]) for word in options}
    return max(word_probabilities, key=word_probabilities.get)

def predict_sentence_with_infilling(word_options):
    all_probs = generate_infilled_word_probabilities(word_options)

    predicted_words = []
    for i, sub_options in enumerate(word_options):
        predicted_words.append(predict_infilled_word(sub_options, i, all_probs))

    return " ".join(predicted_words)

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
    app.run(host="0.0.0.0", debug=True)