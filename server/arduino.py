from serial import Serial
from pynput.keyboard import Controller, Key
from lib.load import load_trie, load_words, load_fingermap
from lib.base_prediction import fingers_to_possible_sentences, letter_to_finger
from lib.type import type_sequence
from server import predict_sentence

keyboard = Controller()

CONTROL_KEY = 5

def read_serial(comport, baudrate):
  fingermap = load_fingermap()
  words = load_words(fingermap)
  trie = load_trie(words)

  ser = Serial(comport, baudrate, timeout=0.1)

  writing = False
  sequence = []

  try:
    while True:
      data = ser.readline().decode().strip()

      if not data:
        continue

      if not data.isdigit():
        print(f"Invalid digit {data}")
        continue

      data = int(data)

      if data == CONTROL_KEY:
        writing = not writing

        if writing:
          print("Listening for sequence...")
          sequence = []
        else:
          print("Finished listening for sequence. Received:")
          print(sequence)

          possible_words = fingers_to_possible_sentences(sequence, fingermap, trie)
          print("Possible words:", possible_words)
          prediction = predict_sentence(possible_words)
          print("Prediction:", prediction)

          type_sequence(prediction, keyboard, replace=len(prediction))
      elif writing:
        print(data)
        type_sequence([data], keyboard)
        sequence.append(data)

  except KeyboardInterrupt:
    print("Stopped listening to serial output.")
    ser.close()

if __name__ == '__main__':
  read_serial('/dev/cu.usbserial-DN02Z9QE', 9600)
  # fingermap = load_fingermap()
  # words = load_words(fingermap)
  # trie = load_trie(words)

  # sentence = "can i put my balls in your jaws"
  # sequence = [letter_to_finger(letter, fingermap) for letter in sentence]

  # type_sequence(sequence, keyboard)

  # possible_words = fingers_to_possible_sentences(sequence, fingermap, trie, words)
  # prediction = predict_sentence(possible_words)

  # type_sequence(prediction, keyboard, replace=len(prediction))