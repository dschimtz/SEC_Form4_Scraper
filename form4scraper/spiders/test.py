# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 17:14:56 2020

@author: User
"""
import csv

with open(r'C:\Users\User\Desktop\ScrapyScraper\form4scraper\Universe.csv', 'r') as f:
    reader = csv.reader(f)
    urls = list(reader)
    
ciks = [row[1] for row in urls]

print(ciks[1:5])