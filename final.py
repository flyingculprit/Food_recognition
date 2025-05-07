import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient
from tkinter import Tk, Label, Button, StringVar, Frame, LEFT, RIGHT, TOP, BOTTOM
from PIL import Image, ImageTk
import google.generativeai as genai

# Initialize Roboflow Inference client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="X3PiayjEhkfMyE96iL1w"
)

# Set up Gemini API key
genai.configure(api_key="AIzaSyD5EVduUfkCnbj_fWs2-Lci18Eq7necSYs")
model = genai.GenerativeModel("gemini-1.5-flash")  # ✅ Confirmed working model

# Use the correct available model
def get_grocery_info(grocery_name):
    prompt = f"""
Provide detailed information about the grocery product '{grocery_name}'.
Include:
1.which age people need to eat
2.what are the chemical substances added in this product
3.side effects (downsides) in 5 words
4. vitamins and minerals in 5 words
5. A 2-3 line summary at the end in 10 words
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Initialize GUI
root = Tk()
root.title("Live Grocery Recognition")
root.geometry("900x600")

top_frame = Frame(root)
top_frame.pack(side=TOP)

left_frame = Frame(root)
left_frame.pack(side=LEFT, fill="both", expand=True)

right_frame = Frame(root)
right_frame.pack(side=RIGHT, fill="both", expand=True)

# GUI Variables
prediction_text = StringVar()
class_name_var = StringVar()
grocery_info_var = StringVar()

image_label = Label(left_frame)
image_label.pack(pady=10)

prediction_label = Label(right_frame, textvariable=prediction_text, font=("Arial", 12), wraplength=250)
prediction_label.pack(pady=5)

class_name_label = Label(right_frame, textvariable=class_name_var, font=("Arial", 12), wraplength=250)
class_name_label.pack(pady=5)

grocery_info_label = Label(right_frame, textvariable=grocery_info_var, font=("Arial", 10), wraplength=250)
grocery_info_label.pack(pady=5)

# Recognition tracking
recognized_items = set()
current_item = ""

def process_frame():
    global current_item

    ret, frame = cap.read()
    if not ret:
        root.after(3000, process_frame)
        return

    # Show frame in GUI
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((300, 300))
    imgtk = ImageTk.PhotoImage(image=img)
    image_label.imgtk = imgtk
    image_label.configure(image=imgtk)

    # Save and send frame to Roboflow
    cv2.imwrite("temp_frame.jpg", frame)

    try:
        result = CLIENT.infer("temp_frame.jpg", model_id="grocery-dataset-q9fj2/5")

        if result and 'predictions' in result and result['predictions']:
            pred = max(result['predictions'], key=lambda x: x['confidence'])
            class_name = pred['class']

            # Only process if it's a new item
            if class_name != current_item and class_name not in recognized_items:
                current_item = class_name
                recognized_items.add(class_name)

                confidence = pred['confidence']
                # prediction_text.set(f"Prediction: {class_name} ({confidence:.2f})")
                class_name_var.set(f"Item Name: {class_name}")

                print(f"Recognized: {class_name}")

                # Fetch grocery info using Gemini API
                grocery_info = get_grocery_info(class_name)
                grocery_info_var.set(grocery_info)

    except Exception as e:
        print(f"Inference error: {e}")

    # Schedule next frame check
    root.after(3000, process_frame)

# Reset button to allow new scanning session
def reset_recognition():
    global recognized_items, current_item
    recognized_items.clear()
    current_item = ""
    prediction_text.set("")
    class_name_var.set("")
    grocery_info_var.set("")

reset_button = Button(top_frame, text="Reset Recognition", command=reset_recognition)
reset_button.pack(side=TOP, pady=5)

# Start webcam
cap = cv2.VideoCapture(0)

# Start recognition loop
process_frame()

# Run app
root.mainloop()

# Release webcam on close
cap.release()
