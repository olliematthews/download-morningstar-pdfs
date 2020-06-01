# -*- coding: utf-8 -*-
"""
Contains WebScraper, a class for getting the ISIN number and downloading the latest annual report PDF of a fund from Morningstar
"""

import os
from selenium import webdriver
from time import sleep


class WebScraper:
    def __init__(self, driver_path, headless = True):
        '''
        Initialiser

        Parameters
        ----------
        driver_path : str
            The path to the driver for the chromedriver binaries e.g. C:/.../chromedriver

        headless : boolean, optional
            If False, the browser is not run in headless mode. The default is True.

        Returns
        -------
        None.

        '''
        self.driver_path = driver_path

        # We first download the file to the current working directory, then move it
        download_dir = str(os.path.realpath(os.getcwd()))
        
        # Update browser options. This ensures that the pdf is downloaded instead of being viewed in chrome
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs',  {
            "download.default_directory": download_dir,
            "plugins.always_open_pdf_externally" : True
            }
        )
        
        
        if headless:
        
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
        
        
        # Initialise a webdriver with the options set
        self.browser = webdriver.Chrome(str(driver_path), options = options)
        
        # Keep track of what the pdfs are downloaded as so that you can rename them after
        self.download_renames = {}
        
    def _log_in(self):
        '''
        Gets called if the browser finds itself at a screen where it needs to click on a link to go on to the website (usually the first get request). 
        '''
        # # Click go to website
        # sleep(2)
        redirect = self.browser.find_element_by_id('GoDirectToMS')
        redirect.click()
        
        # # Wait a second to load the next page
        # sleep(1)

    def _get(self, url):
        '''
        Runs a get request for a url, with some checks to ensure it works properly.
        '''

        self.browser.get(url)
        

        # If a 404 error occurs, try waiting and reloading the page, a maximum of 3 times
        wait_time = 0
        n_attempts = 1
        while self.browser.title == 'Morningstar message':
            sleep(wait_time)
            self.browser.get(url)
            wait_time += 1
            if n_attempts >= 3:
                raise  Exception('404 error')
                
        # If you are met by an intro page, call _log_in
        if self.browser.current_url.startswith('https://www.morningstar.be/IntroPage'):
            self._log_in()
            
        self.browser.implicitly_wait(10) # seconds

                
    def get_ISIN(self, fund_id):
        '''
        Get the ISIN for the fund.
    
        Parameters
        ----------
        fund_id : str
            The id for the relevant fund, found after "id=" in the url.
        
        Returns
        -------
        ISIN : int
        '''
        print('Getting ISIN')

        url = 'https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=' + fund_id
        self._get(url)
        
        # Find the table with the ISIN (note we )
        div = self.browser.find_element_by_id('overviewQuickstatsDiv')
        table = div.find_element_by_tag_name('table')
        
        # Find the row with the ISIN
        rows = table.find_elements_by_tag_name('tr')
        for row in rows:
            cols = row.find_elements_by_tag_name('td')
            for col in cols:
                if col.text == 'ISIN':
                    row_with_ISIN = row
        # Return the ISIN
        ISIN = row_with_ISIN.find_element_by_class_name('text').text
        print('ISIN is ' + str(ISIN))

        return ISIN

    def download_pdf(self, fund_id, save_path = None):
        '''
        Download the latest report PDF.

        Parameters
        ----------
        fund_id : int
        save_path : str, optional
            If not specified, the file will be left saved as 'download.pdf'. The default is None.

        '''
        print('Navigating to the PDF')
        url = 'https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=' + fund_id + '&tab=12'
    
        self._get(url)
        
        # Find the link to the desired document
        tables = self.browser.find_elements_by_tag_name('table')
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
        self._get(document_link)
    
        # Now we just find the link to the pdf on the document page, and download. We might need to try this a few times while the page loads
        wait_time = 1
        n_attempts = 1
        while n_attempts < 3:
            try:
                pdf_url = self.browser.find_element_by_id('documentFrame').get_attribute("src")
                break
            except:
                sleep(wait_time)
                        
        self.browser.get(pdf_url)
        print('Downloading...')
        
        download_name = []
        # Wait until download comes up in your directory
        while(len(download_name) == 0):
            # Find the name the file is being downloaded as
            downloading_names = [filename for filename in os.listdir() if filename.endswith('crdownload')]
            download_name = [filename for filename in downloading_names if not filename in self.download_renames.keys()]
            sleep(0.5)
        download_name = download_name[0].replace('.crdownload','')
        
        if not save_path is None:
            self.download_renames.update({download_name : save_path})
        
    def rename_downloads(self):
        '''
        Rename the downloaded file. If it is already there, then just delete the download.
        '''
        print('Waiting for all downloads to finish')
        flag = False
        while not flag:
            flag = True
            os_files = os.listdir()
            # Check that all the download files are in the current directory
            for filename in self.download_renames.keys():
                flag = flag and filename in os_files
                
            sleep(1)
        
        print('Renaming the download files')
        # If the file is already there, just delete the downloaded file instead
        for download_path, save_path in self.download_renames.items():
            try:
                os.rename(download_path, save_path)
            except FileExistsError:
                os.remove(download_path)
            
            
    def kill(self):
        '''
        Close the browser
        '''
        self.browser.quit()
            
