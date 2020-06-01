'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
import requests
from pathlib import Path
import os

def find_pdf(link):
    # documents_link takes you to the 'documents' page for the fund
    documents_link = link + '&tab=12'
    
    # Make a request to the page
    r = requests.get(documents_link)
    html_response = r.text
    
    # Find the report we want
    
def download_pdf(lnk):

    from selenium import webdriver
    from time import sleep

    options = webdriver.ChromeOptions()

    download_folder = str(os.path.realpath(os.getcwd()))

    profile = {"plugins.plugins_list": [{"enabled": False,
                                         "name": "Chrome PDF Viewer"}],
               "download.default_directory": download_folder,
               "download.extensions_to_open": ""}

    options.add_experimental_option("prefs", profile)

    print("Downloading file from link: {}".format(lnk))
    driver_path = Path('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver')
    driver = webdriver.Chrome(str(driver_path), options = options)
    # driver = webdriver.Chrome(chrome_options = options)
    driver.get(lnk)

    filename = lnk.split("/")[4].split(".cfm")[0]
    print("File: {}".format(filename))

    print("Status: Download Complete.")
    print("Folder: {}".format(download_folder))

    driver.close()
    
def download_pdf2(lnk):
    from selenium import webdriver

    download_dir = str(os.path.realpath(os.getcwd()))
    options = webdriver.ChromeOptions()
    
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
                   "download.default_directory": download_dir , "download.extensions_to_open": "applications/pdf"}
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver.exe', chrome_options=options)  # Optional argument, if not specified will search path.
    
    driver.get(lnk)




# if __name__ == '__main__':
#     # link = 'https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=F00000YJ90'
#     # find_pdf(link)
#     # download_pdf('https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=F00000YJ90&tab=14&DocumentId=f61acaaa002b8eba3f904215230a8834&Format=PDF')
#     download_pdf('http://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=1&BorP=P&TID=ALB&CTRY=USA&DT=06/17/2002&DAY=D&STYLE=EQB')
#     # download_pdf('http://spark-public.s3.amazonaws.com/nlp/slides/AdvancedMaxent.pdf')


import os
from selenium import webdriver
from time import sleep
# from selenium.webdriver.chrome.options import Options

url_id = 'F00000YJ90'

download_dir = str(os.path.realpath(os.getcwd()))

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs',  {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
    "plugins.always_open_pdf_externally" : True,
    "download.extensions_to_open": "application/pdf"
    }
)


print('Navigating to the PDF')

driver_path = Path('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver')



browser = webdriver.Chrome(str(driver_path), options = options)

url = 'https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=' + url_id + '&tab=14&DocumentId=f61acaaa002b8eba3f904215230a8834&Format=PDF'
browser.get(url)
sleep(2)
redirect = browser.find_element_by_id('GoDirectToMS')
redirect.click()
# sleep(1)

# individual_button = browser.find_element_by_id('individualinvestor')
# individual_button.click()

# accept_button = browser.find_element_by_id('_evidon-accept-button')
# accept_button.click()

sleep(2)
pdf_url = browser.find_element_by_id('documentFrame').get_attribute("src")

browser.get(pdf_url)

print('Downloading...')

if not os.path.exists('./pdf_downloads'):
    os.mkdir('./pdf_downloads')


while not 'download.pdf' in os.listdir():
    pass


save_path = Path('./pdf_downloads')
save_path /= (url_id + '.pdf')

print('File downloaded. Saving it to ' + str(save_path))

os.rename('download.pdf', save_path)

# download = browser.find_element_by_xpath('//*[@id="download"]')

# download.click()

