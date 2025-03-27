import pytesseract
import cv2

def imginp(img):
      imga=cv2.imread(img)
      ocr=pytesseract.image_to_string(img)
      print(ocr)
imginp("imagetext.png")