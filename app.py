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

avgs = [0, 0, 0, 0, 0, 0]

season_stats_url = (
    "https://www.basketball-reference.com/leagues/NBA_" + year + "_per_game.html"
)

uClient = uReq(season_stats_url)
statsheet_html = uClient.read()
uClient.close()

statsheet_soup = soup(statsheet_html, "html.parser")


@app.route("/")
@cross_origin()
def helloWorld():
    return json.dumps({"data": "Hello World"})


# This endpoint returns
# 1) The gamelog -- the number of points, rebounds, assists, steals,
# blocks, and turnovers scored
# 2) The averages -- the season averages in those categories
# 3) The percentiles -- the percentage of players who scored less
# than the player in each category
@app.route("/getstats/<player>", methods=["POST", "GET"])
@cross_origin()
def getAverages(player):

    # GETTING THE DATA:

    # player string url
    player_input = (
        player.split(" ")[1][0:5].lower() + player.split(" ")[0][0:2].lower() + "01"
    )

    # url of bball-reference page
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
    uClient = uReq(season_stats_url)
    statsheet_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    data = page_soup.find("div", {"class": "p1"}).findAll("div")

    for i in range(len(data)):
        if data[i].find("h4")["data-tip"] == "Points":
            avgs[0] = data[i].find("p").text
        if data[i].find("h4")["data-tip"] == "Total Rebounds":
            avgs[1] = data[i].find("p").text
        if data[i].find("h4")["data-tip"] == "Assists":
            avgs[2] = data[i].find("p").text

    data = page_soup.find("div", {"class": "p2"}).findAll("div")

    for i in range(len(data)):
        if data[i].find("h4")["data-tip"] == "Field Goal Percentage":
            avgs[3] = data[i].find("p").text
        if data[i].find("h4")["data-tip"] == "3-Point Field Goal Percentage":
            avgs[4] = data[i].find("p").text
        if data[i].find("h4")["data-tip"] == "Free Throw Percentage":
            avgs[5] = data[i].find("p").text

    # rows of the table
    data = page_soup.findAll("table", {"id": "pgl_basic"})[0].tbody.findAll("tr")

    stats = ["pts", "trb", "ast", "stl", "blk", "tov"]
    log = []

    for j in range(len(stats)):
        statArr = []
        for i in range(len(data)):
            try:
                statArr.append(int(data[i].find("td", {"data-stat": stats[j]}).text))
            except (AttributeError, TypeError, NameError):
                pass
        log.append(statArr)

    data = statsheet_soup.findAll("table", {"class": "stats_table"})[0].tbody.findAll(
        "tr", {"class": "full_table"}
    )

    percentiles = []
    stats = ["pts_per_g", "trb_per_g", "ast_per_g", "fg_pct", "fg3_pct", "ft_pct"]
    for j in range(6):
        percentile_stat = []
        for i in range(len(data)):
            percentile_stat.append(
                float("0" + data[i].find("td", {"data-stat": stats[j]}).text)
            )
        percentile_stat.sort()
        average = float(avgs[j])
        if j > 2:
            formatted_avg = 3
            average = round(float(avgs[j]) / 100, formatted_avg)
        percentiles.append(percentile_stat.index(average) / len(percentile_stat))

    return json.dumps({"avgs": avgs, "gamelog": log, "percentiles": percentiles})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
