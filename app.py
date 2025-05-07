from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient
import google.generativeai as genai
import base64
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


# Roboflow
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="X3PiayjEhkfMyE96iL1w"
)

# Gemini setup
genai.configure(api_key="AIzaSyD5EVduUfkCnbj_fWs2-Lci18Eq7necSYs")
model = genai.GenerativeModel("gemini-1.5-flash")

def get_grocery_info(grocery_name):
    prompt = f"""
Provide detailed information about the grocery product '{grocery_name}'.
Include:
1.which age people need to eat
2.what are the chemical substances added in this product
3. side effects (downsides) in 5 words
4. vitamins and minerals in 5 words
5. A 2-3 line summary at the end in 10 words
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route("/infer", methods=["POST"])
def infer():
    data = request.json
    img_data = data["image"]
    img_bytes = base64.b64decode(img_data.split(",")[1])
    
    # Save temp frame
    with open("temp.jpg", "wb") as f:
        f.write(img_bytes)

    try:
        result = CLIENT.infer("temp.jpg", model_id="grocery-dataset-q9fj2/5")
        if result and 'predictions' in result and result['predictions']:
            pred = max(result['predictions'], key=lambda x: x['confidence'])
            class_name = pred['class']
            grocery_info = get_grocery_info(class_name)
            return jsonify({
                "item": class_name,
                "info": grocery_info
            })
        else:
            return jsonify({"error": "No predictions found"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
