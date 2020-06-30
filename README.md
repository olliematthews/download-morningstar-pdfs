# Webscraping

## Download the latest report PDFs and the ISIN Numbers for Funds

### Requirements

* Numpy
* selenium

Note that to use selenium, you need to have Google Chrome installed as well as the relevant chromedriver, which can be found at: https://chromedriver.chromium.org/downloads.

Before running the code, download the binaries for the chromedriver for your version of chrome, and set the path in the scripts to point to the binaries.

### General Strategy for Writing a New Webscraper

The aim is a webscraper which can navigate a fund provider's website, locate the pdfs and ISINs for a number of funds, and then download those pdfs and save the ISINs. This can be done by using the search page of the fund provider to locate the funds, and then search for the downloads. The general idea is to:

* Make a get request for the search page
* Enter the fund you are looking for, and click on the top result if there are any results
* Navigate the fund summary to find the ISIN and pdf

Note that we configure the browser so that to download a pdf all we have to do is click on it.

#### To locate an element on a page

To get around the website, we locate the correct elements on the pages and click on them, as a human would do. To locate an element, we can look at the source code for the page we are interested in and find a unique identifier for the element we want to interact with. The identifier can be the type of element ('find_element_by_tag_name'), an id ('find_element_by_id'), a class etc.

See https://selenium-python.readthedocs.io/locating-elements.html for a full list of ways to find elemenets.


#### To interact with an element on a page

This can be done with in built functions like click() and send_keys().

#### Waits

See https://selenium-python.readthedocs.io/waits.html for a more complete explanation.

Selenium is not good at knowing when a page is loaded. It is important to put in waits to deal with this, so that the browser only tries to interact with elements when they are actually on the page. We can do this in a few ways:

* sleep() - This is a rudimentary approach, where we simply wait a certain amount of time after arriving on a page before we try to interact. Should be used sparingly as different users can experience different loading times due to e.g. internet speed.
* Explicit waits - These should be used as the primary form of waits. Here, we tell Selenium to wait for a specific event to occur on a page (with a timeout). The event could be the appearance of an element, for example, so can help the browser to wait for the correct amount of time.
* Implicit waits - These are useful in theory, but inefficient in practice. If we call an implicit wait before trying to take an action, the browser will continue to try to take the action until timeout if it fails. The problems with this approach are that the browser is prone to wait too long, and sometimes the desired action will not yield an error if it is taken on the page before it loads, producing dangerous side-effects. To be avoided on the whole.
