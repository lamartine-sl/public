holes = [-7,-14]

def calc_strokes(holes):
    if min(holes) < 0:
        total_holes = 18 if abs(min(holes)) > 9 else 9
        return [0 if -x-1 in holes else -1 for x in range(total_holes)]
    else:
        total_holes = 18 if max(holes) > 9 else 9
        return [-1 if x+1 in holes else 0 for x in range(total_holes)]

calc_strokes([-19])


def calc_press(p1, p2):
    games = [0]
    result = [0 if p1 == p2 else 1 if p1 < p2 else -1 for p1, p2 in zip(p1,p2)]
    for x in result:
        games = [x + y for y in games]
        if abs(games[len(games)-1]) > 1:
            games += [0]
    return games

v1 = [8,4,3,3,5,5,4,4,2]
v2 = [5,3,3,4,4,5,5,5,3]
calc_press(v1,v2)


def calc_press_pairs(p1,p2,p3,p4):
    games = [0]
    result_pair = [0 if p1 + p2 == p3 + p4 else 1 if p1 + p2 < p3 + p4 else -1 for p1, p2, p3,p4 in zip(p1,p2,p3,p4)]
    result_best_score = [0 if min(p1,p2) == min(p3,p4) else 1 if min(p1,p2) < min(p3,p4) else -1 for p1, p2, p3,p4 in zip(p1,p2,p3,p4)]
    for x,y in zip(result_pair, result_best_score):
        games = [x + z for z in games]
        if abs(games[len(games)-1]) > 3:
            games += [0]
        games = [y + z for z in games]
        if abs(games[len(games)-1]) > 3:
            games += [0]

    return games

p1 = [8,4,3,3,5,5,4,4,2]
p2 = [5,3,3,4,4,5,5,5,3]
p3 = [5,3,3,4,4,5,5,6,3]
p4 = [5,5,5,4,5,6,5,4,3]
calc_press_pairs(p1,p2,p3,p4)



import cv2
from PIL import ImageGrab
import pytesseract
import numpy as np
def imToString():
    # Path of tesseract executable
    pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'
    while(True):
  
        # ImageGrab-To capture the screen image in a loop. 
        # Bbox used to capture a specific area.
        cap = ImageGrab.grab(bbox = (700,0,1920,30))
  
        # Converted the image to monochrome for it to be easily 
        # read by the OCR and obtained the output String.
        tesstr = pytesseract.image_to_string(cv2.cvtColor(np.array(cap), cv2.COLOR_BGR2GRAY), lang ='eng')
        print(tesstr)
  
# Calling the function
imToString()
