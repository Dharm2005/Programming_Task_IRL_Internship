from flask import Flask, render_template, request, redirect, abort
from models import db, URL
from urllib.parse import urlparse
import random
import string

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# Functions
def generate_short_code():
  characters = string.ascii_letters + string.digits
  return ''.join(random.choices(characters, k=6))

def is_valid_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme in ("http", "https"), result.netloc])
  except:
    return False

# Routers
@app.route("/", methods = ['GET', 'POST'])
def index():
  short_url = None

  if request.method == "POST":
    long_url = request.form.get("url")

    # Validate URL
    if not is_valid_url(long_url):
      return render_template(
        "home.html",
        data=None,
        error="Please enter a valid URL (must start with http:// or https://)"
      )

    # Check if URL already exists
    existing = URL.query.filter_by(long_url=long_url).first()
    if existing:
        short_url = existing.short_code
    else:
        # Generate unique short code
        while True:
          short_code = generate_short_code()
          if not URL.query.filter_by(short_code=short_code).first():
            break

        new_url = URL(
          long_url=long_url,
          short_code=short_code
        )
        db.session.add(new_url)
        db.session.commit()
        short_url = short_code

  return render_template("home.html", data=short_url)
  
@app.route("/history")
def history():
  urls = URL.query.all()
  return render_template("history.html", urls=urls)


@app.route("/<short_code>")
def redirect_to_original(short_code):
  url = URL.query.filter_by(short_code=short_code).first()
  
  if url:
    url.clicks += 1
    db.session.commit()
    return redirect(url.long_url)
  else:
    return abort(404)


if __name__ == '__main__':
  app.run(debug = True)