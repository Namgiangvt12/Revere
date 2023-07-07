import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request
from utils import Function

url = "https://glenncounty.granicus.com/ViewPublisher.php?view_id=9"


def getdata(url_, header_):
    year2023 = datetime(2023, 1, 1)
    browser = webdriver.Chrome()
    browser.maximize_window()
    browser.get(url_)
    time.sleep(4)
    soup = BeautifulSoup(browser.page_source, 'lxml')
    table = soup.find("table", class_="sortable")
    browser.quit()
    rows = table.select("tbody tr")
    for row in rows:
        cells = row.select("td")
        span = cells[1].find("span").text.strip()
        string_ = cells[1].text.strip().replace(span, "")
        date = Function.convert_date(string_, "%b %d, %Y")
        if date > year2023:
            name = "County_Glenn_" + Function.nameString(date) + "_" + str(random.randint(1, 1000))
            linkElements = cells[5].find_all("a")
            for linkElement in linkElements:
                if linkElement.text.strip() == "Audio":
                    hrefLink = linkElement.get("onclick")
                    hrefLink = hrefLink.replace(r"window.open('//", "").replace(
                        r"','player','toolbar=no,directories=no,status=yes,scrollbars=yes,resizable=yes,menubar=no')",
                        "")
                    link = "https://" + hrefLink
                    newrequest = requests.get(link)
                    soup2 = BeautifulSoup(newrequest.content, "lxml")
                    links = soup2.find("source", type="application/x-mpegurl")
                    realLink = links.get('src').replace("OnDemand/_definst_/mp4:archive/", "").replace("/playlist.m3u8",
                                                                                                       "").replace(
                        "https://archive-stream.granicus.com", "https://archive-video.granicus.com")
                    Function.download_video(realLink, "Glenn County", name, Function.nameString(date))  # download mp4
            print()
            if cells[3].text.strip() != "":
                AgendasHref = cells[3].select("a")
                for href in AgendasHref:
                    AgendasLink = "https:" + href.get('href')
                    response = urllib.request.urlopen(AgendasLink)
                    url_of_request = response.geturl()
                    split_parts = url_of_request.split("_")
                    string_after_underscore = split_parts[-1]
                    split_parts = string_after_underscore.split("%26")
                    string_after_underscore = split_parts[0]
                    AgendasLink = f"https://glenncounty.granicus.com/DocumentViewer.php?file=glenncounty_{string_after_underscore}&view=1"
                    Function.download_pdf(AgendasLink, "Glenn County", name, header_,
                                          Function.nameString(date))  # download agendas
            print()
            if cells[4].text.strip() != "":
                MinutesHref = cells[4].select("a")
                for m_href in MinutesHref:
                    MinutesLink = "https:" + m_href.get('href')
                    Function.download_htmltopdf(MinutesLink, "Glenn County", name, header_, "Minutes",
                                                Function.nameString(date))  # download minutes
        else:
            break


headers = {

    "Referer": "https://glenncounty.granicus.com/ViewPublisher.php?view_id=9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "vi,vi-VN;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "ga=GA1.1.1649355618.1688111057; _ga_QKSF1VK90C=GS1.1.1688111057.1.1.1688111495.0.0.0; __utmc=204500806; __utmz=204500806.1688368176.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=204500806.1649355618.1688111057.1688368176.1688368176.1; __utmc=204500806; __utmz=204500806.1688368176.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=204500806.0.10.1688371528; __utma=204500806.1649355618.1688111057.1688368176.1688368176.1; __utmb=204500806.1.10.1688371528; __utmt=1; __utmt_b=1",
    "Host": "glenncounty.granicus.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
                  "Safari/537.36",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
}


def Crawling_data():
    getdata(url, headers)
    print("Glenn County is done")
