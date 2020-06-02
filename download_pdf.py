'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
from pathlib import Path
import os
from web_scraper import WebScraper
from numpy import genfromtxt
import csv
import pickle

def get_ISIN_download_pdf(funds, headless = False):
    '''
    Locate and download the most recent report for a fund.

    Parameters
    ----------
    funds : list
        The funds to be found.

    Returns
    -------
    ISIN : int

    '''
    
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', headless)
        
    ISINs = {}
    for fund in funds:
        fund_id = scraper.get_fund_id(fund)
        if fund_id is None:
            ISINs.update({fund.replace(' ', '_') : 'Not Found'})
            continue
        ISIN = scraper.get_ISIN(fund_id)
        scraper.download_pdf(fund_id, './pdf_downloads/' + fund.replace(' ', '_') + '.pdf')
        ISINs.update({fund.replace(' ', '_') : ISIN})

    # Make sure there is a directory to save to
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
    scraper.rename_downloads()
    scraper.kill()
    return ISINs


if __name__ == '__main__':
    headless = False
    csv_file = 'ISINs.csv'

    # If this is the first time running, you need to get the fund names. If not you can load a save file.
    if os.path.exists('funds.p'):
        funds = pickle.load(open('funds.p','rb'))
    else:
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
    ISINs = get_ISIN_download_pdf(uncompleted_funds, headless)
    
            
    # Write the ISINs to a csv
    with open('ISINs.csv', 'a', newline = '') as file:
        writer = csv.writer(file)
        for fund_id, ISIN in ISINs.items():
            writer.writerow([fund_id, ISIN])