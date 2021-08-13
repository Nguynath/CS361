import mysql.connector, requests, math
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# ----------------------------------------------------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------------------------------------------------
# Function to submit a query to MySQL
def mysql_getData(query):

    db = mysql_connect()
    mycursor = db.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()
    db.commit()
    mycursor.close()
    db.close()

    return data


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# FLXR Homepage
@app.route("/", defaults={'page': 1}, methods=["GET", "POST"])
@app.route('/page<int:page>')
def load_home(page):

    query_request = request.url

    # Remove https
    if len(query_request) >= 23:
        for element in query_request:
            if element != '?':
                query_request = query_request.replace(str(element), '', 1)
            else:
                break
    else:
        query_request = ''

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
            query += "'Movie' OR 'TV-Movie' OR 'TV-Show' OR 'TV-MiniSeries' OR 'TV-Special' OR 'Short')"
        elif media_q == 'movies':
            query += "'Movie')"
        elif media_q == 'tvMovies':
            query += "'TV-Movie')"
        elif media_q == 'tvShows':
            query += "'TV-Show')"
        elif media_q == 'tvMiniSeries':
            query += "'TV-MiniSeries')"
        elif media_q == 'tvSpecials':
            query += "'TV-Special')"
        elif media_q == 'shorts':
            query += "'Short')"
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
            query += " WHERE (YEAR(`Year`) = "
        else:
            query += " AND (YEAR(`Year`) = "
        releaseYear_q = int(request.args.get('form_releaseYear'))
        query += str(releaseYear_q) + ")"
        url_dict['releaseYearSearch'] = str(releaseYear_q)

    # Sort Buttons/Query Completion
    if 'sort_title_a' in request.args:
        query += " ORDER BY `Title` ASC LIMIT %s, %s;"
    elif 'sort_title_d' in request.args:
        query += " ORDER BY `Title` DESC LIMIT %s, %s;"
    elif 'sort_media_a' in request.args:
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
        query += " ORDER BY `Year` ASC LIMIT %s, %s;"
    elif 'sort_releaseYear_d' in request.args:
        query += " ORDER BY `Year` DESC LIMIT %s, %s;"
    else:
        query += " ORDER BY `IMDB Rating` DESC LIMIT %s, %s;"

    # Pagination
    perpage = 50
    startat = (page - 1) * perpage
    args = (startat, perpage)
    query_size = len(query)
    query_count = query[:query_size - 13]

    # Database Connect/Execute/Close
    db = mysql_connect()

    mycursor = db.cursor(buffered=True)
    mycursor.execute(query, args)
    titleDetails = mycursor.fetchall()

    mycursor.execute(query_count)
    total_row = mycursor.rowcount
    total_page = math.floor(total_row / perpage) + 1
    next_page = page + 1
    prev_page = page - 1

    db.commit()
    mycursor.close()
    db.close()

    return render_template(
        "home.html",
        titleDetails=titleDetails,
        url_dict=url_dict,
        page=page,
        total_page=total_page,
        total_row=total_row,
        next_page=next_page,
        prev_page=prev_page,
        query_request=query_request
    )


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# FLXR Title Detail Page
@app.route("/descriptions", methods=["GET", "POST"])
def description():

    return render_template("descriptions.html")


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# FLXR Title Detail Page
@app.route("/about/<string:id>", methods=["GET", "POST"])
def about(id):

    # MySQL Query
    query = "SELECT * FROM title_info WHERE `Position` = " + str(id)

    # Database Connect/Execute/Close
    titleDetails = mysql_getData(query)

    # Create dictionary of Title Information
    about_dict = {}
    keys = ['title', 'url', 'titleType', 'rating', 'length', 'releaseYear', 'genre', 'releaseDate', 'director']

    for value in range(0, 9):
        about_dict[keys[value]] = titleDetails[0][value + 1]

    # Call Text and Image Scraper Functions
    about_dict['imageURL'] = scrape_image(titleDetails[0][2])
    about_dict['summary'] = get_summary(titleDetails[0][1])

    return render_template("about.html", about_dict=about_dict)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Image Scraper (Self)
def scrape_image(url_page):

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(url_page, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Image
    image = str(soup.find("img", class_="ipc-image")['src'])

    return image


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Image Scraper Microservice Response
@app.route("/scrape/<string:processor>", methods=["GET", "POST"])
def imageScrape(processor):

    # MySQL Query
    query = "SELECT processorURL FROM processor_info WHERE `processorModel` = " + "'" + str(processor) + "'"

    # Database Connect/Execute/Close
    db = mysql_connect()
    mycursor = db.cursor()
    mycursor.execute(query)
    URL = mycursor.fetchall()
    db.commit()
    mycursor.close()
    db.close()

    image_URL = microservice_scrape_image(URL[0][0])

    return jsonify(image_URL)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Provide Image Scraper Microservice
def microservice_scrape_image(url_page):

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    page = requests.get(url_page, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Image
    image = str(soup.find("img", class_="product-view-img-original")['src'])

    return image


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Request Text Scraper Microservice
def get_summary(title):

    title_fixed = title.replace(" ", "_")

    summary = requests.get("https://burnbroo-api.herokuapp.com/summaries/" + title_fixed)

    return summary.json()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)