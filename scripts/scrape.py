import requests, mysql.connector
from bs4 import BeautifulSoup

db = mysql.connector.connect(
    host="us-cdbr-east-04.cleardb.com",
    user="bd62b1c5c8888c",
    password="b8f63b60",
    database="heroku_4cab588d1f5a65c"
)

mycursor = db.cursor()

mycursor.execute("CREATE TABLE IF NOT EXISTS Information (titleID int PRIMARY KEY AUTO_INCREMENT, media VARCHAR(50), title VARCHAR(50), genre VARCHAR(50), rating VARCHAR(50), length VARCHAR(50), releaseyear VARCHAR(50), filmrating VARCHAR(50))")

# ----------------------------------------------------------------------------------------------------------------------
# Gets all Movie/Show IMDB URLs
def scrape_urls(url_page):

    URL = url_page

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    # Scrape URLS
    scrape_url = soup.find_all("span", class_="lister-item-header")

    temp_urls = []
    all_urls = []
    for entry in scrape_url:
        temp_urls.append(entry.find("a", href=True))
    for href in temp_urls:
        all_urls.append('https://www.imdb.com/' + href['href'])

    return all_urls


# ----------------------------------------------------------------------------------------------------------------------
# Gets all Data from Movie/Show IMDB URLs
def scrape_data(url_list):

    all_media = []
    all_titles = []
    all_genres = []
    all_ratings = []
    all_lengths = []
    all_releaseYear = []
    all_filmRatings = []

    # Create Dictionary of Values

    for url in range(0, len(url_list)):

            headers = {
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

            page = requests.get(url_list[url], headers=headers)

            soup = BeautifulSoup(page.content, 'html.parser')

            # Media Type
            all_media.append(soup.find("li", class_="ipc-inline-list__item").get_text())

            # print(all_media)
            # print(len(all_media))

            # Movie/Show Titles
            all_titles.append(soup.find("h1").get_text())

            # print(all_titles)
            # print(len(all_titles))

            # Genres
            scrape_genres = soup.find_all("div", class_="ipc-page-content-container ipc-page-content-container--center")[2]
            all_genres.append(([item.get_text(strip=True) for item in scrape_genres.select("span.ipc-chip__text")]))

            # print(all_genres)
            # print(len(all_genres))

            # Ratings
            if soup.find("div", {'data-testid':'hero-rating-bar__aggregate-rating__score'}) is None:
                all_ratings.append(None)
            else:
                all_ratings.append(soup.find("div", {'data-testid':'hero-rating-bar__aggregate-rating__score'}).find("span").get_text())

            # print(all_ratings)
            # print(len(all_ratings))

            # Release Year
            all_releaseYear.append(soup.select("li", class_="ipc-inline-list__item")[3].select_one("span").get_text())

            # print(all_releaseYear)
            # print(len(all_releaseYear))

            # Length or Film Rating
            if soup.select("li", class_="ipc-inline-list__item")[4].select_one("span") is None:
                all_filmRatings.append(None)
                if "h" in soup.select("li", class_="ipc-inline-list__item")[4].get_text() or "min" in soup.select("li", class_="ipc-inline-list__item")[4].get_text():
                    all_lengths.append(soup.select("li", class_="ipc-inline-list__item")[4].get_text())
                else:
                    all_lengths.append(None)
            else:
                all_filmRatings.append(soup.select("li", class_="ipc-inline-list__item")[4].select_one("span").get_text())
                if "h" in soup.select("li", class_="ipc-inline-list__item")[5].get_text() or "min" in soup.select("li", class_="ipc-inline-list__item")[5].get_text():
                    all_lengths.append(soup.select("li", class_="ipc-inline-list__item")[5].get_text())
                else:
                    all_lengths.append(None)

            # print(all_lengths)
            # print(len(all_lengths))

            # print(all_filmRatings)
            # print(len(all_filmRatings))

    return all_media, all_titles, all_genres, all_ratings, all_lengths, all_releaseYear, all_filmRatings


# ----------------------------------------------------------------------------------------------------------------------
def start_url_scrape():
    # Number of IMDB Pages of Netflix Originals
    pages = 1

    all_urls = []

    for page in range(1, pages + 1):
        temp_url = scrape_urls('https://www.imdb.com/list/ls093971121/?sort=list_order,asc&st_dt=&mode=simple&page=' + str(page) + '&ref_=ttls_vw_smp')
        for url in range(0, len(temp_url)):
            all_urls.append(temp_url[url])

    return all_urls

# ----------------------------------------------------------------------------------------------------------------------

all_urls = start_url_scrape()

all_media, all_titles, all_genres, all_ratings, all_lengths, all_releaseYear, all_filmRatings = scrape_data(all_urls)

# ----------------------------------------------------------------------------------------------------------------------

mycursor.executemany("INSERT INTO heroku_4cab588d1f5a65c.information (media, title, genre, rating, length, releaseyear, filmrating) VALUES (%s, %s, %s, %s, %s, %s, %s)", all_media, all_titles, all_genres, all_ratings, all_lengths, all_releaseYear, all_filmRatings)

# mycursor.executemany("INSERT INTO Information (title) VALUES (%s)", titles)

#db.commit()

# mycursor.execute("SELECT title FROM Information WHERE title = 'House of Cards'")

# for x in mycursor:
#    print(x[0])
