'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
from pathlib import Path
import os
from web_scraper import WebScraper
from numpy import genfromtxt
import csv
import pickle

def get_ISIN_download_pdf(funds, ISIN_file = 'ISINs.csv', headless = False):
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
    
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', headless)
        
    ISINs = {}
    n_funds = len(funds)
    for i, fund in enumerate(funds):
        # Rename any downloaded pdfs as you go
        scraper.rename_downloads_if_done()
        
        print('\n\n')
        completion = round(i/n_funds * 100, 1)
        print(f'Fund {i} of {n_funds} - {completion}% complete')

        # Get the fund id
        fund_id = scraper.get_fund_id(fund)
        if fund_id is None:
            ISINs.update({fund.replace(' ', '_') : 'Not Found'})
            continue
        
        
        ISIN = scraper.get_ISIN(fund_id)
        scraper.download_pdf(fund_id, './pdf_downloads/' + fund.replace(' ', '_') + '.pdf')

        # Write the fund ISIN into the csv
        with open(csv_file, 'a', newline = '') as file:
            writer = csv.writer(file)
            writer.writerow([fund, ISIN])
        

    scraper.rename_downloads()
    scraper.kill()


if __name__ == '__main__':
    headless = False
    csv_file = 'ISINs.csv'
    
    # Create download folder
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
        
        
    # If this is the first time running, you need to get the fund names. If not you can load a save file.
    if os.path.exists('funds.p'):
        funds = pickle.load(open('funds.p','rb'))
    else:
        # Put your path to the chromedrive binaries here!!!
        scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', headless)
        funds = scraper.get_fund_list()
        scraper.kill()
        pickle.dump(funds, open('funds.p','wb'))
        
    # If the csvfile does not exist, fill in headers
    if not os.path.exists(csv_file):
        with open('ISINs.csv', 'w') as file:
            file.write('Funds,ISINs\n')
        uncompleted_funds = funds
    
    
    entries = genfromtxt(csv_file, delimiter=',', dtype = str, skip_header = 1)

    completed_funds = list(entries[:,0]) if entries.shape[0] > 0 else []

    # Make sure you do not run the process more than once for the same fund_id
    uncompleted_funds = [f for f in funds if not f in completed_funds]

    '''
    If you want to test run on only some funds, try putting e.g. "uncompleted_funds[:10]"
    '''
    get_ISIN_download_pdf(uncompleted_funds[10:20], headless)
    
            