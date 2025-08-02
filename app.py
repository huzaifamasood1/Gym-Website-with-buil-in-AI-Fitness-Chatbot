
import pandas as pd
import spacy
import re
import random
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Constants
MIN_AGE = 10
MAX_AGE = 80
MIN_HEIGHT_CM = 90
MAX_HEIGHT_CM = 250
MIN_WEIGHT_KG = 30
MAX_WEIGHT_KG = 250

# Load models and app
nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)
state_store = {}

# Load dataset
df = pd.read_csv("dataset/modified_megaGymDataset_v6.csv")
df["Sets/Duration"] = df["Sets/Duration"].astype(str)
df["goal_corpus"] = df["Goal"].fillna('').astype(str)

# Vectorize and cluster goals
vectorizer = TfidfVectorizer(stop_words="english")
X = vectorizer.fit_transform(df["goal_corpus"])
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10).fit(X)
df["GoalCluster"] = kmeans.labels_

# Question variants
question_variants = {
    0: ["Great! First — how old are you?", "Mind telling me your age?", "What's your age, champ?"],
    1: ["And your height?", "How tall are you?", "What’s your height (in cm, m, or feet)?"],
    2: ["How much do you weigh?", "What’s your weight?", "Could you share your weight in kg or lbs?"],
    3: ["Thanks! Let’s calculate your BMI."],
    4: ["What is your fitness goal? (e.g., get lean, bulk up, cut fat)", "What are you aiming to achieve?", "What’s your goal from working out?"],
    5: ["What’s your workout experience?", "Are you a beginner, intermediate, or advanced?", "How experienced are you with workouts?"],
    6: ["Do you prefer gym or home workouts?", "Where do you work out — gym or home?", "Which environment suits you best — gym or home?"],
    7: ["Which area do you want to target? (arms/abs/full body/legs/shoulders/back/core)", "What body area would you like to focus on?", "What muscle group are you working on?"]
}

def extract_number(text):
    try:
        for token in nlp(text):
            if token.like_num:
                return float(token.text)
        match = re.search(r"\d+", text)
        return float(match.group()) if match else None
    except:
        return None

def parse_height(text):
    text = text.lower()
    if "feet" in text or "foot" in text or "'" in text or "ft" in text:
        match = re.match(r"(\d+)[^\d]+(\d+)", text)
        if match:
            ft, inch = int(match.group(1)), int(match.group(2))
            return round(ft * 30.48 + inch * 2.54, 1)
    if "cm" in text or text.strip().isdigit():
        val = extract_number(text)
        return val if val and MIN_HEIGHT_CM <= val <= MAX_HEIGHT_CM else None
    if "m" in text:
        val = extract_number(text)
        return round(val * 100, 1) if val and 0.9 <= val <= 2.5 else None
    return None

