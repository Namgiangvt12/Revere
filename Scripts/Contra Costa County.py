import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import Function, API
location = {
    'name': 'Contra County',
    'type': 'county'
}
headers = {

}
def getdata (url,header) :
    response = requests.get(url,headers=header)
    if response.status_code == 200 :
        soup = BeautifulSoup(response.content,'lxml')
        tables = soup.find('table', class_='listingTable', id='archive')
        rows = tables.select("tbody tr")
        for row in rows :
            cells = row.select("td")
            date_string = cells[1].text.strip()
            date = Function.convert_date(date_string, "%b %d, %Y")
            millsecond = int(date.timestamp())
            string_date = str(date.month) + "_" + str(date.day) + "_" + str(date.year)
            if date > datetime(2023,1,1) :
                name = "County_Contra_Costa_" + string_date + "_" + str(millsecond)
                a_href = ""
                if not API.check_meeting_exists(name):
                    if cells[3].text.strip() != "" :
                        a_href = cells[3].find("a").get('href').replace("//contra-costa","https://contra-costa")
                        Function.download_pdf(a_href, "Colusa County", name + "_A", header, date_string) #download agendas
                    if cells[6].text.strip() != "":
                        v_href = cells[6].find("a").get('href')
                        Function.download_video(v_href, "Contra Costa", name, string_date)  #download video
                meeting_data = {
                    'name': f'{name}',
                    'media_url': f'N/A',
                    'agenda_url': f'{a_href}',
                    'minutes_url': f'N/A',
                    'meeting_date': f'{date_string}',
                    'meeting_time': f'{str(millsecond)}',
                    'meta_data': {
                        'site_url': f'https://contra-costa.granicus.com/ViewPublisher.php?view_id=1'
                    }
                }
                API.post_meeting_to_server(location, meeting_data)

def Crawling_data():
    getdata("https://contra-costa.granicus.com/ViewPublisher.php?view_id=1",headers)
    print("Contra Costa County is Done")
Crawling_data()