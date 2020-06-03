# Morningstar Webscraping

## Download the latest report PDFs and the ISIN Numbers for Funds from Morningstar

### Requirements

* Numpy
* selenium

Note that to use selenium, you need to have Google Chrome installed as well as the relevant chromedriver, which can be found at: https://chromedriver.chromium.org/downloads.

Before running the code, download the binaries for the chromedriver for your version of chrome, and set the path in the scripts to point to the binaries.

### Instructions

Run 'download_pdf.py'. The script will start a browser which finds the fund id, then the ISIN numbers for each fund listed on https://towardssustainability.be/en/Investment-Product, and then downloads the most recent report. It saves the reports as PDFs to <current directory>/ downloads, and writes a csv file with the ISIN numbers for each fund.

The browser output can be seen by changing headless to False.  


### Potential Improvements

The code could easily be made to run on multiple processes, as it is mostly parallel (some care would need to be taken in locking csv files when writing to them and locking when getting the download names). This would improve speed, if that is desired. 

The funds are often not found on the Morningstar website. This can happen even if the fund is there, as the name might be slightly different to that listed on the list of funds. For example, replacing 'wf' with 'world fund' can get higher results. A more robust way of checking this would be to search again for unfound funds, but with some of the fund name words omitted, to see if the fund can be found.


Another problem is funds not having any reports on the website. To deal with this, we will need to look to other sources.
