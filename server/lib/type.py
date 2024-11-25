from pynput.keyboard import Key
from time import sleep

def type_sequence(sequence, keyboard, replace=0):
  for _ in range(replace):
    keyboard.press(Key.backspace)
    keyboard.release(Key.backspace)
  
  for char in sequence:
    keyboard.press(str(char))
    keyboard.release(str(char))
    sleep(0.025)