from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import torch.nn.functional as F

model_name = "t5-base"
infilling_model = T5ForConditionalGeneration.from_pretrained(model_name)
infilling_tokenizer = T5Tokenizer.from_pretrained(model_name)

def generate_infilled_word_probabilities(word_options, max_length=512):
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
    input_text = f"infill: {text}."
    inputs = infilling_tokenizer(input_text, return_tensors="pt", truncation=True, max_length=max_length)

    # Get model output
    with torch.no_grad():
        output = infilling_model.generate(
            inputs['input_ids'],
            max_length=max_length,
            num_return_sequences=1,
            output_scores=True,
            return_dict_in_generate=True
        )
    
    # # Decode the output
    generated_ids = output.sequences[0].tolist()
    # decoded_output = infilling_tokenizer.decode(generated_ids, skip_special_tokens=False)
    
    # # Extract the infilled parts
    # infilled_parts = re.findall(r'<extra_id_\d+>\s*(.*?)\s*(?=<extra_id_\d+>|$)', decoded_output)
    
    # # Replace the masks in the original text with the infilled parts
    # result = text
    # for i, part in enumerate(infilled_parts):
    #     result = result.replace(f'<extra_id_{i}>', part, 1)
    
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
    if len(options) is 1:
        return options[0]

    word_probabilities = {word: get_infilled_word_probability(word, probs[index][1]) for word in options}
    return max(word_probabilities, key=word_probabilities.get)

word_options = [
    ["yow", "ups", "how", "hos", "bow", "box", "bps", "now", "nos", "mow", "mos"],
    # ["are", "ate", "age", "ace", "ave"],
    ["are"],
    ["you", "yob", "yon", "hob", "hon", "joy", "job", "jon", "jpn", "boyo", "bob", "bpm", "blu", "noh", "nob", "non", "mob", "mon", "mom", "mph"],
    ["doing"],
    ["today", "glean", "gleam", "clean"]
]
all_probs = generate_infilled_word_probabilities(word_options)
print(len(all_probs))
for i, sub_options in enumerate(word_options):
    print(predict_infilled_word(sub_options, i, all_probs))
    