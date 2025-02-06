import time
import re
import pandas as pd
from lib.load import load_trie, load_words, load_fingermap
from lib.base_prediction import fingers_to_possible_words, letter_to_finger
from server import predict_sentence_with_infilling
from tqdm import tqdm

def preprocess_dataset(words):
  start_time = time.time()

  df = pd.read_csv("benchmark/topical_chat.csv")

  start_rows = len(df)
  print("Rows before processing:", start_rows)

  df = df.drop(columns=["sentiment", "conversation_id"])
  df = df["message"].to_list()
  df = list(set(df))

  for i in range(len(df)):
    message = df[i]
    message = message.lower()
    message = " ".join(message.split())
    message = message.strip()
    df[i] = message

  removed = 0
  removed_frequencies = {}
  valid_messages = []
  for message in df:
    good = True
    
    for word in message.split(" "):
      word = word.strip(":;.,!?\"()[]{}<>-")

      if word:
        if word.isnumeric():
          continue

        if word not in words:
          removed += 1
          removed_frequencies[word] = removed_frequencies.get(word, 0) + 1

          good = False

    if good:
      message = re.sub(r"\s+(?=[:;.,!?\"()\[\]{}<>-])", "", message)

      valid_messages.append(message)

  df = valid_messages

  print(f"Removed {removed} words from dataset ({len(removed_frequencies.keys())} unique)")

  removed_frequencies = dict(sorted(removed_frequencies.items(), key=lambda item: item[1], reverse=True))

  with open("benchmark/removed_words.txt", "w") as f:
    for word, freq in removed_frequencies.items():
      f.write(f"{word}: {freq}\n")

  df = pd.DataFrame(df, columns=["message"])
  df.to_csv("benchmark/topical_chat-cleaned.csv", index=False)

  end_rows = len(df)
  print(f"Rows after processing: {end_rows} ({(end_rows - start_rows) / start_rows * 100:.2f}%)")

  print(f"Preprocessing took {time.time() - start_time:.2f} seconds")
  
if __name__ == "__main__":
  fingermap = load_fingermap()
  all_words = load_words(fingermap)
  trie = load_trie(all_words)

  # preprocess_dataset(all_words)

  df = pd.read_csv("benchmark/topical_chat-cleaned.csv")

  messages = df["message"].to_list()
  messages = messages[:10]

  start_time = time.time()
  with open("benchmark/log.txt", "w") as f:
    correct_predictions = 0
    correct_words = 0
    total_words = 0
    for message in tqdm( messages , desc="Benchmarking...", unit="message"):
      try:
        template = ""
        words = []

        current_word = ""
        for letter in message + " ":
          if letter == " ":
            if current_word:
              if current_word.isnumeric():
                template += current_word
              else:
                words.append(current_word)
                template += "{}"
              
              current_word = ""
            
            template += " "
          elif letter in ":;.,!?\"()[]{}<>-":
            if current_word:
              if current_word.isnumeric():
                template += current_word
              else:
                words.append(current_word)
                template += "{}"

              current_word = ""
            
            template += letter
          else:
            current_word += letter

        total_words += len(words)

        template = template.strip()

        word_options = []
        for word in words:
          try:
            fingers_for_word = [letter_to_finger(letter, fingermap) for letter in word]
          except KeyError:
            print(f"Skipping word '{word}' due to missing finger mapping.")
            break
          
          possible_words = set()
          for j, finger in enumerate(fingers_for_word):
            possible_words = fingers_to_possible_words(finger, fingermap, trie, possible_words, all_words, j == 0, j == len(fingers_for_word) - 1)

          word_options.append(list(possible_words))

        prediction = predict_sentence_with_infilling(word_options, template=template.strip())

        if prediction == message:
          correct_predictions += 1
          correct_words += len(words)
        else:
          predicted_words = prediction.split(" ")
          incorrect_words_for_prediction = []
          for i, word in enumerate(message.split(" ")):
            if predicted_words[i] != word:
              incorrect_words_for_prediction.append(predicted_words[i])

          correct_words += len(words) - len(incorrect_words_for_prediction)

          f.write(f"Failed at message: {message}\n")
          f.write(f"Prediction: {prediction}\n")
          f.write(f"Incorrect words: {incorrect_words_for_prediction}\n")
          f.write(f"{'-'*40}\n")
      except:
        f.write(f"Error processing message: {message}\n")
        f.write(f"{'-'*40}\n")

  print(f"Word accuracy: {correct_words / total_words * 100:.2f}%")
  print(f"Sentence accuracy: {correct_predictions / len(messages) * 100:.2f}%")
  print(f"Benchmark took {time.time() - start_time:.2f} seconds")