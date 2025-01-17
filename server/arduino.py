from serial import Serial
from pynput.keyboard import Controller
from lib.load import load_trie, load_words, load_fingermap
from lib.base_prediction import fingers_to_possible_sentences
from lib.type import type_sequence, delete
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
  control = False
  shortcut = False

  def delete_last_char():
    if len(sequence) == 0:
      return

    last = sequence.pop()
    delete(keyboard, len(str(last)))

  shortcuts = {
    10: delete_last_char
  }

  try:
    while True:
      try:
        data = ser.readline().decode().strip()
      except UnicodeDecodeError:
        continue
      
      if data:
        print(data)

      continue

      if not data:
        continue

      key = int(data[:-1])
      inputType = data[-1]
      
      if inputType == "p" and key == CONTROL_KEY:
        control = True
      elif inputType == "r" and key == CONTROL_KEY:
        control = False

      if inputType == "r":
        if not control:
          if key == CONTROL_KEY:
            if shortcut:
              shortcut = False
              continue

            writing = not writing

            if writing:
              print("Listening for sequence...")
              sequence = []
            else:
              print("Finished listening for sequence. Received:")
              print(sequence)

              possible_words = fingers_to_possible_sentences(sequence, fingermap, trie, words)
              print("Possible words:", possible_words)
              prediction = predict_sentence(possible_words)
              print("Prediction:", prediction)

              replace = "".join([str(x) for x in sequence]).__len__()
              type_sequence(prediction, keyboard, replace=replace, capitalize=True)
          elif writing:
            type_sequence([int(x) for x in str(key)], keyboard)
            sequence.append(key)
        else:
          shortcut = True

          if key in shortcuts:
            shortcuts[key]()


  except KeyboardInterrupt:
    print("Stopped listening to serial output.")
    ser.close()

if __name__ == '__main__':
  read_serial('/dev/cu.usbserial-DN02Z9QE', 9600)

