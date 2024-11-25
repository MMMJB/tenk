import json
import time
from lib.trie import Trie

def load_fingermap():
  with open("../src/static/base-fingermap.json") as f:
    fingermap = json.load(f)

  return fingermap

def load_words(fingermap):
  with open("../public/words.txt") as f:
    words = f.read().lower().split()

  words = [word for word in words if all(char in fingermap for char in word)]

  words = set(words)

  return words

def load_trie(words):
  start_time = time.time()
  print("Loading words...")

  trie = Trie.build_trie(list(words))

  end_time = time.time()
  print(f"Loaded {len(words)} words in {end_time - start_time:.2f}s.")

  return trie