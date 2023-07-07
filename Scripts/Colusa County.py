import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from utils import Function, API

header = {

}
location = {
    'name': 'Colusa County',
    'type': 'county'
}
m_href = ""


def getminutes(url, headers):
    global m_href
    r = requests.get(url, headers=headers)
    print(r.status_code)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        tables = soup.find("td", class_="pageStyles")
        rows = tables.select("table", summary="Archive Details")
        for row in rows:
            text = row.find("img")
            if text is not None:
                try:
                    dateText = text.get("alt")
                    date_string = dateText.split(" ")[1]
                    date_only = date_string.split(" ")[0]
                    date_object = datetime.strptime(date_only, "%m-%d-%y")
                    formatted_date = date_object.strftime("%m_%d_%Y")
                    millsecond = date_object.timestamp()
                    month, day, year = date_only.split("-")
                    year2 = int(year)
                    if year2 > 22:
                        name = "County_Colusa_" + formatted_date + "_" + str(millsecond)
                        ref = row.find("a")
                        if not API.check_meeting_exists(name):
                            if ref is not None:
                                m_href = "https://www.countyofcolusa.org/" + ref.get("href")
                                Function.download_minutes(m_href, "Colusa County", name + "_M", header, formatted_date) #download minutes
                    else:
                        print("Downloaded Minutes")
                        break
                except Exception as e:
                    print("Error", str(e))
                    break

    else:
        print("Cant connect to server")


def getagendas(url, headers):
    r = requests.get(url, headers=headers)
    print(m_href)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'lxml')
        tables = soup.find("td", class_="pageStyles")
        rows = tables.select("table", summary="Archive Details")
        for row in rows:
            text = row.find("img")
            if text is not None :
                try:
                    dateText = text.get("alt")
                    date_string = dateText.split(" ")[0]
                    date_only = date_string.split(" ")[0]
                    date_string = date_only.replace("-", "_")
                    formatted_date = Function.convert_date(date_only, "%m-%d-%Y")
                    millsecond = int(formatted_date.timestamp())
                    month, day, year = date_only.split("-")
                    year2 = int(year)
                    if year2 > 2022:
                        name = "County_Colusa_" + date_string + "_" + str(millsecond)
                        if not API.check_meeting_exists(name):
                            ref = row.find("a")
                            if ref is not None:
                                a_href = "https://www.countyofcolusa.org/" + ref.get("href")
                                Function.download_pdf(a_href, "Colusa County", name + "_A", header, date_string)  # download agendas
                                meeting_data = {
                                    'name': f'{name}',
                                    'media_url': f'N/A',
                                    'agenda_url': f'{a_href}',
                                    'minutes_url': f'{m_href}',
                                    'meeting_date': f'{date_string}',
                                    'meeting_time': f'{str(millsecond)}',
                                    'meta_data': {
                                        'site_url': f'https://www.countyofcolusa.org/archive.aspx'
                                    }
                                }
                                API.post_meeting_to_server(location, meeting_data)

                    else:
                        print("Done")
                        break
                except Exception as e:
                    print("Error", str(e))
                    break

    else:
        print("Cant connect to server")


MinutesUrl = "https://www.countyofcolusa.org/Archive.aspx?AMID=38&Type=&ADID="
AgendaUrl = "https://www.countyofcolusa.org/Archive.aspx?AMID=37&Type=&ADID="


def Crawling_data():
    print("-----------Downloading Minutes----------")
    getminutes(MinutesUrl, header)
    print("-----------Downloading Agendas----------")
    getagendas(AgendaUrl, header)
    print("Colusa County is done")
