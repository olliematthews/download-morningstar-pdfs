'''
Will find a kbc fund
'''
from pathlib import Path
import os
from web_scraper import WebScraper
from numpy import genfromtxt
import csv
import pickle

def write_ISIN(csv_file, fund, download_pdf, ISIN):
    '''
    Write a row to the ISIN file

    Parameters
    ----------
    csv_file : str
    fund : str
    ISIN : str

    Returns
    -------
    None.

    '''
    with open(csv_file, 'a', newline = '') as file:
        writer = csv.writer(file)
        print(fund)
        writer.writerow([fund, download_pdf, ISIN])
    
def get_ISIN_download_pdf(funds, csv_file = 'ISINs.csv', headless = False):
    '''
    Locate and download the most recent report for a fund, also save ISIN numbers.

    Parameters
    ----------
    funds : list
        The funds to be found.
    csv_file : str
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
        downloaded_files = scraper.rename_downloads_if_done()
        # Add any renamed files to the ISIN doc
        if len(downloaded_files) > 0:
            for fund_name in downloaded_files:
                temp_fund_name = fund_name.replace(' ','_')
                download_pdf, ISIN = ISINs.pop(temp_fund_name)
                write_ISIN(csv_file, fund_name, download_pdf, ISIN)
                
        
        print('\n\n')
        completion = round(i/n_funds * 100, 1)
        print(f'Fund {i} of {n_funds} - {completion}% complete')

        # Get the fund id
        ISIN, download_pdf = scraper.find_fund(fund, './pdf_downloads/' + nospace_fund + '.pdf')
        if ISIN is None:
            # If you can't find the fund, write not found in the ISIN doc
            write_ISIN(csv_file, fund, 'Not Found', 'Not Found')
        elif download_pdf is None:
            # Write the fund ISIN into the csv straight away if there is no pdf. Otherwise, wait until the
            # pdf is found.
            write_ISIN(csv_file, fund, 'Not Found', ISIN)
        else:
            # If you are waiting for the pdf to download, store the ISIN temporarily
            ISINs.update({nospace_fund : [download_pdf, ISIN]})
        

    scraper.rename_downloads()
    scraper.kill()

if __name__ == '__main__':
    headless = False
    csv_file = 'info_file.csv'
    funds = []
    with open('kbc_funds.txt', 'r') as file:
        for line in file:
            funds.append(line.strip('\n'))

    # Create download folder
    if not os.path.exists('./pdf_downloads'):
        os.mkdir('./pdf_downloads')
    # Remove any uncompleted downloads
    [os.remove('./pdf_downloads/' + file) for file in os.listdir('./pdf_downloads') if file.endswith('.crdownload')]
        
    # If the csvfile does not exist, fill in headers
    if not os.path.exists(csv_file):
        with open(csv_file, 'w') as file:
            file.write('Fund,PDF Name,ISIN\n')
        uncompleted_funds = funds
    else:
        entries = genfromtxt(csv_file, delimiter=',', dtype = str, skip_header = 1)
    
        completed_funds = list(entries[:,0]) if entries.shape[0] > 0 else []
        # Make sure you do not run the process more than once for the same fund_id
        uncompleted_funds = [f for f in funds if not f in completed_funds]
    
    
    get_ISIN_download_pdf(uncompleted_funds, csv_file, headless = headless)
    
            