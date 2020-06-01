'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
import requests
from pathlib import Path
import os
from selenium import webdriver
from time import sleep
from web_scraper import WebScraper
  
     
def find_download_pdf(fund_ids):
    '''
    Locate and download the most recent report for a fund.

    Parameters
    ----------
    fund_id : list
        The ids for the relevant funds.

    Returns
    -------
    ISIN : int

    '''
    
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver')
    for fund_id in fund_ids:
        try:    
            fund_id = str(fund_id)
        except:
            raise Exception('fund_id should be a string or integer')
        
    ISINs = {}
    for fund_id in fund_ids:
        ISIN = scraper.get_ISIN(fund_id)
        
        
        # Make sure there is a directory to save to
        if not os.path.exists('./pdf_downloads'):
            os.mkdir('./pdf_downloads')
        
        scraper.download_pdf(fund_id, './pdf_downloads/' + fund_id + '.pdf')
        ISINs.update({fund_id : ISIN})
    
    return ISINs


if __name__ == '__main__':
    fund_ids = ['F00000YJ90', 'F000011JP3']
    ISINs = find_download_pdf(fund_ids)




