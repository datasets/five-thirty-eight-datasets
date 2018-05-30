from bs4 import BeautifulSoup
from urllib.request import urlopen

open('generated_links.txt', "w")

url = 'https://github.com/fivethirtyeight/data'

soup = BeautifulSoup(urlopen(url), 'html.parser')
with open('generated_links.txt', "a") as generated_links:
    for a in soup.find_all('a'):
        clazz = a.get('class')
        if a and clazz and 'js-navigation-open' in clazz:
            href = a.get('href')
            generated_links.write('https://github.com/' + href + '\n')
