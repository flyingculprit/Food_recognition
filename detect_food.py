from tensorflow.keras.models import load_model
import numpy as np
import cv2
import google.generativeai as genai

# -------- CONFIG --------
EFFNET_MODEL_PATH = "EfficientNetB1.hdf5"  # EfficientNetB1 model path
GEMINI_API_KEY = "surya"  # Replace with your actual Gemini key
IMAGE_PATH = "egg.jpg"  # Replace with your food image

# -------- 1. Load EfficientNetB1 Model --------
model = load_model(EFFNET_MODEL_PATH)  # Load EfficientNetB1

# -------- 2. Preprocess Image --------
image = cv2.imread(IMAGE_PATH)
image = cv2.resize(image, (224, 224))  # Resize to match the input size of EfficientNetB1 (224x224)
image = np.expand_dims(image, axis=0)  # Add batch dimension
image = image / 255.0  # Normalize the image to [0, 1]

# -------- 3. Make Prediction --------
predictions = model.predict(image)

# Get the class with the highest probability
predicted_class = np.argmax(predictions, axis=1)
predicted_class_name = str(predicted_class[0])  # Assuming your classes are indexed 0, 1, 2, ...

# Map to class name (you need to define this mapping based on your model's classes)
class_names = {0: 'Apple', 1: 'Chapathi', 2: 'Chicken Gravy', 3: 'Fries', 4: 'Idli', 5: 'Pizza', 6: 'Rice', 7: 'Soda', 8: 'Tomato', 9: 'Vada', 10: 'banana', 11: 'burger'}

detected_food = class_names.get(predicted_class_name, "Unknown Food")
print(f"\n🔍 Detected Food: {detected_food}")

# -------- 4. Ask Gemini about the food --------
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel(model_name="models/gemini-pro")  # ✅ Correct model path

prompt = f"""
Give a detailed analysis of the food item '{detected_food}'.
1. What age group is it suitable for?
2. What are the general ingredients?
3. What are the health benefits?
4. What are the potential health risks?
Keep it short, informative, and easy to understand.
"""

response = gemini.generate_content(prompt)
print("\n💡 Food Information from Gemini:")
print(response.text)
