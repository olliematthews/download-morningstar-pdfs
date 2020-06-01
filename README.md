# Morningstar Webscraping

## Download the latest report PDFs and the ISIN Numbers for Funds from Morningstar

### Requirements

* Numpy
* selenium

Note that to use selenium, you need to have Google Chrome installed as well as the relevant chromedriver, which can be found at: https://chromedriver.chromium.org/downloads.

Before running the code, download the binaries for the chromedriver for your version of chrome, and set the path in the scripts to point to the binaries.

### Instructions

Run 'download_pdf.py', with the list of fund ids you want to download. The script will start a browser which finds the ISIN numbers for each fund, and downloads the most recent report. It saves the reports as PDFs to <current directory>/ downloads, and writes a csv file with the ISIN numbers for each fund.

The browser can be suppressed by running selenium 'headlessly'. In practice, this is more buggy for the moment, so it is recommended not to do this. 
