from pynput.keyboard import Key
from time import sleep

def type_sequence(sequence, keyboard, replace=0, capitalize=False):
  for _ in range(replace):
    keyboard.press(Key.backspace)
    keyboard.release(Key.backspace)
  
  for i, char in enumerate(sequence):
    if capitalize and i == 0:
      keyboard.press(Key.shift)
      keyboard.press(str(char))
      keyboard.release(str(char))
      keyboard.release(Key.shift)
    else:
      keyboard.press(str(char))
      keyboard.release(str(char))
    
    sleep(0.025)

def delete(keyboard, times=1, delay=False):
  for _ in range(times):
    keyboard.press(Key.backspace)
    keyboard.release(Key.backspace)

    if delay:
      sleep(0.025)