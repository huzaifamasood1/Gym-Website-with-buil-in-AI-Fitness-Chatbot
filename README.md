# AI Fitness Chatbot

This is a web-based AI-powered fitness chatbot that provides personalized workout and diet plans based on user input such as age, height, weight, and fitness goals.

## 📁 Project Structure

```
project/
│
├── app.py                 # Flask backend for chatbot
├── chatbot.py             # NLP + KMeans logic
├── chat.html              # Frontend chatbot interface
├── BMI.php                # BMI calculator (PHP)
├── appointment.php        # Appointment booking (PHP)
├── login.php              # Login handler (PHP)
├── about.html             # Static About Us page
├── services.html          # Static Services page
├── team.html              # Static Team page
└── static/                # JS, CSS, images
```

---

## 🧠 Core Technologies

- **Python Flask** (backend for chatbot)
- **spaCy** (for NLP entity extraction)
- **KMeans** (for goal clustering)
- **PHP** (BMI, appointments, login)
- **HTML/CSS/JS + Bootstrap** (frontend)
- **XAMPP** (for running PHP files)

---

## 🚀 How to Run the Project

### 1. Clone or Download
Unzip the project folder and open it in your code editor (e.g., VS Code).

### 2. Backend Setup (Python + Flask)

#### a. Create and activate virtual environment (Windows)
```bash
python -m venv venv
venv\Scripts\activate
```

#### b. Install dependencies
```bash
pip install flask scikit-learn spacy
python -m spacy download en_core_web_sm
```

#### c. Run Flask app
```bash
python app.py
```

The backend will run on `http://127.0.0.1:5000`

---

### 3. PHP Setup (BMI & Appointment)

#### a. Install XAMPP

Download from: https://www.apachefriends.org/index.html

#### b. Copy Project Folder to XAMPP
Move your project folder to `C:/xampp/htdocs/`

#### c. Start Apache Server
Open XAMPP Control Panel and start Apache

#### d. Open in Browser
Access via: `http://localhost/project_folder_name/home.html`

---

## ✅ Features

- Chatbot with BMI and fitness goal classification
- Dynamic 6-day workout + diet plan generation
- BMI calculator (height/weight logic)
- Appointment booking form
- User login and plan selection
- Static pages: About Us, Services, Team

---

## 🔍 Notes

- Make sure Flask is running before using the chatbot
- Use XAMPP only for PHP pages (BMI, appointments)
- All form submissions and results are processed locally

---

## 👨‍💻 Developers

- Muhammad Anas -089
- Chaudhary Ammaz Hussain -037