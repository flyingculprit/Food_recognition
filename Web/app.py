from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
import random
import smtplib
import ssl
import google.generativeai as genai
from PIL import Image
import base64
import io

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this!

# Configure Gemini API
genai.configure(api_key="AIzaSyBkQSeElRxt2jD98uc21JAxlKkiQkUNcOc")  # Replace with your key
model = genai.GenerativeModel('models/gemini-1.5-flash')

# MongoDB setup
client = MongoClient("mongodb+srv://commander:LwC72c5UL8xsF5ug@cluster0.bbqab.mongodb.net/")
db = client["user_database"]
users_col = db["user"]

# SMTP config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_ADDRESS = "cyrusbyte.in@gmail.com"
EMAIL_PASSWORD = "mysbesxffdzworkx"

def send_otp_email(to_email, otp):
    message = f"""\
Subject: Your OTP Verification Code

Your OTP code is: {otp}
"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, message)

@app.route("/")
def home():
    return redirect(url_for("signup"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        # Check if user exists
        if users_col.find_one({"email": email}):
            flash("Email already registered, please login.")
            return redirect(url_for("login"))

        # Generate OTP and save user with otp and not verified yet
        otp = str(random.randint(100000, 999999))
        user_data = {
            "email": email,
            "password": password,  # IMPORTANT: Store hashed passwords in production!
            "otp": otp,
            "verified": False
        }
        users_col.insert_one(user_data)

        # Send OTP email
        send_otp_email(email, otp)
        session["email"] = email
        flash("OTP sent to your email.")
        return redirect(url_for("otp"))

    return render_template("signup.html")

@app.route("/otp", methods=["GET", "POST"])
def otp():
    email = session.get("email")
    if not email:
        flash("Please sign up first.")
        return redirect(url_for("signup"))

    if request.method == "POST":
        entered_otp = request.form["otp"]
        user = users_col.find_one({"email": email})

        if user and user["otp"] == entered_otp:
            users_col.update_one({"email": email}, {"$set": {"verified": True}, "$unset": {"otp": ""}})
            flash("OTP verified successfully! Please login.")
            return redirect(url_for("login"))
        else:
            flash("Invalid OTP. Please try again.")

    return render_template("otp.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]
        user = users_col.find_one({"email": email})

        if user:
            if not user.get("verified", False):
                flash("Please verify your email with OTP first.")
                session["email"] = email
                return redirect(url_for("otp"))
            if user["password"] == password:
                session["user"] = email
                flash(f"Welcome, {email}!")
                # Redirect to indexx.html after login instead of dashboard
                return redirect(url_for("index"))
            else:
                flash("Wrong password.")
        else:
            flash("User not found. Please signup.")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    return f"Hello {session['user']}! You are logged in."

@app.route("/index")
def index():
    if "user" not in session:
        flash("Please login first.")
        return redirect(url_for("login"))
    return render_template('indexx.html')

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
