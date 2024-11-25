from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer, BertForMaskedLM, BertTokenizer
import numpy as np

app = Flask(__name__)
CORS(app)

device = torch.device("cpu")

# Load pre-trained base model and tokenizer
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# Load pre-trained infilling model and tokenizer
infilling_model_name = "bert-base-uncased"
infilling_model = BertForMaskedLM.from_pretrained(infilling_model_name)
infilling_tokenizer = BertTokenizer.from_pretrained(infilling_model_name)

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
    if all(len(sub_options) == 1 for sub_options in word_options):
        return " ".join(sub_options[0] for sub_options in word_options)
    elif not all(len(sub_options) > 1 for sub_options in word_options):
        return predict_sentence_with_infilling(word_options)

    current_text = ""
    predicted_sentence = []

    for options in word_options:
        next_word = predict_next_word(current_text, options)
        predicted_sentence.append(next_word)
        current_text += " " + next_word

    return " ".join(predicted_sentence)

def predict_infilled_words(word_options, suffix=".", max_length=512):
    # Convert word_options to a single input string and collect mask positions
    words = []
    mask_positions = []
    all_word_tokens = []

    for i, sub_options in enumerate(word_options):
        if len(sub_options) == 1:
            words.append(sub_options[0])
        else:
            words.append(infilling_tokenizer.mask_token)
            mask_positions.append(i)
            # Tokenize potential words and store token IDs
            tokenized_options = [infilling_tokenizer.convert_tokens_to_ids(infilling_tokenizer.tokenize(word)) for word in sub_options]
            all_word_tokens.append(tokenized_options)

    text = " ".join(words)
    
    # Prepare the input for BERT
    input_text = f"{text}{suffix}"
    inputs = infilling_tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
    
    # Find the positions of [MASK] tokens
    mask_token_id = infilling_tokenizer.mask_token_id
    mask_token_indices = (inputs['input_ids'][0] == mask_token_id).nonzero(as_tuple=True)[0]

    # Get model output
    with torch.no_grad():
        outputs = infilling_model(**inputs)
        
    logits = outputs.logits[0]
    
    # Process token probabilities
    vocab_size = logits.size(-1)  # Size of the vocabulary
    predictions = []

    for mask_index, word_tokens in zip(mask_token_indices, all_word_tokens):
        # Get probabilities for all tokens
        probs = F.softmax(logits[mask_index], dim=-1)
        
        # Initialize a dictionary to hold combined probabilities
        word_probabilities = {}
        
        for token_ids in word_tokens:
            # Compute the product of probabilities for the tokens
            prob = 1.0
            for token_id in token_ids:
                if token_id < vocab_size:  # Ensure token_id is within vocab size
                    prob *= probs[token_id].item()
            
            word_probabilities[token_ids[0]] = prob

        # Find the token ID with the highest product probability
        best_token_id = max(word_probabilities, key=word_probabilities.get)
        best_prob = word_probabilities[best_token_id]

        # Convert the token ID back to the word
        best_word_token = infilling_tokenizer._convert_id_to_token(best_token_id)
        predictions.append((best_word_token, best_prob))

    highest_prediction = ("", 0)
    highest_prediction_index = 0
    for i, prediction in enumerate(predictions):
        if prediction[1] > highest_prediction[1]:
            highest_prediction = prediction
            highest_prediction_index = i

    # Only replace the most confident token, then rerun the function with the new word list
    highest_prediction_position = mask_positions[highest_prediction_index]
    new_word_options = word_options
    word_options[highest_prediction_position] = [highest_prediction[0]]

    if not all(len(sub_options) == 1 for sub_options in word_options):
        return predict_infilled_words(new_word_options)
    else:
        return new_word_options
    
def predict_sentence_with_infilling(word_options):
    output = predict_infilled_words(word_options)
    output_words = np.array(output).flatten()
    return np.apply_along_axis(" ".join, 0, output_words).tolist()

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
    app.run(host="172.26.196.115", debug=True)