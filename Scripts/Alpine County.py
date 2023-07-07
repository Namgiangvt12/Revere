import random
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from utils import Function,API

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "vi,vi-VN;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "WebUserConnected=False; AgencyName=AlpineCountyCA; DepartmentID=0; __utmc=31658478; __utmz=31658478.1688030659.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1979929033.1688030659; _gid=GA1.2.613696358.1688030659; __utma=31658478.1979929033.1688030659.1688037948.1688045444.3; __utmt=1; __utmb=31658478.6.10.1688045444; _gat=1; _ga_7R5E5J3P4X=GS1.2.1688045446.3.1.1688045666.0.0.0",
    "Host": "alpinecountyca.iqm2.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}
location = {
    'name': 'Alpina County',
    'type': 'county'
}

def getID(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_value = query_params.get("ID")[0]
    return id_value


def getdata(url, headers):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.find("div", class_="Section")
    rows = table.find_all("div", class_=re.compile("Row MeetingRow|Row MeetingRow Alt"))
    for row in rows:
        time = ""
        date_string = row.select("div.RowLink")
        hrefID = row.select_one("div.RowLink a")
        datetime_obj = ""
        millsecond = ""
        for string in date_string:
            datetime_obj = datetime.strptime(string.text.strip(), "%b %d, %Y %I:%M %p")
            time = Function.convert_to_time_for_push(string.text.strip(), "%b %d, %Y %I:%M %p")
            millsecond = int(datetime_obj.timestamp())
            date_string = Function.nameString(datetime_obj)
        first_cells = row.find("div", class_="RowRight MeetingLinks")
        cells = first_cells.find_all("div")
        if len(cells) >= 3 and cells[0].select_one("a").get('href') != "":
            linkagenda = cells[0].select_one("a")
            name = "County_Alpine_" + Function.nameString(datetime_obj) + "_" + str(millsecond)
            href = "http://alpinecountyca.iqm2.com/Citizens/" + linkagenda.get('href')
            print(name)
            print(API.check_meeting_exists(name))
            if not API.check_meeting_exists(name): #check crawled ?
                v_url = ""
                m_url = ""
                Function.download_pdf(href, "Alpine County", name + "_A", headers,Function.nameString(datetime_obj))  # download pdf
                if len(cells) >= 5 and cells[4].select_one("a").get('href') != "":
                    linkVideo = f"http://alpinecountyca.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID={getID(hrefID.get('href'))}&Format=Minutes"
                    newresponse = requests.get(linkVideo, headers=headers)
                    newsoup = BeautifulSoup(newresponse.content, 'lxml')
                    html_code = newsoup.prettify()
                    start_index = html_code.find('<!-- MEDIA URL:')
                    end_index = html_code.find('-->', start_index)
                    v_url = html_code[start_index + 16:end_index]
                    if v_url != "":
                        try:
                            print("download video")
                            #Function.download_video(v_url, "Alpine County", name,Function.nameString(datetime_obj))  # download video
                        except:
                            print("Cant Download this link")
                if len(cells) >= 4 and cells[3].select_one("a").get('href') != "":
                    linkMinutes = cells[3].select_one("a")
                    name = "Alpine_County_" + Function.nameString(datetime_obj) + "_" + str(millsecond)
                    m_url = "http://alpinecountyca.iqm2.com/Citizens/" + linkMinutes.get('href')
                    Function.download_minutes(m_url, "Alpine County", name + "_M", headers,Function.nameString(datetime_obj))  # download minutes
                meeting_data = {
                    'name': f'{name}',
                    'media_url': f'{Function.check_empty(v_url)}',
                    'agenda_url': f'{Function.check_empty(href)}',
                    'minutes_url': f'{Function.check_empty(m_url)}',
                    'meeting_date': f'{Function.convert_to_date_for_push(date_string,"%m_%d_%Y")}',
                    'meeting_time': f'{time}',
                    'meta_data': {
                        'site_url': 'http://alpinecountyca.iqm2.com/citizens/default.aspx'
                    }
                }
                API.post_meeting_to_server(location, meeting_data)
                print(API.post_meeting_to_server(location, meeting_data))

def Crawling_data():
    url = "http://alpinecountyca.iqm2.com/Citizens/Calendar.aspx?From=1/1/2023&To=12/31/2023"
    getdata(url, _headers)
    print("Alpine County is Done !")
Crawling_data()