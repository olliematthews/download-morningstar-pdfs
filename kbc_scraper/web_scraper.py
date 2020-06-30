# -*- coding: utf-8 -*-
"""
Contains WebScraper, a class for getting the ISIN number and downloading the latest annual report PDF of a fund from Morningstar
"""

import os
from selenium import webdriver
from time import sleep, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys

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
        download_dir = str(os.path.realpath('./pdf_downloads'))
        
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
        self.downloading = {}
                    
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
            for download_name, delete in self.downloading.values():
                flag = flag and filename in os_files
                
            sleep(1)
            
        for download_name, delete in self.downloading.values():
            if delete:
                os.remove('pdf_downloads/' + download_name)
        
            
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
        download_pdf : str
            Name of the pdf for the fund
        '''
        # First, we need to go to the search page and switch to the correct frame
        self.browser.get('https://www.kbc.be/corporate/en/product/investments/fund-finder.html')
        
        # Switch to frame
        self.frame = self.browser.find_element_by_tag_name('iframe')
        self.browser.switch_to.frame(self.frame)
        # WebDriverWait(self.browser, self.wait_time).until(
        #   expected_conditions.presence_of_element_located(
        #     (By.ID, 'searchbutton'),
        #   )
        # )
        WebDriverWait(self.browser, self.wait_time).until(
          expected_conditions.invisibility_of_element_located(
            (By.CLASS_NAME, 'k-loading-image'),
          )
        )
        
        # Make search
        search_field = self.browser.find_element_by_id('FinderIsin')
        search_field.clear()
        search_field.send_keys(fund)
        search_field.send_keys(Keys.RETURN)
        
        WebDriverWait(self.browser, self.wait_time).until(
          expected_conditions.invisibility_of_element_located(
            (By.CLASS_NAME, 'k-loading-image'),
          )
        )

        # search_button = self.browser.find_element_by_id('searchbutton')
        # search_button.click()
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
                    break
                
        annual_reports =  self.browser.find_elements_by_xpath('//*[contains(text(), "Annual report")]')
        if len(annual_reports) == 0:
            print('No annual reports found')
            return ISIN, None
        else:
            print('Downloading...')
            for i in range(3):
                annual_reports[0].click()   
    
                download_name = []
                # Wait until download comes up in your directory
                start_time = time()
                while(len(download_name) == 0):
                    # Find the name the file is being downloaded as
                    downloading_names = [filename for filename in os.listdir('./pdf_downloads') if filename.endswith('crdownload')]
                    download_name = [filename for filename in downloading_names if not filename in [v[0] for v in self.downloading.values()]]
                    if time() > start_time + 1:
                        break
                    
                if len(download_name) == 0:
                    continue
                else:
                    download_name = download_name[0].replace('.crdownload','')
                    break
            if i >= 3:
                raise Exception
            # Save the download name, with a boolean to indicate whether to 
            # delete it after or not (if it has already been downloaded)
            try:
                root_download_name_index = download_name.index('(')
                root_download_name = download_name[:root_download_name_index].replace(' ', '.pdf')
                delete = True

            except:
                delete = False
                root_download_name = download_name
                
                
            # Catch any failed downloads
            if download_name in [val[0] for val in self.downloading.values()]:
                lost_fund = [k for k, v in self.downloading.items() if v[0] == download_name][0]
                self.downloading.pop(lost_fund)
                print(f'Download of {fund} failed')
                
            self.downloading.update({fund: [download_name, delete]})

            return ISIN, root_download_name
        
    def rename_downloads_if_done(self):
        '''
        Rename the downloaded files if they are done downloading
        Returns
        -------
        renamed - list:
            A list containing the downloaded files which were renamed
        '''
        downloaded = []
        to_pop = []
        # If the file is already there, just delete the downloaded file instead
        for fund, (download_name, delete) in self.downloading.items():
            download_path = 'pdf_downloads/' + download_name
            if os.path.exists(download_path):
                downloaded.append(fund)
                to_pop.append(fund)
                if delete:
                    print('Deleting copy of PDF')
                    os.remove(download_path)

        for key in to_pop:
            self.downloading.pop(key)
        return downloaded

    def kill(self):
        '''
        Close the browser
        '''
        self.browser.quit()
            
