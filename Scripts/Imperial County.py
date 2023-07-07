import random
from _datetime import datetime
from utils import Function
import requests
from bs4 import BeautifulSoup
url = "https://imperial.granicus.com/ViewPublisher.php?view_id=2"
headers={

}
def getdata(url_) :
    year2023 = datetime(2023, 1, 1)
    response = requests.get(url_)
    if response.status_code == 200 :
        soup = BeautifulSoup(response.content,"lxml")
        section = soup.find("div",class_= "AccordionPanelContent")
        tbody = section.find("tbody")
        rows = tbody.select("tr")
        for row in rows :
            cells = row.select("td")
            span = cells[1].find("span").text.strip()
            date_str = cells[1].text.strip().replace(span,"")
            date = Function.convert_date(date_str, "%b %d, %Y")
            string_date = Function.nameString(date)
            if date >= year2023 :
                name = "County_Imperial_" + string_date + "_" + str(random.randint(1, 2000))
                hrefAgendas = "https:" + cells[3].find("option",target="blank ").get('value')
                Function.download_htmltopdf(hrefAgendas, "Imperial County", name, headers, "Agendas", string_date) #download Agendas
                linkElements = cells[4].find_all("a")
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
                        realLink = links.get('src').replace("OnDemand/_definst_/mp4:archive/", "").replace(
                            "/playlist.m3u8", "").replace("https://archive-stream.granicus.com",
                                                          "https://archive-video.granicus.com")
                        Function.download_video(realLink, "Imperial County", name, string_date)  # download mp4
            else:
                break
def Crawling_data():
    getdata(url)
    print("Imperial County is Done")