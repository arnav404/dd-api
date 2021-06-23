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

avgs = [0, 0, 0, 0, 0]


@app.route("/")
@cross_origin()
def helloWorld():
    return json.dumps({"data": "Hello World"})


@app.route("/getavgs/<pl>", methods=["POST", "GET"])
@cross_origin()
def getAverages(pl):
    player = pl

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

    return json.dumps({"data": avgs})


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

    return json.dumps({"data": pts})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)
