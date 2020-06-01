# -*- coding: utf-8 -*-
"""
Contains WebScraper, a class for getting the ISIN number and downloading the latest annual report PDF of a fund from Morningstar
"""

import requests
from pathlib import Path
import os
from selenium import webdriver
from time import sleep


class WebScraper:
    def __init__()