import random
from utils import Function
import requests
from bs4 import BeautifulSoup
headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "vi,vi-VN;q=0.9,en-US;q=0.8,en;q=0.7",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Cookie": "__utmz=196938163.1688311346.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.831031792.1688358326; _ga_Q7MG8ZYY5J=GS1.1.1688366198.4.0.1688366198.0.0.0; Setting-448-Calendar Options=info|; Setting-448-ASP.calendar_aspx.gridCalendar.SortExpression=MeetingStartDate DESC; Setting-448-Calendar Body=25778; Setting-448-Calendar Year=2023; ASP.NET_SessionId=yymt2aqmqwbuqtwdz5oplkgi; BIGipServerinsite.legistar.com_443=924975882.47873.0000; __utma=196938163.1528487023.1688311346.1688383886.1688476219.8; __utmc=196938163; __utmt=1; __utmb=196938163.1.10.1688476219",
"Host": "humboldt.legistar.com",
"Sec-Fetch-Dest": "document",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-Site": "none",
"Sec-Fetch-User": "?1",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "Windows",
}
url = "https://humboldt.legistar.com/Calendar.aspx"
def getdata(url_,headers_) :
    response = requests.get(url_,headers=headers)
    if response.status_code == 200 :
        soup = BeautifulSoup(response.content,"lxml")
        table = soup.find("table",class_="rgMasterTable")
        tbody = table.find('tbody')
        rows = tbody.select("tr")
        for row in rows :
            cells = row.select("td")
            date_string = cells[1].text.strip().replace("/","_")
            name = "County_Humboldt_" + date_string + "_" + str(random.randint(1, 2000))
            if cells[6].text.strip() != "Not available" :
                AgendasURL = "https://humboldt.legistar.com/" + cells[6].find("a").get("href")
                Function.download_pdf(AgendasURL, "Humboldt County", name, headers_, date_string) #download agendas
            if cells[7].text.strip() != "Not available" :
                MinutesURL = "https://humboldt.legistar.com/" + cells[7].find("a").get("href")
                Function.download_minutes(MinutesURL, "Humboldt County", name, headers_, date_string) #download minutes
            if cells[8].text.strip() != "Not available" :
                hrefLink = cells[8].find("a").get("onclick")
                hrefLink = hrefLink.replace(r"window.open('", "").replace(
                    r"','video');return false;", "")
                link = "https://humboldt.legistar.com/" + hrefLink
                new_request = requests.get(link)
                soup2 = BeautifulSoup(new_request.content, "lxml")
                links = soup2.find("source", type="application/x-mpegurl")
                realLink = links.get('src').replace("OnDemand/_definst_/mp4:archive/", "").replace("/playlist.m3u8",
                                                                                                   "").replace(
                    "https://archive-stream.granicus.com", "https://archive-video.granicus.com")
                Function.download_video(realLink, "Glenn County", name, date_string)  # download mp4

def Crawling_data():
    getdata(url,headers)
    print("Humboldt County is Done")