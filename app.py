from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import os
import json

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

player = "James Harden"
year = "2021"
stat = "pts"

url2 = "https://www.basketball-reference.com/leagues/NBA_" + year + "_per_game.html"

client2 = uReq(url2)
totals_html = client2.read()
client2.close()

soup2 = soup(totals_html, "html.parser")

totals = soup2.findAll("table", {"id": "per_game_stats"})[0].tbody.findAll(
    "tr", {"class": "full_table"}
)


@app.route("/")
@cross_origin()
def getAverage():
    return json.dumps({"data": "Hello World"})


@app.route("/getlogs/<pl>/<st>", methods=["POST", "GET"])
@cross_origin()
def getGamelog(pl, st):
    player = pl
    stat = st
    # player string url
    player_input = (
        player.split(" ")[1][0:5].lower() + player.split(" ")[0][0:2].lower() + "01"
    )

    # url of bball reference page
    my_url = (
        "https://www.basketball-reference.com/players/c/"
        + player_input
        + "/gamelog/"
        + year
        + "#pgl_basic"
    )

    # getting the data
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    # rows of the table
    data = page_soup.findAll("table", {"id": "pgl_basic"})[0].tbody.findAll("tr")

    pts = []

    for i in range(len(data)):
        try:
            pts.append(int(data[i].find("td", {"data-stat": stat}).text))
        except (AttributeError, TypeError, NameError):
            pass

    return json.dumps({"data": str(pts)[1:-1]})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
