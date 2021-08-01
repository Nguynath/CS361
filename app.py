from flask import Flask, render_template, url_for
import requests, mysql.connector
app = Flask(__name__)

db = mysql.connector.connect(
    host="us-cdbr-east-04.cleardb.com",
    user="bd62b1c5c8888c",
    password="b8f63b60",
    database="heroku_4cab588d1f5a65c"
)

mycursor = db.cursor()

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return "<h1>About Page</h1>"

if __name__ == '__main__':
    app.run(debug=True)