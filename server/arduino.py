from serial import Serial
from lib.load import load_trie, load_words, load_fingermap
from lib.base_prediction import fingers_to_possible_sentences, letter_to_finger
from server import predict_sentence

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
      elif writing:
        print(data)
        sequence.append(data)

  except KeyboardInterrupt:
    print("Stopped listening to serial output.")
    ser.close()

if __name__ == '__main__':
  read_serial('/dev/cu.usbserial-DN02Z9QE', 9600)
