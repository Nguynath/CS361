import mysql.connector
from flask import Flask, render_template, url_for, request

app = Flask(__name__)


# ----------------------------------------------------------------------------------------------------------------------
# MySQL Database Connection
def mysql_connect():
    try:
        db = mysql.connector.connect(
            host="us-cdbr-east-04.cleardb.com",
            user="bd62b1c5c8888c",
            password="b8f63b60",
            database="heroku_4cab588d1f5a65c"
        )
    except mysql.connector.error as err:
        print("Something went wrong: {}".format(err))

    return db


# ----------------------------------------------------------------------------------------------------------------------
# FLXR Homepage
@app.route("/", defaults={'page': 0}, methods=["GET", "POST"])
@app.route('/page<int:page>')
def load_home(page):
    query = "SELECT * FROM title_info"
    and_count = 0

    # if 'form_titleSearch' in request.args:
    #     if and_count == 0:
    #         and_count += 1
    #         query += ' WHERE (`Title` like '

    if 'form_media' in request.args:
        if and_count == 0:
            and_count += 1
            query += ' WHERE (`Title Type` = '
        media_q = request.args.get('form_media')
        if media_q == 'both':
            and_count = 0
            query = "SELECT * FROM title_info"
        elif media_q == 'show':
            query += "'tvSeries' OR `Title Type` = 'tvMiniSeries' OR `Title Type` = 'tvSpecial' OR `Title Type` = 'tvMovie')"
        elif media_q == 'movie':
            query += "'movie')"

    if 'form_genre' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (FIND_IN_SET('"
        else:
            query += " AND (FIND_IN_SET('"
        genre_q = request.args.get('form_genre')
        query += str(genre_q)
        query += "',Genres))"

    if 'form_rating' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (`IMDB Rating` BETWEEN "
        else:
            query += " AND (`IMDB Rating` BETWEEN "
        rating_q = int(request.args.get('form_rating'))
        query += str(rating_q)
        query += ' AND '
        query += str(rating_q + 0.9) + ")"

    if 'form_length' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (`Runtime`"
        else:
            query += " AND (`Runtime`"
        length_q = request.args.get('form_length')
        if length_q == '3plus':
            query += ' >= 180)'
        elif length_q == '2to3':
            query += ' BETWEEN 120 AND 180)'
        elif length_q == '1to2':
            query += ' BETWEEN 60 AND 120)'
        elif length_q == 'less1':
            query += ' <= 60)'

    if 'form_releaseYear' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (YEAR(`Release Date`) = "
        else:
            query += " AND (YEAR(`Release Date`) = "
        releaseYear_q = int(request.args.get('form_releaseYear'))
        query += str(releaseYear_q) + ")"

    perpage = 100
    startat = page * perpage
    query += " ORDER BY `IMDB Rating` DESC LIMIT %s, %s;"

    print(query)

    args = (startat, perpage)

    db = mysql_connect()
    mycursor = db.cursor()
    mycursor.execute(query, args)
    titleDetails = mycursor.fetchall()
    db.commit()
    mycursor.close()
    db.close()

    and_count = 0

    return render_template("home.html", titleDetails=titleDetails)


# ----------------------------------------------------------------------------------------------------------------------
# FLXR Title Detail Page
@app.route("/about/<string:id>", methods=["GET", "POST"])
def about(id):
    print(id)
    if request.method == "POST":
        userDetails = request.form
        name = userDetails["name"]
        email = userDetails["email"]

        mycursor = db.cursor()
        mycursor.execute("INSERT INTO users(name, email) VALUES (%s, %s)", (name, email))
        db.commit()
        mycursor.close()
    return render_template("about.html")


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
