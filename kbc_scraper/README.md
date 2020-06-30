# KBC Webscraping

## Download the latest report PDFs and the ISIN Numbers for Funds from KBC

### Instructions

Run 'download_pdf.py'. The script will start a browser which finds the fund id, then the ISIN numbers for each fund listed on https://towardssustainability.be/en/Investment-Product, and then downloads the most recent report. It saves the reports as PDFs to <current directory>/ downloads, and writes a csv file with the ISIN numbers for each fund.

Note that many funds yield the same PDF so in this approach, we only save one of each pdf, and write a csv file in which we say which fund can be found in which PDF.

The browser output can be seen by changing headless to False.  
