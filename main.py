from flask import Flask, request, jsonify

app = Flask(__name__)

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9
}

PROTEIN_MULTIPLIERS = {
    "maintain": 1.5,
    "lose": 2.0,
    "bulk": 1.5
}

def calculate_bmr(age, sex, weight_kg, height_cm):
    sex = sex.lower()
    if sex in ("male", "m"):
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

@app.route("/", methods=["GET"])
def protein_calculator():
    try:
        age = int(request.args.get("age", 0))
    except ValueError:
        age = 0

    try:
        weight = float(request.args.get("weight", 0))
    except ValueError:
        weight = 0

    try:
        height = float(request.args.get("height", 0))
    except ValueError:
        height = 0

    sex = request.args.get("sex", "male").lower()
    activity = request.args.get("activity_level", "sedentary").lower()
    goal = request.args.get("goal", "maintain").lower()

    if age <= 0 or weight <= 0 or height <= 0:
        return jsonify({
            "success": False,
            "message": "Please provide valid age, weight and height. Example: ?age=19&weight=80&height=175"
        })

    if age < 13:
        return jsonify({
            "success": False,
            "age": age,
            "message": "This calculation is not recommended for minors (under 13)."
        })

    if activity not in ACTIVITY_MULTIPLIERS:
        return jsonify({
            "success": False,
            "message": f"activity_level must be one of {list(ACTIVITY_MULTIPLIERS.keys())}"
        })

    if goal not in ("maintain", "lose", "bulk"):
        return jsonify({
            "success": False,
            "message": "goal must be 'maintain', 'lose', or 'bulk'"
        })

    bmr = calculate_bmr(age, sex, weight, height)
    tdee = bmr * ACTIVITY_MULTIPLIERS[activity]

    if goal == "lose":
        calories = max(0, tdee - 500)
    elif goal == "bulk":
        calories = tdee + 500
    else:
        calories = tdee

    protein = round(weight * PROTEIN_MULTIPLIERS[goal], 2)

    return jsonify({
        "success": True,
        "age": age,
        "weight_kg": weight,
        "height_cm": height,
        "sex": sex,
        "activity_level": activity,
        "goal": goal,
        "results": {
            "bmr": round(bmr, 1),
            "tdee_maintenance": round(tdee, 1),
            "recommended_calories_for_goal": round(calories, 1),
            "protein_grams_per_day": f"{protein}g"
        },
        "note": "Protein is based on goal and weight. Calories are adjusted per goal: ~500 kcal deficit for lose, +500 kcal surplus for bulk.",
        "message": "Protein is only one part of balanced nutrition. Whether your goal is weight loss or gain, maintaining calories with quality protein, carbs, and fats is essential."
    })


# 📄 HTML Documentation Page
@app.route("/docs")
def docs():
    return """
    <html>
    <head>
        <title>Calorie & Protein Calculator API Docs</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
            h1 { color: #2c3e50; }
            code { background: #eee; padding: 2px 6px; border-radius: 4px; }
            .example { background: #fff; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; }
        </style>
    </head>
    <body>
        <h1>🍎 Calorie & Protein Calculator API</h1>
        <p>Use this API to calculate <b>BMR, TDEE, Calories & Protein</b> for different goals (maintain, lose, bulk).</p>
        
        <h2>📌 Endpoint</h2>
        <p><code>GET /</code></p>

        <h2>🔹 Query Parameters</h2>
        <ul>
            <li><b>age</b> (int, required) – Age in years</li>
            <li><b>weight</b> (float, required) – Weight in kg</li>
            <li><b>height</b> (float, required) – Height in cm</li>
            <li><b>sex</b> (string, optional) – male / female (default: male)</li>
            <li><b>activity_level</b> (string, optional) – sedentary / light / moderate / active / very_active</li>
            <li><b>goal</b> (string, optional) – maintain / lose / bulk (default: maintain)</li>
        </ul>

        <h2>🔹 Example Requests</h2>
        <div class="example"><code>/?age=25&weight=70&height=175&sex=male&activity_level=moderate&goal=maintain</code></div>
        <div class="example"><code>/?age=25&weight=70&height=175&sex=male&activity_level=moderate&goal=lose</code></div>
        <div class="example"><code>/?age=25&weight=70&height=175&sex=male&activity_level=moderate&goal=bulk</code></div>

        <h2>🔹 Example Response</h2>
        <pre>{
  "success": true,
  "age": 25,
  "weight_kg": 70.0,
  "height_cm": 175.0,
  "sex": "male",
  "activity_level": "moderate",
  "goal": "maintain",
  "results": {
    "bmr": 1673.8,
    "tdee_maintenance": 2594.4,
    "recommended_calories_for_goal": 2594.4,
    "protein_grams_per_day": "105.0g"
  }
}</pre>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)