import random
import requests
from bs4 import BeautifulSoup
from utils import Function, API

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "vi,vi-VN;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "Setting-57-Calendar Options=info|; Setting-57-ASP.calendar_aspx.gridCalendar.SortExpression=MeetingStartDate DESC; __utmz=196938163.1688311346.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Setting-57-Calendar Body=4317; Setting-57-Calendar Year=2023; ASP.NET_SessionId=0eb1ri10vjavjjxobl4knam3; BIGipServerinsite.legistar.com_443=908198666.47873.0000; __utma=196938163.1528487023.1688311346.1688311346.1688354025.2; __utmc=196938163",
    "Host": "eldorado.legistar.com",
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

location = {
    'name': 'El Dorado County',
    'type': 'county'
}

def getdata(url, header_):
    response = requests.get(url, headers=header_)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        table = soup.find("table", class_="rgMasterTable")
        rows = table.select("tbody tr")
        if rows:
            for row in rows:
                cells = row.select("td")
                string_date = cells[1].text.strip().replace("/","_")
                date = Function.convert_date(string_date, "%m_%d_%Y")
                millsecond = int(date.timestamp())
                name = "County_EL_Dorado_" + string_date + "_" + str(millsecond)
                if not API.check_meeting_exists(name):
                    m_href = ""
                    a_href = ""
                    v_href = ""
                    if cells[8].text.strip() != "Not available" :
                        VideoHref = cells[8].select("span a")
                        for v_href in VideoHref :
                            VideosLink = "https://eldorado.legistar.com/" + v_href.get('onclick').replace(r"window.open('","").replace(r"','video');return false;","")
                            newrequest = requests.get(VideosLink)
                            soup2 = BeautifulSoup(newrequest.content,"lxml")
                            rows = soup2.find("a", class_="download-option flex-col-center")
                            if rows :
                                v_href = rows.get('href')
                                Function.download_video(v_href, "El Dorado County", name, string_date)
                    if cells[6].text.strip() != "Not available" :
                        AgendasHref = cells[6].select("span a")
                        for href in AgendasHref :
                            a_href = "https://eldorado.legistar.com/" + href.get('href')
                            Function.download_pdf(a_href, "El Dorado County", name + "_A", header_, string_date)
                    if cells[7].text.strip() != "Not available" :
                        MinutesHref = cells[7].select("span a")
                        for m_href_ in MinutesHref :
                            m_href = "https://eldorado.legistar.com/" + m_href_.get('href')
                            Function.download_minutes(m_href, "El Dorado County", name + "_M", header_, string_date)
                    meeting_data = {
                        'name': f'{name}',
                        'media_url': f'{v_href}',
                        'agenda_url': f'{a_href}',
                        'minutes_url': f'{m_href}',
                        'meeting_date': f'{string_date}',
                        'meeting_time': f'{str(millsecond)}',
                        'meta_data': {
                            'site_url': f'https://eldorado.legistar.com/Calendar.aspx'
                        }
                    }
                    API.post_meeting_to_server(location, meeting_data)

def Crawling_data():
    getdata("https://eldorado.legistar.com/Calendar.aspx", headers)
    print("El Dorado County is done")
