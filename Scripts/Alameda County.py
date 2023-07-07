import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import Function, API

headers = {

}
location = {
    'name': 'Alamenda County',
    'type': 'county'
}


def getdata(url):
    LastestDate = datetime(2023, 1, 1)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.find_all("div", class_="archive")
    for table in tables:
        if table.find("h3").text.strip() == "BOS Regular Meetings":
            element_div = table.find("tbody")
            rows = element_div.select("tr")
            for row in rows:
                cells = row.select("td")
                span = cells[1].find("span").text.strip()
                string_ = cells[1].text.strip().replace(span, "")
                date = Function.convert_date(string_, "%b %d, %Y")
                name = "County_Alameda_" + Function.nameString(date) + "_" + span
                if date > LastestDate:
                    if not API.check_meeting_exists(name):
                        Mp4Link = ""
                        MinutesLink = ""
                        Mp3Link = ""
                        if cells[4].text.strip() != "":
                            MinutesHref = cells[4].select("a")
                            for m_href in MinutesHref:
                                MinutesLink = "https:" + m_href.get('href')
                                #Function.download_minutes(MinutesLink, "Alameda County", name + "_M", headers,Function.nameString(date))
                        if cells[6].text.strip() != "":
                            Mp3Href = cells[6].select("a")
                            for mp3_href in Mp3Href:
                                Mp3Link = mp3_href.get('href')
                                #Function.download_mp3(Mp3Link, "Alameda County", name, Function.nameString(date))
                        if cells[6].text.strip() == "" and cells[7].text.strip() != "":
                            Mp4Href = cells[7].select("a")
                            for mp4_href in Mp4Href:
                                Mp4Link = mp4_href.get('href')
                                #Function.download_video(Mp4Link, "Alameda County", name, Function.nameString(date))
                        if cells[3].text.strip() != "" :
                            AgendasHref = cells[3].select("a")
                            for href in AgendasHref:
                                AgendasLink = "https:" + href.get('href')
                                Function.download_pdf(AgendasLink, "Alameda County", name + "_A", headers,Function.nameString(date))
                                meeting_data = {
                                    'name': f'{name}',
                                    'media_url': f'{Function.check_empty({Mp4Link} | {Mp3Link})}',
                                    'agenda_url': f'{AgendasLink}',
                                    'minutes_url': f'{Function.check_empty(MinutesLink)}',
                                    'meeting_date': f'{Function.convert_to_date_for_push(string_,"%b %d, %Y")}',
                                    'meeting_time': f'00:00',
                                    'meta_data': {
                                        'meeting_time_manipulate' : True,
                                        'site_url': f'https://bos.acgov.org/broadcast/'
                                    }
                                }
                                API.post_meeting_to_server(location, meeting_data)
                                print(API.post_meeting_to_server(location, meeting_data))
                else:
                    break


def Crawling_data():
    url = "https://alamedacounty.granicus.com/ViewPublisher.php?view_id=2"
    getdata(url)
    print("Alameda County is Done")
Crawling_data()
