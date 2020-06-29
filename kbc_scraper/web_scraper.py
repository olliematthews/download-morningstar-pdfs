# -*- coding: utf-8 -*-
"""
Contains WebScraper, a class for getting the ISIN number and downloading the latest annual report PDF of a fund from Morningstar
"""

import os
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


class WebScraper:
    def __init__(self, driver_path, headless = True, wait_time = 5):
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
        self.wait_time = wait_time
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
        
        # Go to search page
        self.browser.get('https://www.kbc.be/corporate/en/product/investments/fund-finder.html')
        
        # Switch to frame
        self.frame = self.browser.find_element_by_tag_name('iframe')
        self.browser.switch_to.frame(self.frame)
            
        
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

            
    def find_fund(self, fund, save_path = None):
        '''
        Find the fund, get its isin and download the pdf

        Parameters
        ----------
        fund : str
        save_path : str, optional
            If not specified, the file will be left saved as 'download.pdf'. The default is None.
            
        Returns
        -------
        ISIN : int
        '''
        search_field = self.browser.find_element_by_id('FinderIsin')
        search_field.send_keys(fund)
        search_button = self.browser.find_element_by_id('searchbutton')
        search_button.click()
        # TODO sort out explicit waits

        while(1):
            try:
                top_result = self.browser.find_element_by_xpath('//*[@id="fundFinderResultGrid"]/table/tbody/tr[1]')
                name = top_result.find_element_by_tag_name('td').text.split('\n')[0]
                continue_flag = False
                for word in fund.split(' '):
                    if not word in name:
                        continue_flag = True
                if continue_flag:
                    continue
                ISIN = top_result.get_attribute('isin')
                top_result.click()
                break
            except:
                pass
            
        # Wait for page to load
        while(1):
            title = self.browser.find_elements_by_class_name('h2')
            if len(title) > 0:
                title_text = title[0].find_element_by_tag_name('span').text
                if all([word in title_text for word in fund.split(' ')]):
                    sleep(1)
                    break
            
            
        annual_reports =  self.browser.find_elements_by_xpath('//*[contains(text(), "Annual report")]')
        if len(annual_reports) == 0:
            print('No annual reports found')
            return ISIN
        else:
            print('Downloading...')
            annual_reports[0].click()   
            print('clicked')
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
            return ISIN
        
        
    def kill(self):
        '''
        Close the browser
        '''
        self.browser.quit()
            
