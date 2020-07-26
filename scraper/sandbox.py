from bs4 import BeautifulSoup
import re
html = open('./html/brandibble/1720a7fe22681dc9.html', 'r')
soup = BeautifulSoup(html, 'html.parser')
html.close()
print(soup.find_all('blockquote')[1].find('table', attrs={"class": "container"}).find_all('table')[1].find('tbody'))





'''
safe html for delivery.com === print(soup.find('table', attrs={"id": 'main-container'}))
safe html for toasttab.com === print(soup.find_all('blockquote')[1])
safe html for gloriafood === print(soup.find('td', attrs={"id": "templateBody"}))
safe html for brandibble === print(soup.find_all('blockquote')[1].find('table', attrs={"class": "container"}).find_all('table')[1].find('tbody'))
'''