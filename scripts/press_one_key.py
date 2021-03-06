# SCRIPT TO PRESS KEYS ON WINDOWS
# Create by: Ney Moresco
# Date: 2021-11-03

import time, random

# Import keyboard package, if not installed will download
try:
    import keyboard
except:
    import os
    os.system("pip install keyboard")
    import keyboard

# Function to exit script if user presses "esc"
def quit_script(seconds):
    startTime = time.time()
    while time.time() - startTime < seconds:
        if keyboard.is_pressed("esc"):
            return True
    return False

# Get key
print("Press the key you want to press in the script:")
key_stroke = keyboard.read_key()

# Print instructions in the console
print('Remember, to stop the script press the "Esc" key, the script will starts in 10 seconds...')

# Wait 10 seconds 
time.sleep(10)

# Loop
while True:
    keyboard.press_and_release(key_stroke)
    if quit_script(random.sample(range(4,8),1)[0]):
        break
