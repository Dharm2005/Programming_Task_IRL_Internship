from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    name = request.args.get("name")

    if name:
        name = name.upper()
    else:
        name = "NO NAME PROVIDED"

    return render_template("index.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)
