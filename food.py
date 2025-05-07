import torch
import cv2
import google.generativeai as genai

# -------- CONFIG --------
YOLO_MODEL_PATH = "E:/Git/food_detection/best.pt"  # Downloaded model
GEMINI_API_KEY = "AIzaSyABi2JxvIjYdkiS0es6Uu_jBT_H1mRAB5Q"  # Replace with your actual Gemini key
IMAGE_PATH = "E:/Git/food_detection/egg.jpg"  # Replace with your food image

# -------- 1. Load YOLOv5 Model --------
model = torch.hub.load('ultralytics/yolov5', 'custom', path=YOLO_MODEL_PATH, force_reload=True)

# -------- 2. Detect Food in Image --------
results = model(IMAGE_PATH)
results.print()  # Print YOLOv5 result summary

# Parse the first detected label
detected_items = results.pandas().xyxy[0]['name'].tolist()
if not detected_items:
    print("No food item detected.")
    exit()

detected_food = detected_items[0]
print(f"\n🔍 Detected Food: {detected_food}")

# -------- 3. Ask Gemini about the food --------
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-pro")

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
