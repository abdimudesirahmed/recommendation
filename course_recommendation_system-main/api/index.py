from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__, template_folder="../templates")

# Load models
try:
    similarity = pickle.load(open('models/similarity.pkl', 'rb'))
    courses_df = pickle.load(open('models/courses.pkl', 'rb'))
    course_list_dicts = pickle.load(open('models/course_list.pkl', 'rb'))
except Exception as e:
    print(f"Error loading model files: {e}")
    similarity, courses_df, course_list_dicts = None, None, None

if courses_df is not None:
    course_names = courses_df['course_name'].values.tolist()
else:
    course_names = []

def recommend(course_name):
    if courses_df is None or similarity is None:
        return []
    if course_name not in courses_df['course_name'].values:
        return []
    try:
        index = courses_df[courses_df['course_name'] == course_name].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended = []
        for i in distances[1:7]:
            recommended.append({
                "name": courses_df.iloc[i[0]].course_name,
                "url": courses_df.iloc[i[0]].course_url
            })
        return recommended
    except Exception:
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    selected_course = None
    recommendations = []
    if request.method == "POST":
        selected_course = request.form.get("course_name")
        recommendations = recommend(selected_course)
    return render_template("index.html", courses=course_names,
                           recommendations=recommendations,
                           selected_course=selected_course)

# 👉 Key change: expose as `app` for Vercel
# DispatcherMiddleware makes Flask compatible with serverless
app = DispatcherMiddleware(app)
handler = app  # Vercel looks for `handler`
