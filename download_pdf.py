'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
import requests
from pathlib import Path
import os
from selenium import webdriver
from time import sleep


def find_download_pdf(fund_id):
    '''
    Locate and download the most recent report for a fund.

    Parameters
    ----------
    fund_id : str, int
        The id for the relevant fund, found after "id=" in the url.

    Returns
    -------
    None.

    '''
    try:    
        fund_id = str(fund_id)
    except:
        raise Exception('fund_id should be a string or integer')
        
    # We first download the file to the current working directory, then move it
    download_dir = str(os.path.realpath(os.getcwd()))
    
    # Update browser options. This ensures that the pdf is downloaded instead of being viewed in chrome
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
    
    '''
    # TODO - go headless.
    
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    '''
    
    # Initialise a webdriver with the options set
    driver_path = Path('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver')
    browser = webdriver.Chrome(str(driver_path), options = options)

    print('Navigating to the PDF')
    url = 'https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=' + url_id + '&tab=12'

    browser.get(url)
    sleep(5)
    
    # Click go to website
    redirect = browser.find_element_by_id('GoDirectToMS')
    redirect.click()
    
    sleep(2)
    # Find the link to the desired document
    tables = browser.find_elements_by_tag_name('table')
    rows = tables[1].find_elements_by_tag_name('tr')
    
    # We go through the rows of the table until we find "Verslagen" the next row then contains the most recent document
    flag = False
    for row in rows:
        if flag:
            row_with_doc = row
            break
        cols = row.find_elements_by_tag_name('td')
        for col in cols:
            if col.text == 'Verslagen':
                flag = True
    # Take the link from that row
    document_link = row_with_doc.find_element_by_tag_name('a').get_attribute('href')
    browser.get(document_link)

    # Now we just find the link to the pdf on the document page, and download    
    sleep(2)
    pdf_url = browser.find_element_by_id('documentFrame').get_attribute("src")
    
    browser.get(pdf_url)
    
    print('Downloading...')
    
    # Make sure there is a directory to save to
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
    
    
    # Wait until download is finished, then move the file
    while not 'download.pdf' in os.listdir():
        pass
    
    
    save_path = Path('./pdf_downloads')
    save_path /= (url_id + '.pdf')
    
    print('File downloaded. Saving it to ' + str(save_path))
    
    # If the file is already there, just delete the downloaded file instead
    try:
        os.rename('download.pdf', save_path)
    except FileExistsError:
        print('File already exists - download aborted.')
        os.remove('download.pdf')
    



if __name__ == '__main__':
    url_id = 'F00000YJ90'
    find_download_pdf(url_id)



