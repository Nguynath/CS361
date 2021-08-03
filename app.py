import mysql.connector, requests, urllib.request
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

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

    url_dict = {}

    # Title Text Search
    if 'form_titleSearch' in request.args:
        text_q = request.args.get('form_titleSearch')
        if text_q == '':
            query = "SELECT * FROM title_info"
        else:
            if and_count == 0:
                and_count += 1
                url_dict['titleSearch'] = text_q
                query += ' WHERE (`Title` LIKE ' + "'%" + str(text_q) + "%')"

    # Media Filter
    if 'form_media' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (`Title Type` = "
        else:
            query += " AND (`Title Type` = "

        media_q = request.args.get('form_media')
        if media_q == 'all':
            query = "SELECT * FROM title_info"
            and_count = 0
        elif media_q == 'movies':
            query += "'movie')"
        elif media_q == 'tvMovies':
            query += "'tvMovie')"
        elif media_q == 'tvShows':
            query += "'tvSeries')"
        elif media_q == 'tvMiniSeries':
            query += "'tvMiniSeries')"
        elif media_q == 'tvSpecials':
            query += "'tvSpecial')"
        url_dict['mediaSearch'] = str(media_q)

    # Genre Filter
    if 'form_genre' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (FIND_IN_SET('"
        else:
            query += " AND (FIND_IN_SET('"
        genre_q = request.args.get('form_genre')
        query += str(genre_q)
        query += "',Genres))"
        url_dict['genreSearch'] = str(genre_q)

    # Rating Filter
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
        url_dict['ratingSearch'] = str(rating_q)

    # Runtime Filter
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
        url_dict['runtimeSearch'] = str(length_q)

    # Release Year Filter
    if 'form_releaseYear' in request.args:
        if and_count == 0:
            and_count += 1
            query += " WHERE (YEAR(`Release Date`) = "
        else:
            query += " AND (YEAR(`Release Date`) = "
        releaseYear_q = int(request.args.get('form_releaseYear'))
        query += str(releaseYear_q) + ")"
        url_dict['releaseYearSearch'] = str(releaseYear_q)

    # Pagination
    perpage = 100
    startat = page * perpage
    args = (startat, perpage)

    # Sort Buttons/Query Completion
    if 'sort_media_a' in request.args:
        query += " ORDER BY `Title Type` ASC LIMIT %s, %s;"
    elif 'sort_media_d' in request.args:
        query += " ORDER BY `Title Type` DESC LIMIT %s, %s;"
    elif 'sort_genres_a' in request.args:
        query += " ORDER BY `Genres` ASC LIMIT %s, %s;"
    elif 'sort_genres_d' in request.args:
        query += " ORDER BY `Genres` DESC LIMIT %s, %s;"
    elif 'sort_ratings_a' in request.args:
        query += " ORDER BY `IMDB Rating` ASC LIMIT %s, %s;"
    elif 'sort_ratings_d' in request.args:
        query += " ORDER BY `IMDB Rating` DESC LIMIT %s, %s;"
    elif 'sort_runtimes_a' in request.args:
        query += " ORDER BY `Runtime` ASC LIMIT %s, %s;"
    elif 'sort_runtimes_d' in request.args:
        query += " ORDER BY `Runtime` DESC LIMIT %s, %s;"
    elif 'sort_releaseYear_a' in request.args:
        query += " ORDER BY `Release Date` ASC LIMIT %s, %s;"
    elif 'sort_releaseYear_d' in request.args:
        query += " ORDER BY `Release Date` DESC LIMIT %s, %s;"
    else:
        query += " ORDER BY `IMDB Rating` DESC LIMIT %s, %s;"
    print("Query:", query)

    # Database Connect/Execute/Close
    db = mysql_connect()
    mycursor = db.cursor()
    mycursor.execute(query, args)
    titleDetails = mycursor.fetchall()
    db.commit()
    mycursor.close()
    db.close()

    return render_template("home.html", titleDetails=titleDetails, url_dict=url_dict)


# ----------------------------------------------------------------------------------------------------------------------
# FLXR Title Detail Page
@app.route("/about/<string:id>", methods=["GET", "POST"])
def about(id):

    # MySQL Query
    query = "SELECT URL FROM title_info WHERE `Position` = " + str(id)

    # Database Connect/Execute/Close
    db = mysql_connect()
    mycursor = db.cursor()
    mycursor.execute(query)
    titleDetails = mycursor.fetchall()
    db.commit()
    mycursor.close()
    db.close()

    # Call Text Scraper/Add to dictionary of data
    about_dict = {}
    about_dict['Title'], about_dict['imageURL'] = scrape_data(titleDetails[0][0])


    return render_template("about.html", about_dict=about_dict)


# ----------------------------------------------------------------------------------------------------------------------

def scrape_data(url_page):

    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(url_page, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Movie/Show Titles
    title = soup.find("h1").get_text()

    # Image
    image = str(soup.find("img", class_="ipc-image")['src'])

    return title, image


# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
