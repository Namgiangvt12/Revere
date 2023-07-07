import random
import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from utils import Function, API
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {

}
location = {
    'name': 'Del Norte County',
    'type': 'county'
}
url = "https://delnortecoca.portal.civicclerk.com/?category_id=26"
def getLinkVideo (url) :
    NewBrowser = webdriver.Chrome()
    NewBrowser.maximize_window()
    NewBrowser.get(url)
    wait = WebDriverWait(NewBrowser, 20)
    element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/section/section/section[1]/section/div/div/div/div[2]/div[4]")))
    if element :
        soup = BeautifulSoup(NewBrowser.page_source,'lxml')
        NewBrowser.quit()
        link = soup.find("video",class_="jw-video jw-reset")
        if link :
            return link.get("src")
def getIDMinuteAgendas(url,name_,header_,string_date,millsecond_) :
    a_href = ""
    m_href = ""
    v_hef = ""
    Docsbrower = webdriver.Chrome()
    Docsbrower.maximize_window()
    Docsbrower.get(url)
    wait = WebDriverWait(Docsbrower, 20)
    AgendasBTN = wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/section/section/section[1]/section[2]/iframe")))
    if AgendasBTN :
        OGLink = AgendasBTN.get_attribute("src")
        start_index = OGLink.find("file=")
        a_href = OGLink[start_index + len("file="):]
        Function.download_pdf(a_href, "Del Norte County", name_ + "_A" , header_, string_date) #download agendas
        print("Agendas Done")
        MinutesClicked = wait.until(EC.presence_of_element_located(
        (By.XPATH,"/html/body/div[1]/div/section/section/section[1]/section[1]/section/ul/li[3]")))
        if MinutesClicked :
            MinutesClicked.click()
        MinutesBtn = wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/section/section/section[1]/section[2]/iframe")))
        OGMinutesLink = MinutesBtn.get_attribute("src")
        start_index2 = OGMinutesLink.find("file=")
        m_href = OGMinutesLink[start_index2 + len("file="):]
        Function.download_minutes(m_href, "Del Norte County", name_ + "_M", header_, string_date) #download minutes
    time.sleep(2)
    ChangeToMedia = Docsbrower.find_element(By.XPATH,"/html/body/div[1]/div/section/nav/a[2]")
    ChangeToMedia.click()
    element = wait.until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/section/section/section[1]/section/div/div/div/div[2]/div[4]")))
    if element:
        soup = BeautifulSoup(Docsbrower.page_source, 'lxml')
        Docsbrower.quit()
        links = soup.find("video", class_="jw-video jw-reset")
        if links:
            v_hef = links.get("src")
            Function.download_video(v_hef, "Del Norte County", name_, string_date) #download video
    meeting_data = {
        'name': f'{name_}',
        'media_url': f'{v_hef}',
        'agenda_url': f'{a_href}',
        'minutes_url': f'{m_href}',
        'meeting_date': f'{string_date}',
        'meeting_time': f'{str(millsecond_)}',
        'meta_data': {
            'site_url': f'https://delnortecoca.portal.civicclerk.com/'
        }
    }
    API.post_meeting_to_server(location, meeting_data)

def getdata(url):
    brower = webdriver.Chrome()
    brower.maximize_window()
    brower.get(url)
    time.sleep(5)
    fromdate = brower.find_element(By.XPATH,"/html/body/div[1]/div/main/div/aside/div/div[2]/div/div/div[1]/div/div/input")
    fromdate.send_keys("01/01/2023")
    todate = brower.find_element(By.XPATH,"/html/body/div[1]/div/main/div/aside/div/div[2]/div/div/div[2]/div/div")
    todate.click()
    time.sleep(5)
    scroll_wrap = brower.find_element(By.ID, "scroll-wrap")
    brower.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_wrap)
    time.sleep(3)
    soup = BeautifulSoup(brower.page_source,'lxml')
    table = soup.find("ul",class_="cpp-MuiList-root prmbl-list cpp-157 cpp-161 cpp-MuiList-padding")
    rows = table.select("ul li button")
    for row in rows :
        cell_1 = row.find("div",class_="cpp-MuiGrid-root prmbl-grid cpp-171 cpp-172 cpp-MuiGrid-item cpp-MuiGrid-grid-xs-true")
        if cell_1 is not None :
            millsecond = ""
            try :
                date_string = row.find("h5", class_="cpp-MuiTypography-root cpp-175 prmbl-typography cpp-MuiTypography-h5")
                date = Function.convert_date(date_string.text.strip(), "%b %d, %Y")
                millsecond = date.timestamp()
                string_date = str(date.month) + "_" + str(date.day) + "_" + str(date.year)
            except :
                string_date = "N/A"
                print("cant convert date")
            video = row.select_one("a",class_="cpp-MuiButtonBase-root cpp-MuiIconButton-root prmbl-button cpp-49 prmbl-iconBtn")
            if video :
                name = "County_Del_Norte_" + string_date + str(millsecond)
                if not API.check_meeting_exists(name):
                    linkHref = "https://delnortecoca.portal.civicclerk.com" + video.get('href')
                    number = re.search(r'/(\d+)/', linkHref).group(1)
                    linkDocs = f"https://delnortecoca.portal.civicclerk.com/event/{number}/files"
                    getIDMinuteAgendas(linkDocs,name,headers,string_date,millsecond)
                    print("Downloaded minutes & agendas & video")
    time.sleep(2)
    brower.quit()
def Crawling_data():
    getdata(url)
    print("Del Norte County is Done")
