from flask import Flask, jsonify
import random
import time

app = Flask(__name__)


@app.route("/weather")
def weather():

    time.sleep(random.uniform(0, 1.5))

    if random.random() < 0.2:
        return {"error": "temporary failure"}, 500

    return jsonify(
        {
            "temp": random.randint(-10, 35),
            "wind": random.randint(0, 50),
            "rain": random.choice([0, 0, 1, 5]),
        }
    )


app.run(host="0.0.0.0", port=5000)
