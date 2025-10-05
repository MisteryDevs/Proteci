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
    # Get parameters
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

    # Validate input
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

    # BMR & TDEE
    bmr = calculate_bmr(age, sex, weight, height)
    tdee = bmr * ACTIVITY_MULTIPLIERS[activity]

    if goal == "lose":
        calories = max(0, tdee - 500)
    elif goal == "bulk":
        calories = tdee + 500
    else:
        calories = tdee

    # Protein intake
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

if __name__ == "__main__":
    app.run(debug=True)
