#! /usr/bin/env python

from urllib.parse import urlencode
import httplib2

httplib2.debuglevel = 1
h = httplib2.Http('.cache')

url = 'http://sfc.bihar.gov.in/fpshopsSummaryDetails.htm'

data = {
    'mode':'searchFPShopDetails',
    'dyna(state_id)':'10',
    'dyna(fpsCode)':'',
    'dyna(scheme_code)':'',
    'dyna(year)':'2015',
    'dyna(month)':'12',
    'dyna(district_id)':'1001',
    'dyna(block_id)':'10010125',
    'dyna(fpshop_id)':'200000016602',
}

print(urlencode(data))
response, content = h.request(url, 'POST', urlencode(data), headers = {'Content-Type': 'application/x-www-form-urlencoded'})

with open('z.html', 'wb') as html_file:
    print('Writing z.html')
    html_file.write(content)
