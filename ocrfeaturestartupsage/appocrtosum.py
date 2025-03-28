from flask import Flask, request, render_template
import os
import requests
import pytesseract
import cv2
from PIL import Image
from docx import Document
import pdfplumber

# Cohere API Details
API_KEY = "nAylv2Qh78wLh7CWl6Z9NqVvbxuSanV01IyeyEQv"  # Replace with your actual Cohere API key
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Flask app setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def summarize_text(text):
    """Summarizes text using Cohere's API (requires 250+ characters)."""
    if len(text) < 250:
        text = text * (250 // len(text) + 1)  # Repeat text to meet length requirement
    
    data = {"text": text[:1000], "length": "medium"}  # Cohere's API max input limit
    response = requests.post("https://api.cohere.ai/v1/summarize", json=data, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("summary", "Summarization failed.")
    else:
        return f"Error summarizing text: {response.text}"

@app.route("/", methods=["GET", "POST"])
def upload_file():
    extracted_text = ""  
    summarized_text = ""  

    if request.method == "POST":
        file = request.files["file"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            # **Extract text from different file types**
            if file.filename.endswith((".png", ".jpg", ".jpeg")):
                img = cv2.imread(filepath)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img)
                extracted_text = pytesseract.image_to_string(pil_img)

            elif file.filename.endswith(".docx"):
                doc = Document(filepath)
                extracted_text = "\n".join([para.text for para in doc.paragraphs])

            elif file.filename.endswith(".pdf"):
                with pdfplumber.open(filepath) as pdf:
                    extracted_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

            else:
                return "<h2>Unsupported file type!</h2>"

            # **Summarize the extracted text**
            summarized_text = summarize_text(extracted_text) if len(extracted_text) > 250 else extracted_text

    return render_template("index.html", text=extracted_text, summary=summarized_text)

if __name__ == "__main__":
    app.run(debug=True)
