'''
Function which can take a link to a fund on the Morningstar website, and download the most recent Report.
'''
from pathlib import Path
import os
from web_scraper import WebScraper
from numpy import genfromtxt

     
def get_ISIN_download_pdf(fund_ids):
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
    
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', False)
    for fund_id in fund_ids:
        try:    
            fund_id = str(fund_id)
        except:
            raise Exception('fund_id should be a string or integer')
        
    ISINs = {}
    for fund_id in fund_ids:
        ISIN = scraper.get_ISIN(fund_id)
        scraper.download_pdf(fund_id, './pdf_downloads/' + fund_id + '.pdf')
        ISINs.update({fund_id : ISIN})

    # Make sure there is a directory to save to
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
    scraper.rename_downloads()
    scraper.kill()
    return ISINs


if __name__ == '__main__':
    
    csv_file = 'ISINs.csv'
    fund_ids = ['F00000YJ90', 'F000011JP3']

    # If the csvfile does not exist, fill in headers
    if not os.path.exists(csv_file):
        with open('ISINs.csv', 'w') as file:
            file.write('Fund IDs, ISINs \n')
        uncompleted_fund_ids = fund_ids
    

    entries = genfromtxt(csv_file, delimiter=',', dtype = str, skip_header = 1)

    completed_fund_ids = list(entries[:,0]) if entries.shape[0] > 0 else []

    # Make sure you do not run the process more than once for the same fund_id
    uncompleted_fund_ids = [f_id for f_id in fund_ids if not f_id in completed_fund_ids]

    ISINs = get_ISIN_download_pdf(uncompleted_fund_ids)
    
            
    # Write the ISINs to a csv
    with open('ISINs.csv', 'a') as file:
        for fund_id, ISIN in ISINs.items():
            file.write(fund_id + ',' + ISIN + '\n')