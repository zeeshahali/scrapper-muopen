import os
import docx
import shutil
import requests
from selenium import webdriver
import time
import datetime
import urllib.parse



chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : os.getcwd() + "/Downloads"}
chrome_options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(options=chrome_options, executable_path="chromedriver.exe")

#Parent Directory
date = datetime.datetime.now().strftime("(%Y-%m-%d)(%H.%M.%S)")
parent_dir = os.path.join(os.getcwd(), "Data" + date)

def get_sheet():
    sheet_title = ""
    value = ""
    exists = True
    try:
        Sheet = driver.find_element_by_id("sheetmusic-download-button")
        value = Sheet.get_attribute("href")
        index = value.split("=")
        myTitle = index[1]
        rsheet_title = urllib.parse.unquote(myTitle)
        sheet_title = rsheet_title.replace(':', '.')
        chs = ['/', '\\', '\"', '*', '?', '<', '>', '|']
        for ch in chs: sheet_title = sheet_title.replace(ch, '-')
    except:
        return sheet_title, value, False
    return sheet_title, value, True

def download_sheet(path):
    name, url, exists = get_sheet()
    if exists:
        try:
            download_file(path + name, url)
        except:
            download_file(path+"Sheet.pdf", url)

def download_file(file_name, url):
    with requests.get(url, stream=True, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }) as r:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

def directory_name(title, mood, instrument, length):
    if len(title) > 100:
        new_title = title[:99]
        title = new_title
    rdirectory = title + "-"
    if mood != "+ add moods"    :   rdirectory = rdirectory + mood + "-"
    rdirectory = rdirectory + instrument + "-" + str(length)
    directory = rdirectory.replace(':', ';')
    chs = ['/', '\\', '\"', '*', '?', '<', '>', '|']
    for ch in chs: directory = directory.replace(ch, '-')
    return directory

def get_page_data():
    mylist = []
    elements = driver.find_elements_by_tag_name('li')
    for x in range(15, 23):
        mylist.append(elements[x].text)
    return mylist

def get_data(classes, directories, titles, links, pages):
    for clas in classes:
        title = clas.find_element_by_css_selector('div.cell.title').text
        chs = ['/', '\\', '\"', '*', '?', '<', '>', '|']
        for ch in chs: title = title.replace(ch, '-')
        mood = clas.find_element_by_css_selector('div.cell.moods').text
        instruments = clas.find_element_by_css_selector('div.cell.instruments').text
        length = clas.find_element_by_css_selector('div.cell.length').text
        page_link = clas.find_element_by_css_selector('div.cell.title')\
            .find_element_by_css_selector('a').get_attribute('href')
        link = clas.find_element_by_class_name('moplayer-audio').get_attribute('src')
        directory = directory_name(title, mood, instruments, length)
        if directory not in directories:
            directories.append(directory)
            links.append(link)
            titles.append(title)
            pages.append(page_link)
    return directories, titles, links, pages

def create_folder(name):
    directory = os.path.join(parent_dir, name)
    os.mkdir(directory)
    return directory+"/"

def create_doc(filename, url):
    mylist = []
    elements = driver.find_elements_by_tag_name('li')
    for x in range(15, 22):
        mylist.append(elements[x].text)
    document = docx.Document()
    document.add_heading('Information', 0)
    try:
        about = driver.find_element_by_xpath("//div[@itemprop='description']").text
        document.add_heading('About This Piece', level=2)
        document.add_paragraph(about)
    except:
        pass
    document.add_heading('URL:' + url, level=3)
    document.add_paragraph("")
    document.add_heading('INFO:', level=2)
    for items in mylist:
        try:
            index = items.split(":")
            element = index[1]
            index[1] = ":\t"
            index.append(element)
            document.add_paragraph(index)
        except:
            pass
    document.save(filename)

def download_page_data(page, path):
    driver.get(page)
    time.sleep(2)
    create_doc(path+"Information.docx", page)
    download_sheet(path)

def login(email, password):
    driver.find_element_by_name("username").send_keys(email)
    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_xpath('//*[@id="submit-id-submit"]').click()

def data_dir():
    if not os.path.isdir(parent_dir): os.mkdir(parent_dir)

def download_data(url):
    driver.get(url)
    login('saimfd003@gmail.com', '123saim') #add email and password here (<email>, <password>)
    input("Press Enter to continue after you have selected filters")
    directories = []
    titles = []
    links = []
    pages = []
    current_page = 2
    current_url = driver.current_url
    currentList = current_url.split('?', 1)
    while 1:
        classes = driver.find_elements_by_xpath("//div[contains(@class, 'flex-table-row moplayer moplayer-processed')]")
        get_data(classes, directories, titles, links, pages)
        my_url = currentList[0] + '?page=' + str(current_page) + '&' + currentList[1]
        driver.get(my_url)
        try:
            status = driver.find_element_by_xpath("//div[@class='error-404']")
            break
        except:
            current_page = current_page + 1
    data_dir()
    for i in range(len(directories)):
        print("Downloading (" + str(i+1) + "/" + str(len(directories)) + ") .....")
        path = create_folder(directories[i])
        download_page_data(pages[i], path)
        try:
            download_file(path+titles[i]+".mp3", links[i])
        except:
            download_file(path+"Music.mp3", links[i])
    driver.close()

url = "https://musopen.org/account/login/"

download_data(url)