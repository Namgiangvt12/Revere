import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from utils import Function, API

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "vi,vi-VN;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "__utmz=196938163.1688311346.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=196938163; Setting-445-Calendar Options=info|; Setting-445-ASP.calendar_aspx.gridUpcomingMeetings.SortExpression=MeetingStartDate DESC; Setting-445-ASP.calendar_aspx.gridCalendar.SortExpression=MeetingStartDate DESC; BIGipServerinsite.legistar.com_443=908198666.47873.0000; _gid=GA1.2.504217478.1688358327; Setting-445-Calendar Year=2023; Setting-445-ASP.calendar_aspx.tabCalendar.TabIndex=0; Setting-445-Calendar Body=25588; Setting-445-ASP.meetingdetail_aspx.gridMain.SortExpression=Sequence ASC; ASP.NET_SessionId=3anrciugx5c3gecrzfjzankl; __utma=196938163.1528487023.1688311346.1688361052.1688363305.6; __utmt=1; _gat_gtag_UA_129137734_1=1; _ga_Q7MG8ZYY5J=GS1.1.1688363304.3.1.1688363313.0.0.0; _ga=GA1.1.831031792.1688358326; __utmb=196938163.2.10.1688363305",
    "Host": "fresnocounty.legistar.com",
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
    'name': 'Fresno County',
    'type': 'county'
}

def getdata(url, header_):
    response = requests.get(url, headers=header_)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        tables = soup.find_all("table", class_="rgMasterTable")
        for table in tables:
            rows = table.select("tbody tr")
            if len(rows) > 2:
                for row in rows:
                    cells = row.select("td")
                    string_date = cells[1].text.strip().replace("/", "_")
                    date = Function.convert_date(string_date, "%m_%d_%Y")
                    date_to_push = datetime.strftime(date, "%Y-%m-%d")
                    millsecond = int(date.timestamp())
                    name = "County_Fresno_" + string_date + "_" + str(millsecond)
                    time_of_meeting = cells[3].text.strip()
                    if cells[6].text.strip() != "Not available":
                        print(API.check_meeting_exists(name))
                        if not API.check_meeting_exists(name):
                            m_href = ""
                            a_href = ""
                            v_href = ""
                        # download Video
                            if cells[8].text.strip() != "Not available":
                                VideoHref = cells[8].select("span a")
                                for v_href in VideoHref:
                                    VideosLink = "https://fresnocounty.legistar.com/" + v_href.get('onclick').replace(
                                        r"window.open('", "").replace(r"','video');return false;", "")
                                    newrequest = requests.get(VideosLink)
                                    soup2 = BeautifulSoup(newrequest.content, "lxml")
                                    link = soup2.find("source", type="application/x-mpegurl")
                                    v_href = link.get('src').replace("OnDemand/_definst_/mp4:archive/", "").replace(
                                        "/playlist.m3u8", "").replace("https://archive-stream.granicus.com",
                                                                      "https://archive-video.granicus.com")
                                    #Function.download_video(v_href, "Fresno County", name, string_date) #download video
                                    print()
                            # download Minutes
                            if cells[7].text.strip() != "Not available":
                                MinutesHref = cells[7].select("span a")
                                for m_href_ in MinutesHref:
                                    m_href = "https://fresnocounty.legistar.com/" + m_href_.get('href')
                                    #Function.download_minutes(m_href, "Fresno County", name + "_M", header_, string_date) #download minutes
                                    # download Agendas
                                    if cells[6].text.strip() != "Not available":
                                        AgendasHref = cells[6].select("span a")
                                        for href in AgendasHref:
                                            a_href = "https://fresnocounty.legistar.com/" + href.get('href')
                                            print(a_href)
                                            Function.download_pdf(a_href, "Fresno County", name + "_A", header_,string_date)  # download agendas
                                        meeting_data = {
                                            'name': f'{name}',
                                            'media_url': f'{Function.check_empty(v_href)}',
                                            'agenda_url': f'{a_href}',
                                            'minutes_url': f'{Function.check_empty(m_href)}',
                                            'meeting_date': f'{date_to_push}',
                                            'meeting_time': f'{Function.convert_to_time_for_push(time_of_meeting,"%I:%M %p")}',
                                            'meta_data': {
                                                'site_url': f'https://fresnocounty.legistar.com/Calendar.aspx'
                                            }
                                        }
                                        API.post_meeting_to_server(location, meeting_data)

def Crawling_data():
    getdata("https://fresnocounty.legistar.com/Calendar.aspx", headers)
    print("Fresno County is Done")
Crawling_data()
