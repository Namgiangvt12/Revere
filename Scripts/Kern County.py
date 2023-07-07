import random
from utils import Function
import requests
from bs4 import BeautifulSoup

url = "https://kern.granicus.com/ViewPublisher.php?view_id=56"
headers = {

}


def getdata(url_):
    response = requests.get(url_)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find("table", id="Year2023Archives")
        rows = table.select("tr")
        for row in rows:
            cells = row.select("td")
            if len(cells) == 7:
                parts = cells[2].text.strip().split('-')
                string_date = parts[0].strip().replace("/", "_")
                name = "Kern_County_" + string_date + str(random.randint(1, 2000))
                if cells[5].text.strip() == "Minutes (PDF)":
                    linkMinutes = "https:" + cells[5].find("a").get('href')
                    Function.download_minutes(linkMinutes, "Kern County", name, string_date)  # download minutes
                if cells[6].text.strip() == "Video/Supporting Docs":
                    linktoVideo = "https:" + cells[6].find("a").get('href')
                    new_request = requests.get(linktoVideo)
                    soup2 = BeautifulSoup(new_request.content, "lxml")
                    links = soup2.find("source", type="application/x-mpegurl")
                    realLink = links.get('src').replace("OnDemand/_definst_/mp4:archive/", "").replace(
                        "/playlist.m3u8", "").replace("https://archive-stream.granicus.com",
                                                      "https://archive-video.granicus.com")
                    Function.download_video(realLink, "Imperial County", name, string_date)  # download mp4


def Crawling_data():
    getdata(url)
    print("Kern County is Done")
