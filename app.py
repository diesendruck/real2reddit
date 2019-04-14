from jolene0 import run_jolene
from flask import Flask, request, render_template
app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/submit", methods=['POST'])
def submit():
    _url = request.form['inputUrl']
    reddit_url = run_jolene(_url)

    return render_template('index.html', redditUrl=reddit_url)


if __name__ == "__main__":
    app.run(debug=True)
