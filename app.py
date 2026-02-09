from flask import Flask, render_template, request
from scanner import scan_market

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    relaxed = False
    market = "US"  # default

    if request.method == "POST":
        # Get market from form
        market = request.form.get("market", "US")
        # Check relaxed mode
        relaxed = request.form.get("relaxed") == "on"
        # Run scan
        results = scan_market(market, relaxed=relaxed)

    # Pass variables to template so dropdown & checkbox persist
    return render_template("index.html", results=results, relaxed=relaxed, market=market)

if __name__ == "__main__":
    app.run(debug=True)
