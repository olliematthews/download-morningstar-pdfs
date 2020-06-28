'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
from pathlib import Path
import os
from web_scraper import WebScraper
from numpy import genfromtxt
import csv
import pickle

def write_ISIN(ISIN_file, fund, fund_id, ISIN):
    '''
    Write a row to the ISIN file

    Parameters
    ----------
    ISIN_file : str
    fund : str
    fund_id : str
    ISIN : str

    Returns
    -------
    None.

    '''
    with open(csv_file, 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow([fund, 'Not Found'])
    
def get_ISIN_download_pdf(fund, ISIN_file = 'ISINs.csv', headless = False):
    '''
    Locate and download the most recent report for a fund, also save ISIN numbers.

    Parameters
    ----------
    funds : list
        The funds to be found.
    ISIN_file : str
        The filename to which ISINs are written
    headless : boolean
        If True, browser is run headlessly

    '''
    
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', headless = headless)
        
    ISINs = {}
    nospace_fund = fund.replace(' ', '_')
            
    
    print('\n\n')

    # Get the fund id
    ISIN = scraper.find_fund(fund, nospace_fund + '.pdf')
    print(f'ISIN for {fund} is {ISIN}')
    scraper.rename_downloads()
        
    scraper.kill()


if __name__ == '__main__':
    headless = False
    csv_file = 'ISINs.csv'
    
    # Remove any uncompleted downloads
    [os.remove(file) for file in os.listdir() if file.endswith('.crdownload') or file.endswith('.pdf')]
    # Create download folder
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
        
        
    # Put your path to the chromedrive binaries here!!!
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', headless = headless)
    scraper.kill()
        
    # If the csvfile does not exist, fill in headers
    if not os.path.exists(csv_file):
        with open('ISINs.csv', 'w') as file:
            file.write('Funds,ISINs\n')
    
    fund = 'Horizon KBC ExpertEase SRI Dynamic'
    
    get_ISIN_download_pdf(fund, headless = headless)
    
            