import random
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from utils import Function,API

_headers = {
"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"Accept-Encoding":"gzip, deflate",
"Accept-Language":"vi,vi-VN;q=0.9,en-US;q=0.8,en;q=0.7",
"Cache-Control":"max-age=0",
"Connection":"keep-alive",
"Cookie":"WebUserConnected=False; AgencyName=AlpineCountyCA; DepartmentID=0; __utmc=31658478; __utmz=31658478.1688030659.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1979929033.1688030659; _gid=GA1.2.613696358.1688030659; __utma=31658478.1979929033.1688030659.1688037948.1688045444.3; __utmt=1; __utmb=31658478.6.10.1688045444; _gat=1; _ga_7R5E5J3P4X=GS1.2.1688045446.3.1.1688045666.0.0.0",
"Host":"alpinecountyca.iqm2.com",
"Upgrade-Insecure-Requests":"1",
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}
location = {
    'name': 'Calaveras County',
    'type': 'county'
}
def getID (url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_value = query_params.get("ID")[0]
    return id_value
def getdata(url,headers):
    r = requests.get(url,headers=headers)
    soup = BeautifulSoup(r.content,'lxml')
    table = soup.find("div", class_="Section")
    rows = table.find_all("div", class_=re.compile("Row MeetingRow|Row MeetingRow Alt"))

    for row in rows:
        formatted_time = ""
        millsecond = ""
        m_href = ""
        a_href = ""
        v_href = ""
        date_string = row.select("div.RowLink")
        hrefID = row.select_one("div.RowLink a")
        for string in date_string:
            datetime_obj = datetime.strptime(string.text.strip(), "%b %d, %Y %I:%M %p")
            formatted_time = Function.nameString(datetime_obj)
            millsecond = int(datetime_obj.timestamp())
        first_cells = row.find("div", class_="RowRight MeetingLinks")
        cells = first_cells.find_all("div")
        name = "Calaveras_County_" + formatted_time + "_" + str(millsecond)
        if not API.check_meeting_exists(name):
            if len(cells) >= 3 and cells[1].select_one("a").get('href') != "":
                linkagenda = cells[0].select_one("a")
                a_href = "http://calaverascountyca.iqm2.com/Citizens/" + linkagenda.get('href')
                Function.download_pdf(a_href, "Amador County", name + "_A", headers,formatted_time)   #download pdf
                if len(cells) >= 5 and cells[4].select_one("a").get('href') != "":
                    linkVideo = f"http://calaverascountyca.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID={getID(hrefID.get('href'))}&Format=Minutes"
                    newresponse = requests.get(linkVideo,headers=headers)
                    newsoup = BeautifulSoup(newresponse.content,'lxml')
                    html_code = newsoup.prettify()
                    start_index = html_code.find('<!-- MEDIA URL:')
                    end_index = html_code.find('-->', start_index)
                    v_href = html_code[start_index+16:end_index]
                    try :
                        print("video downloaded")
                        Function.download_video(v_href, "Calaveras County", name, formatted_time) #download video
                    except :
                        print("Cant download this link")


            if len(cells) >= 4 and cells[3].select_one("a").get('href') != "":
                linkMinutes = cells[3].select_one("a")
                m_href = "http://calaverascountyca.iqm2.com/Citizens/" + linkMinutes.get('href')
                Function.download_minutes(m_href, "Calaveras County", name + "_M", headers,formatted_time) #download minutes
            meeting_data = {
                'name': f'{name}',
                'media_url': f'{v_href}',
                'agenda_url': f'{a_href}',
                'minutes_url': f'{m_href}',
                'meeting_date': f'{formatted_time}',
                'meeting_time': f'{millsecond}',
                'meta_data': {
                    'site_url': f'http://calaverascountyca.iqm2.com/Citizens/Default.aspx'
                }
            }
            API.post_meeting_to_server(location, meeting_data)



def Crawling_data() :
    url = "http://calaverascountyca.iqm2.com/Citizens/Calendar.aspx?From=1/1/2023&To=12/31/2023"
    getdata(url,_headers)
    print("Calaveras county is done")