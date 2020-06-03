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
        
    def _log_in(self):
        '''
        Gets called if the browser finds itself at a screen where it needs to click on a link to go on to the website (usually the first get request). 
        '''
        # # Click go to website
        # sleep(2)
        WebDriverWait(self.browser, self.wait_time).until(
          expected_conditions.presence_of_element_located(
            (By.ID, 'GoDirectToMS'),
          )
        )

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
            

    def get_fund_list(self):
        '''
        Gets the list of funds from https://towardssustainability.be/en/Investment-Product
        This could be used for a different set of funds, but the find requests would need to be tweaked

        Returns
        -------
        fund_list : list
            A list of funds which can be searched on the morningstar website

        '''
        url = 'https://towardssustainability.be/en/Investment-Product'
        self.browser.get(url)
        fund_items = self.browser.find_elements_by_class_name('views-field-title')
        fund_hyperrefs = []
        for fund_item in fund_items:
            try:
                fund_hyperrefs.append(fund_item.find_element_by_tag_name('a'))
            except:
                pass
        fund_list = [hyperref.text for hyperref in fund_hyperrefs]
        return fund_list
    
    
    def get_fund_id_ISIN(self, search_string):
        '''
        Searches morningstar to find the fund id for a string. If there are multiple search result, picks the top one and reports the choice. Returns none if there are no results.

        Parameters
        ----------
        search_string : str
            The string used to query the fund.
        # require_permission : boolean
        #     If True, will ask for permission before picking a fund.

        Returns
        -------
        fund_id : int
            The unique fund_id used to identify the fund on the website.
        ISIN : str
            The ISIN for the fund
            
        '''
        
        # Format the search query into a url
        print('Getting fund id for ' + search_string)
        search_url = search_string.replace(' ', '%20')
        url = 'https://www.morningstar.be/be/funds/SecuritySearchResults.aspx?search=' + search_url + '&type='
        self._get(url)
        WebDriverWait(self.browser, self.wait_time).until(
          expected_conditions.presence_of_element_located(
            (By.ID, 'ctl00_MainContent_Label2'),
          )
        )

        # Get all search results
        results = self.browser.find_elements_by_class_name('searchLink')
        # Pick the top result
        if len(results) == 0:
            print('No search results found for "' + search_string + '"')
            return None, None
            # print('No results for "' + search_string + '". Trying search again with word omissions.')
            # results = self._retry_search(search_string)
            # if results is None:
            #     print('Still no results found. Moving onto next fund.')
            #     return None
        
        chosen_result = results[0]
        ISIN = self.browser.find_element_by_class_name('searchIsin').find_element_by_tag_name('span').text
        hyperref = chosen_result.find_element_by_tag_name('a')
        n_results = len(results)
        if n_results > 1:
            print('Search found ' + str(n_results) + ' results. Picked ' + hyperref.text)
        href_link = hyperref.get_attribute('href')
        # Find the id in the hyperref
        index = href_link.index('id=')
        return href_link[index + 3 :], ISIN
            
    
    def _retry_search(self, search_string):
        '''
        An attempt to find funds where the name is slightly different on the website than listed elsewhere.
        We drop one word at a time from the search string, and see if any search results come up. 
        If results come up for multiple searches, we take the top result for the search string that yields the fewest results.

        Parameters
        ----------
        search_string : str
            The (unsuccessful) search string

        Returns
        -------
        fund_id : int
            None if no fund is found.

        '''
        split_string = search_string.split(' ')
        search_results = {}
        for word in split_string:
            search_url = '%20'.join([w for w in split_string if not w == word])
            url = 'https://www.morningstar.be/be/funds/SecuritySearchResults.aspx?search=' + search_url + '&type='
            self._get(url)
            
            WebDriverWait(self.browser, self.wait_time).until(
              expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'searchLink'),
              )
            )
            # Get all search results
            results = self.browser.find_elements_by_class_name('searchLink')
            if len(results) > 0:
                search_results.update({word : results})
            
        if len(search_results) == 0:
            return None
        
        else:
            least_results = [v for k, v in sorted(search_results.items(), key=lambda item: len(item))][0]
            return least_results
        

    def download_pdf(self, fund_id, save_path = None):
        '''
        Download the latest report PDF.

        Parameters
        ----------
        fund_id : int
        save_path : str, optional
            If not specified, the file will be left saved as 'download.pdf'. The default is None.
            
        Returns
        -------
        success : boolean
            True if the pdf is found
        '''
        print('Navigating to the PDF')
        url = 'https://www.morningstar.be/be/funds/snapshot/snapshot.aspx?id=' + fund_id + '&tab=12'
    
        self._get(url)

        WebDriverWait(self.browser, self.wait_time).until(
          expected_conditions.presence_of_element_located(
            (By.TAG_NAME, 'table'),
          )
        )

        # Find the link to the desired document
        tables = self.browser.find_elements_by_tag_name('table')
        rows = tables[1].find_elements_by_tag_name('tr')
        
        # We go through the rows of the table until we find "Verslagen" the next row then contains the most recent document
        flag = False
        row_with_doc = None
        for row in rows:
            if flag:
                row_with_doc = row
                break
            cols = row.find_elements_by_tag_name('td')
            for col in cols:
                if col.text == 'Verslagen':
                    flag = True
                    
        if row_with_doc is None:
            print('No reports available to download for this fund')
            return False
        
        # Take the link from that row
        document_link = row_with_doc.find_element_by_tag_name('a').get_attribute('href')
        self._get(document_link)
    
        # Now we just find the link to the pdf on the document page, and download. We might need to try this a few times while the page loads
        wait_time = 0.5
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
        return True
        
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

    def rename_downloads_if_done(self):
        '''
        Rename the downloaded files if they are done downloading
        Returns
        -------
        renamed - list:
            A list containing the downloaded files which were renamed
        '''
        renamed = []
        to_pop = []
        # If the file is already there, just delete the downloaded file instead
        for download_path, save_path in self.download_renames.items():
            if os.path.exists(download_path):
                print(f'Renaming {download_path} to {save_path}')
                renamed.append(self.download_renames[download_path])
                to_pop.append(download_path)
                try:
                    os.rename(download_path, save_path)
                except FileExistsError:
                    os.remove(download_path)
        for key in to_pop:
            self.download_renames.pop(key)
        return renamed
            
    def kill(self):
        '''
        Close the browser
        '''
        self.browser.quit()
            
