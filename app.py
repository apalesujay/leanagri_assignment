'''

# Website to scrape: http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases 
#
# Data format: Excel 
#
# Fields: Disease name - Image link - Origin - See if you can identify the pest - Check what can legally come into Australia - Secure any suspect specimens 
#
# Output data: 
# - Submit the extracted Excel data 
# - Submit your code 
#
# Bonus points: 
# - Download the images programmatically and link them in the Excel sheet locally. 
# - Host the data back as a web page using the data from excel.

'''

import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import os, sys


def get_parsed_content(url):
    '''
    Takes url as an argument and returns parsed content
    '''
    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    return soup

def startScrape(url):
    '''
    Scrapes data from the response obtained after requesting the given url 
    '''
    disease_name = []
    image_links = []
    origin = []
    see_if_you_can_identify_the_pest = []
    check_what_can_legally_come_into_australia = []
    suspect_specimens = []
    images = []
        
    # Gets parsed content obtained from given url and fetches all the links of diseases from it
    soup = get_parsed_content(url)
    scrape = Scrape(soup)
    links = scrape.links()

    # Fetches required fields from each link
    for link in links:

        print('\nFetching from: {}'.format(link))

        soup = get_parsed_content(link)
        scrape = Scrape(soup)

        if scrape.disease_name() != 'no data':

            disease_name.append(scrape.disease_name())
            origin.append(scrape.origin())
            image = scrape.image()
            images.append(image[0])
            image_links.append(image[1])          
            suspect_specimens.append(scrape.suspect_specimens())
            check_what_can_legally_come_into_australia.append(scrape.check_what_can_legally_come_into_australia())
            see_if_you_can_identify_the_pest.append(scrape.see_if_you_can_identify_the_pest())


    # Writes data to Excel file & creates HTML file to host data 
    write = Write(disease_name, image_links, origin, see_if_you_can_identify_the_pest, check_what_can_legally_come_into_australia, suspect_specimens, images)
    write.to_excel()
    write.to_html()

class Write(object):
    '''
    Writes the data to Excel file and creates HTML file for each disease
    '''
    def __init__(self, disease_name, image_links, origin, see_if_you_can_identify_the_pest, check_what_can_legally_come_into_australia, suspect_specimens, images):
        self.disease_name =  disease_name
        self.images = images
        self.origin = origin
        self.see_if_you_can_identify_the_pest = see_if_you_can_identify_the_pest
        self.check_what_can_legally_come_into_australia = check_what_can_legally_come_into_australia
        self.suspect_specimens = suspect_specimens
        self.image_links = image_links

    # Writes data to Excel file using DataFrame from pandas
    def to_excel(self):
        df = pd.DataFrame()
        df['disease_name'] = self.disease_name
        df['origin'] = self.origin
        df['image_links'] = self.image_links
        df['images'] = self.images
        df['see_if_you_can_identify_the_pest'] = self.see_if_you_can_identify_the_pest
        df['check_what_can_legally_come_into_australia'] = self.check_what_can_legally_come_into_australia
        df['suspect_specimens'] = self.suspect_specimens
        writer = pd.ExcelWriter('leancrop.xlsx')
        df.to_excel(writer,'Sheet1')
        writer.save()

    # Reads data from Excel file and creates HTML file for a given disease
    def to_html(self):
        df = pd.read_excel('leancrop.xlsx')

        for i in range(len(df.index)):

            f = open(df['image_links'][i].split('/')[-1].split('.jpg')[0]+'.html','w+')

            html = """
            <html>
            <head></head>
            <body>
            
            <h1>"""+df['disease_name'][i]+"""</h1>
            
            <img src="""+df['image_links'][i]+""">
            </br></br>
            <strong>origin:</strong>"""+df['origin'][i]+"""
            </br></br>
            <strong>see if you can identify the pest</strong>
            <p>"""+df['see_if_you_can_identify_the_pest'][i]+"""</p>
            </br></br>
            <strong>Check what can legally come into australia</strong>
            <p>"""+df['check_what_can_legally_come_into_australia'][i]+"""</p>
             </br></br>
            <strong>secure any suspect specimens</strong>
            <p>"""+df['suspect_specimens'][i]+"""</p>
            </body>
            </html>
            """

            f.write(html)
            f.close()

class Scrape(object):
    '''
    Scrapes(fetches) required fields from the parsed content
    '''
    def __init__(self, soup):
        self.soup = soup

    # Scrapes all the required links and returns
    def links(self):
        base_url = "http://www.agriculture.gov.au"
        anchor_tags = self.soup.find('ul', class_="flex-container").find_all('a')
        links = [base_url+anchor_tag['href'] for anchor_tag in anchor_tags if anchor_tag['href'].startswith('/')]
        return links

    # Scrapes each required disease name and returns
    def disease_name(self):
        try:
            disease_name = self.soup.find('div', class_="pest-header-content").find('h2').text
        except:
            try:
                disease_name = self.soup.find('div', class_="page-content full-width").find('h1').text
            except:
                disease_name = 'no data'

        return disease_name

    # Scrapes all the required images and returns
    def image(self):
        base_url = "http://www.agriculture.gov.au"
        try:
            image_url=  base_url + self.soup.find('div', class_="pest-header-image").find('img')['src']
            urllib.request.urlretrieve(image_url, image_url.split('/')[-1])
        except:
            image_url = '/no image'

        return os.getcwd()+'/'+image_url.split('/')[-1],image_url

    # Scrapes every required origin and returns
    def origin(self):
        try:
            origin = [strong.next_sibling for strong in self.soup.find('div', class_="pest-header-content").find_all('strong') if 'Origin' in strong.text]
        except:
            origin = ['']
        return origin[0]
 
    def see_if_you_can_identify_the_pest(self):
        try:
            ptags = self.soup.find_all('h3',class_="trigger")[0].find_next('div', class_="hide").find_all('p')
            paragraph = ''
            for p in ptags:
                paragraph +=p.text.strip().replace('\r\n','')
            print(paragraph)
        except:
            paragraph = 'no data'
        return paragraph

    def check_what_can_legally_come_into_australia(self):
        try:
            ptags = self.soup.find_all('h3',class_="trigger")[1].find_next('div', class_="hide").find_all('p')
            paragraph = ''
            for p in ptags:
                paragraph +=p.text.strip().replace('\r\n','')
            print(paragraph)
        except:
            paragraph = 'no data'
        return paragraph

    # Scrapes suspect specimens and returns
    def suspect_specimens(self):
        try:
            ptags = self.soup.find_all('h3',class_="trigger")[2].find_next('div', class_="hide").find_all('p')
            paragraph = ''
            for p in ptags:
                paragraph +=p.text.strip().replace('\r\n','')
            print(paragraph)
        except:
            paragraph = ''
        return paragraph

# Driver code
if __name__ == '__main__':
    
    # URL to be scrapped
    url= "http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases"
    
    # Driver function
    startScrape(url)
