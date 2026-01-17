from flask import Flask, request, render_template
from logic import check_string

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def home():
  user_data = {}
  
  if request.method == "POST":
    user_data['text'] = request.form.get("text")
    user_data['regex'] = request.form.get("regex")
    
    output = check_string(user_data['text'], user_data['regex'])
    
  return render_template("index.html", data=output)

if __name__ == "__main__":
    app.run(debug=True)