def parse_weight(text):
    val = extract_number(text)
    if "lb" in text or "pound" in text:
        return round(val * 0.4536, 1) if val else None
    return val if val and MIN_WEIGHT_KG <= val <= MAX_WEIGHT_KG else None

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        convo = data.get("conversation", [])
        user_id = data.get("user_id", "default")
        user_msgs = [msg["content"].strip() for msg in convo if msg["role"] == "user"]
        user_input = user_msgs[-1].lower() if user_msgs else ""

        if user_id not in state_store:
            state_store[user_id] = {}
        state = state_store[user_id]
        step = len(state)

        if step == 0:
            if user_input in ["yes", "ready", "sure", "let's go"]:
                state["start"] = True
                return jsonify({"reply": random.choice(question_variants[0])})
            else:
                return jsonify({"reply": "Hi! I'm your AI Personal Trainer 🤖💪\nLet's build your perfect workout. Ready?"})

        elif step == 1:
            age = extract_number(user_input)
            if age and MIN_AGE <= age <= MAX_AGE:
                state["age"] = age
                return jsonify({"reply": random.choice(question_variants[1])})
            return jsonify({"reply": "Please enter a valid age between 10–80."})

        elif step == 2:
            height = parse_height(user_input)
            if height:
                state["height"] = height
                return jsonify({"reply": random.choice(question_variants[2])})
            return jsonify({"reply": "Hmm, that height doesn't seem right. Try like '177 cm' or '5 feet 9 inches'."})

        elif step == 3:
            weight = parse_weight(user_input)
            if weight:
                state["weight"] = weight
                if "height" in state:
                    h_m = state["height"] / 100
                    bmi = round(weight / (h_m ** 2), 1)
                    state["bmi"] = bmi
                    label = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
                    return jsonify({"reply": f"📊 Your BMI is {bmi} ({label}).\n{random.choice(question_variants[4])}"})
                return jsonify({"reply": "Thanks! Now tell me your height so I can calculate your BMI."})
            return jsonify({"reply": "Hmm, that weight doesn't seem valid. Try like '70 kg' or '150 lbs'."})

        elif step == 4:
            try:
                vec = vectorizer.transform([user_input])
                state["goal_cluster"] = int(kmeans.predict(vec)[0])
                return jsonify({"reply": random.choice(question_variants[5])})
            except:
                return jsonify({"reply": "I couldn't understand your goal. Try phrases like 'lose weight', 'get lean', or 'build muscle'."})

        elif step == 5:
            state["level"] = user_input
            return jsonify({"reply": random.choice(question_variants[6])})

        elif step == 6:
            state["type"] = user_input
            return jsonify({"reply": random.choice(question_variants[7])})

        elif step == 7:
            state["target"] = user_input
            cluster = state.get("goal_cluster", 0)
            plan_df = df[df["GoalCluster"] == cluster]

            if "target" in state and "Category" in plan_df.columns:
                user_targets = re.split(r"[,\s/&]+", state["target"].lower())
                synonyms = {
                    "core": ["core", "abs", "abdominal"],
                    "legs": ["legs", "lower body", "quads", "hamstrings", "glutes"],
                    "arms": ["arms", "biceps", "triceps"],
                    "back": ["back", "lats", "upper back"],
                    "shoulders": ["shoulders", "delts", "shoulder"],
                    "full body": ["full body", "total", "compound"]
                }
                keywords = set()
                for ut in user_targets:
                    for group in synonyms.values():
                        if any(syn in ut for syn in group):
                            keywords.update(group)
                mask = plan_df["Category"].astype(str).str.lower().apply(lambda cat: any(k in cat for k in keywords))
                plan_df = plan_df[mask]

            if "level" in state and "Level" in plan_df.columns:
                plan_df = plan_df[plan_df["Level"].astype(str).str.lower().str.contains(state["level"])]
            if "type" in state and "Type" in plan_df.columns:
                plan_df = plan_df[plan_df["Type"].astype(str).str.lower().str.contains(state["type"])]

            if plan_df.empty:
                plan_df = df.sample(21)

            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            plan = "📅 Here's your personalized 7-day workout plan:\n\n"
            repeated = plan_df.sample(21, replace=len(plan_df) < 21)
            for i, day in enumerate(days):
                sub = repeated.iloc[i * 3:i * 3 + 3]
                plan += f"{day}:\n"
                for ex, sets, reps in sub[["Exercise", "Sets/Duration", "Reps"]].values:
                    plan += f"  - {ex} | {sets} | {reps}\n"
                plan += "\n"

            plan += "Would you like a tailored diet plan too?"
            return jsonify({"reply": plan})

        elif step == 8:
            affirmatives = ["yes", "sure", "of course", "yeah", "please", "yep", "absolutely", "definitely"]
            if any(word in user_input for word in affirmatives):
                return jsonify({"reply": "🥗 Here's your tailored diet plan:\nBreakfast: Oats & eggs\nLunch: Grilled chicken + salad\nDinner: Steamed fish & rice\nSnacks: Almonds & Greek yogurt"})
            else:
                return jsonify({"reply": "Alright! You can ask for it anytime 💡"})

    except Exception as e:
        return jsonify({"reply": f"An error occurred: {str(e)}"})

    return jsonify({"reply": random.choice(question_variants.get(len(state), ["Let’s continue!"]))})

if __name__ == "__main__":
    app.run(debug=True)
