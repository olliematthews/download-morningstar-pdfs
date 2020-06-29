'''
Will find a kbc fund
'''
from pathlib import Path
import os
from web_scraper import WebScraper
from numpy import genfromtxt
import csv
import pickle

def write_ISIN(ISIN_file, fund, ISIN):
    '''
    Write a row to the ISIN file

    Parameters
    ----------
    ISIN_file : str
    fund : str
    ISIN : str

    Returns
    -------
    None.

    '''
    with open(ISIN_file, 'a', newline = '') as file:
        writer = csv.writer(file)
        writer.writerow([fund, ISIN])
    
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
        
    scraper = WebScraper('C:/Users/Ollie/Downloads/chromedriver_win32/chromedriver', headless = headless)
        
    ISINs = {}
    n_funds = len(funds)
    for i, fund in enumerate(funds):
        print(fund)
        nospace_fund = fund.replace(' ', '_')
        # Rename any downloaded pdfs as you go
        renamed_files = scraper.rename_downloads_if_done()
        # Add any renamed files to the ISIN doc
        if len(renamed_files) > 0:
            for fund_path in renamed_files:
                temp_fund_name = fund_path.replace('./pdf_downloads/','').replace('.pdf','')
                ISIN = ISINs.pop(temp_fund_name)
                write_ISIN(ISIN_file, fund, ISIN)
                
        
        print('\n\n')
        completion = round(i/n_funds * 100, 1)
        print(f'Fund {i} of {n_funds} - {completion}% complete')

        # Get the fund id
        ISIN, success = scraper.find_fund(fund, './pdf_downloads/' + nospace_fund + '.pdf')
        if ISIN is None:
            # If you can't find the fund, write not found in the ISIN doc
            write_ISIN(ISIN_file, fund, 'Not Found')
        elif not success:
            # Write the fund ISIN into the csv straight away if there is no pdf. Otherwise, wait until the
            # pdf is found.
            write_ISIN(ISIN_file, fund, ISIN)
        else:
            # If you are waiting for the pdf to download, store the ISIN temporarily
            ISINs.update({nospace_fund : [ISIN]})
        

    scraper.rename_downloads()
    scraper.kill()

if __name__ == '__main__':
    headless = False
    csv_file = 'ISINs.csv'
    funds = []
    with open('kbc_funds.txt', 'r') as file:
        for line in file:
            funds.append(line.strip('\n'))

    # Remove any uncompleted downloads
    [os.remove(file) for file in os.listdir() if file.endswith('.crdownload') or file.endswith('.pdf')]
    # Create download folder
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
        
        
    # If the csvfile does not exist, fill in headers
    if not os.path.exists(csv_file):
        with open('ISINs.csv', 'w') as file:
            file.write('Funds,ISINs\n')
    
    
    get_ISIN_download_pdf(funds, headless = headless)
    
            