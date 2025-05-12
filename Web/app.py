from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import base64
import io

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key="AIzaSyBkQSeElRxt2jD98uc21JAxlKkiQkUNcOc")  # Replace with your key
model = genai.GenerativeModel('models/gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize')
def recognize():
    return render_template('recognize.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data_url = request.json.get('image')

    # Convert base64 to image
    header, encoded = data_url.split(",", 1)
    image_data = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(image_data))

    prompt = """
Provide detailed information about the grocery product.
Include:
1. Which age people Can eat:
2. Approximate list of chemical additives or preservatives usually found in similar products:
3. Side effects (downsides) in 10 words:
4. Vitamins and minerals in 5 words:
5. A 2-3 line summary at the end:
State clearly this is a general approximation based on the image.
"""

    response = model.generate_content([image, prompt])
    return jsonify({'result': response.text})

if __name__ == "__main__":
    app.run(debug=True)