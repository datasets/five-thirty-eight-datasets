import json
import os
from urllib.request import urlopen

from bs4 import BeautifulSoup
from datapackage import Package

from generate_links import generate_links

raw_data_url = 'https://raw.githubusercontent.com/fivethirtyeight/data/master/'


def init(file='generated_links.txt'):
    generate_links()
    with open(file, "r") as links:
        for i, link in enumerate(links.readlines()):
            print(str(i) + ': ' + str(link))
            generate_dataset(link)


def generate_dataset(url):
    url = url.strip()
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    title = url[len('https://github.com/fivethirtyeight/data/tree/master/'):]
    directory = "datasets/" + title
    csv_found = False
    for link in soup.find_all('a'):
        content = link.string
        href = link.get('href')
        if content and '.csv' in content and href and '.csv' in href:
            csv_found = True
            csv_url = raw_data_url + title + '/' + content
            csv_name = content
            if 'https://' in content:
                csv_url = content
                csv_name = content[content.rindex('/') + 1:]
            if not os.path.exists(directory + "/data/"):
                os.makedirs(directory + "/data/")
            with open(directory + "/data/" + csv_name, "w", encoding='utf-8') as output_file:
                for line in urlopen(csv_url):
                    decoded_line = line.decode('ascii', 'ignore')
                    decoded_line = decoded_line.strip().lower()
                    decoded_line = decoded_line.replace('"', '')
                    output_file.write(decoded_line + '\n')
                    print(decoded_line)

            output_file.close()

    if not csv_found:
        return

    datapackage_creator(location="datasets/" + title,
                        title=title.title().replace('-', ' '),
                        name=title,
                        source_title='FiveThirtyEight - ' + title.title().replace('-', ' '),
                        source_path=url)

    readme_name = ''
    for link in soup.find_all('a'):
        content = link.string
        href = link.get('href')
        if content and 'readme.md' in content.lower() and href and 'readme.md' in href.lower():
            readme_name = content

    readme_url = raw_data_url + title + '/' + readme_name
    print(readme_url)
    with open(directory + '/README.md', "w", encoding='utf-8') as output_file:
        for line in urlopen(readme_url):
            decoded_line = line.decode('utf-8', 'ignore')
            decoded_line = decoded_line.strip()
            decoded_line = decoded_line.replace('"', '')
            output_file.write(decoded_line + '\n')
            print(decoded_line)

        output_file.write("\nThis dataset was scraped from [FiveThirtyEight - " + title + '](' + url + ')')


def datapackage_creator(location, title, name, source_title, source_path):
    package = Package()

    package.descriptor['title'] = title
    package.descriptor['name'] = name

    package.descriptor['sources'] = [{}]
    package.descriptor['sources'][0]['title'] = source_title
    package.descriptor['sources'][0]['path'] = source_path

    package.descriptor['licences'] = [{}]
    package.descriptor['licences'][0]['name'] = 'odc-pddl'
    package.descriptor['licences'][0]['title'] = 'Open Data Commons Public Domain Dedication and Licence (PDDL)'
    package.descriptor['licences'][0]['path'] = 'http://opendatacommons.org/licenses/pddl/'

    package.commit()
    package.infer(location + '/data/*.csv')
    package_json = package.descriptor
    del package_json['profile']

    with open(location + '/datapackage.json', 'w') as data_file:
        json.dump(package_json, data_file, indent=4, sort_keys=True)


init()
