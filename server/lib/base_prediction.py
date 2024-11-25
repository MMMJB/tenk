import time

def letter_to_finger(letter, fingermap):
  return fingermap[letter]

def finger_to_possible_letters(finger, fingermap):
  return [letter for letter, finger_ in fingermap.items() if finger_ == finger]

def fingers_to_possible_words(finger, fingermap, trie, words, all_words, is_first_letter, is_last_letter):
  possible_letters = finger_to_possible_letters(finger, fingermap)
  
  if is_first_letter:
    return set(possible_letters)
  
  possible_words = set()

  for word in words:
    for possible_letter in possible_letters:
      new_word = word + possible_letter

      if trie.search_trie(new_word):
        possible_words.add(new_word)

  if not is_last_letter:
    return possible_words
  else:
    return possible_words.intersection(all_words)
  
def fingers_to_possible_sentences(fingers, fingermap, trie, all_words):
  SPACE_FINGER = letter_to_finger(" ", fingermap)
  terminating = False

  words = []
  current_word = []

  for finger in fingers:
    if finger == SPACE_FINGER:
      words.append(current_word)
      current_word = []
    else:
      current_word.append(finger)

  words.append(current_word)

  sentence_words = []

  for fingers_for_word in words:
    possible_words = set()
    
    for j, finger in enumerate(fingers_for_word):
      possible_words = fingers_to_possible_words(finger, fingermap, trie, possible_words, all_words, j == 0, j == len(fingers_for_word) - 1)

    if not possible_words:
      terminating = True
      break

    sentence_words.append(possible_words)

  if terminating:
    print("No possible words found.")
    return []
  
  return sentence_words