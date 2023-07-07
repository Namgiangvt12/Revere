import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import Function,API
from urllib.parse import urlparse, parse_qs

header = {

}
location = {
    'name': 'Butte County',
    'type': 'county'
}

def getID(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    id_value = query_params.get("clip_id")[0]
    return id_value


def getdata(url, headers):
    EarlyestDate = datetime(2023, 1, 1)
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    rows = soup.find_all("tr", class_="listingRow")
    for row in rows:
        cells = row.find_all("td")
        date_string = cells[1].text.strip()[:12]
        formatted_date = Function.convert_date(date_string, "%b %d, %Y")
        millsecond = int(formatted_date.timestamp())
        if (formatted_date > EarlyestDate):

            if len(cells) > 4:
                title = cells[0].text.strip()
                if "Board of Supervisors" in title:
                    name = "Butte_County_" + Function.nameString(formatted_date) + "_" + str(millsecond)
                    if not API.check_meeting_exists(name):
                        linkAgendas = cells[3].find_all("a")
                        for linkAgenda in linkAgendas:
                            href = "https:" + linkAgenda.get('href')
                            name = "Butte_County_" + Function.nameString(formatted_date) + "_" + str(millsecond)
                            Function.download_htmltopdf(href, "Butte County", name + "_A", header, "Agendas",
                                                        Function.nameString(formatted_date))  # DOWNLOAD AGENDA
                            hrefVideo = f"https://buttecounty.granicus.com/player/clip/{getID(href)}?view_id=2"
                            newrequest = requests.get(hrefVideo)
                            newsoup = BeautifulSoup(newrequest.content, 'lxml')
                            links = newsoup.find("source", type="application/x-mpegurl")
                            realLink = links.get('src').replace("OnDemand/_definst_/mp4:archive/", "").replace(
                                "/playlist.m3u8", "").replace("https://archive-stream.granicus.com",
                                                              "https://archive-video.granicus.com")
                            Function.download_video(realLink, "Butte County", name, Function.nameString(formatted_date))
                            meeting_data = {
                                'name': f'{name}',
                                'media_url': f'{realLink}',
                                'agenda_url': f'{href}',
                                'minutes_url': f'N/A',
                                'meeting_date': f'{Function.nameString(formatted_date)}',
                                'meeting_time': f'{millsecond}',
                                'meta_data': {
                                    'site_url': f'http://buttecounty.granicus.com/ViewPublisher.php?view_id=2'
                                }
                            }
                            API.post_meeting_to_server(location, meeting_data)



def Crawling_data():
    url = "http://buttecounty.granicus.com/ViewPublisher.php?view_id=2"
    getdata(url, headers=header)
    print("Butte County is Done")