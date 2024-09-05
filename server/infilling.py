from transformers import BertTokenizer, BertForMaskedLM# T5ForConditionalGeneration, T5Tokenizer
import torch
import torch.nn.functional as F

model_name = "bert-base-uncased"
infilling_model = BertForMaskedLM.from_pretrained(model_name)
infilling_tokenizer = BertTokenizer.from_pretrained(model_name)

def generate_infilled_word_probabilities(word_options, suffix=".", max_length=512):
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

    highest_prediction_position = mask_positions[highest_prediction_index]
    new_word_options = word_options
    word_options[highest_prediction_position] = [highest_prediction[0]]

    if not all(len(sub_options) == 1 for sub_options in word_options):
        return generate_infilled_word_probabilities(new_word_options)
    else:
        return new_word_options

def main():
    word_options = [
        ["yow", "ups", "how", "hos", "bow", "box", "bps", "now", "nos", "mow", "mos"],
        ["are", "ate", "age", "ace", "ave"],
        ["you", "yob", "yon", "hob", "hon", "joy", "job", "jon", "jpn", "boyo", "bob", "bpm", "blu", "noh", "nob", "non", "mob", "mon", "mom", "mph"],
        ["doing"],
        ["today", "glean", "gleam", "clean"]
    ]
    results = generate_infilled_word_probabilities(word_options)
    print(results)

main()