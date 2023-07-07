from utils import API
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import Function

header = {

}
location = {
    'name': 'Amador County',
    'type': 'county'
}


def getdata(url, headers):
    EarlyestDate = datetime(2023, 1, 1)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    table = soup.find("tbody")
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        date_string = cells[1].select_one("time", itemprop_="startDate")
        formatted_date = Function.convert_date(date_string.text.strip(), "%m/%d/%Y %I:%M %p")
        print(Function.nameString(formatted_date))
        millsecond = int(formatted_date.timestamp())
        if (formatted_date > EarlyestDate):
            m_href = ""
            href = ""
            otherhref =""
            name = "County_Amador_" + Function.nameString(formatted_date) + "_" + str(millsecond)
            if not API.check_meeting_exists(name):
                if cells[2].text.strip() != "Not Included":
                    links = cells[2].find_all("a")
                    for link in links:
                        thumnail1 = link.find("img")
                        href = "https://www.amadorgov.org" + link.get('href')
                        if thumnail1.get('src') == "/DefaultContent/Default/_gfx/document_icons/otherdoc.png":
                            #Function.download_mp3(href, "Amador County", name, Function.nameString(formatted_date))  # DOWNLOAD MP3
                            print("Download mp3")
                        else:
                            if 'Agenda' in link.text.strip() and not "Packet" in link.text.strip():
                                Function.download_pdf(href, "Amador County", name + "_A", header,Function.nameString(formatted_date))  # download pdf
                    if cells[3].text.strip() != "Not Included":
                        linkMinutes = cells[3].find_all("a")
                        for linkMinute in linkMinutes:
                            m_href = "https://www.amadorgov.org" + linkMinute.get('href')
                            #Function.download_minutes(m_href, "Amador County", name + "_M", header,Function.nameString(formatted_date))  # DOWNLOAD MINUTES
                    if cells[4].text.strip() != "Not Included":
                        other = cells[4].find("a")
                        otherhref = "https://www.amadorgov.org" + other.get('href')
                        thumbnail = cells[4].find("img")
                        if thumbnail.get('src') != "/DefaultContent/Default/_gfx/document_icons/pdf.png":
                            print("Download mp3")
                            Function.download_mp3(otherhref, "Amador County", name, Function.nameString(formatted_date))  # DOWNLOAD MP3
                    meeting_data = {
                        'name': f'{name}',
                        'media_url': f'{Function.check_empty(otherhref)}',
                        'agenda_url': f'{Function.check_empty(href)}',
                        'minutes_url': f'{Function.check_empty(m_href)}',
                        'meeting_date': f'{Function.convert_to_date_for_push(Function.nameString(formatted_date),"%m_%d_%Y")}',
                        'meeting_time': f'{Function.convert_to_time_for_push(date_string.text.strip(), "%m/%d/%Y %I:%M %p")}',
                        'meta_data': {
                            'site_url': f'{url}'
                        }
                    }
                    API.post_meeting_to_server(location,meeting_data)

def Crawling_data():
    url = "https://www.amadorgov.org/about/agendas-minutes-meetings/-toggle-allpast/-seldept-12#eventdepts_46_108_608"
    getdata(url, headers=header)
    print("Amador County is Done")
Crawling_data()
