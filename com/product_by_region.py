from lxml import html, etree
from bs4 import BeautifulSoup
import requests
import pprint
import json
import logging
from datetime import datetime
import re

# Constants
AZGOV_PRODS_BY_REGION = "https://service.prerender.io/https://azure.microsoft.com/en-us/global-infrastructure/services/?products=all&regions=usgov-non-regional,us-dod-central,us-dod-east,usgov-arizona,usgov-texas,usgov-virginia"

# Helpers

## Gets text from an HTML element
def text(elt):
    return elt.text_content().replace(u'\xa0', u' ').replace('✔️', "Check")

#✔️
def replace_images(str):
    return str.replace(
        '<img src="//azurecomcdn.azureedge.net/cvt-94bb7ea5624702377c0fe0b7ed7771726181533628678b7df021a4dd7d2d400d/images/page/global-infrastructure/services/ga.svg" alt="" role="presentation">', "GA").replace('<img src="//azurecomcdn.azureedge.net/cvt-94bb7ea5624702377c0fe0b7ed7771726181533628678b7df021a4dd7d2d400d/images/page/global-infrastructure/services/preview-active.svg" alt="" role="presentation">', "Preview-Active").replace('<img src="//azurecomcdn.azureedge.net/cvt-94bb7ea5624702377c0fe0b7ed7771726181533628678b7df021a4dd7d2d400d/images/page/global-infrastructure/services/preview.svg" alt="" role="presentation">', 
        "Preview")

class AzGovProductAvailabilty:
    def __init__(self):
        self.__created = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        self.__soup = BeautifulSoup()
        self.__azureGovermentProductAvailablity = {}       
        self.__servicesList = []
        self.__capabilitiesList = []
        self.__services = {}
        self.__capabilities = {}

    def __getFromWeb(self):
        page = requests.get(AZGOV_PRODS_BY_REGION)
        soup = BeautifulSoup(page.content, features='lxml')
        return soup
    
    def __getFromLocal(self):
        with open("render.html") as f:
            # content = f.readlines()
            render = html.document_fromstring(f.read())
            render = html.tostring(render)
                            
        soup = BeautifulSoup(render, features='lxml')
        return soup


    def __replaceSoupImage (self, img_file_name, text):
        imgs = self.__soup.find_all(name="img", attrs={
            "src": re.compile(img_file_name)
            }, recursive=True)

        for img in imgs:
            img.name = "p"
            del img['src']
            del img['role']
            del img['alt']
            if (text.__contains__("-active")):               
                img['ga-expected'] = img.parent.get_text(" ", strip=True).replace("GA expected ","")
    
            img.string=text

        return self.__soup

    def __removeToolTipContentFromSoup (self):
        tooltips = self.__soup.find_all("span",attrs={"class":"table-tooltip"}) + self.__soup.find_all("span",attrs={"class":"tooltip-content"}) + self.__soup.find_all("span",attrs={"class":"hide-text"})
        for tiptag in tooltips:
            tiptag.decompose()

        return self.__soup
    
    def __hydrateServiceAndCapabilityJsons(self):
        rows = self.__soup.find_all('tr')

        service_json = {}
        capability_json = {}

        lastCategory = ""
        lastService = ""
        for row in rows[2:]:
            processedRow = self.__processRow(row)
            if (processedRow['type'] == "category-row"):              
                lastCategory = processedRow['id']
                
            elif (processedRow['type'] == "service-row"):
                id = processedRow['id']

                processedRow['capabilities'] = []

                if (id not in service_json):
                    service_json[id] = processedRow
                
                try:
                    service_json[id]['categories'].index (lastCategory)
                except:
                    service_json[id]['categories'].append (lastCategory)               
                    
                lastService = id

            else:
                id = processedRow['id']

                if (id not in capability_json):
                    capability_json[id] = processedRow
               
                capability_json[id]['service'] = lastService
                
                try:
                     capability_json[id]['categories'].index(lastCategory)
                except:
                    capability_json[id]['categories'].append (lastCategory)
                
        ## add capabilities to services

        for key in capability_json.keys():
            cap = capability_json[key]
            svc = cap['service']

            # store just the id for now.
            service_json[svc]['capabilities'].append (key)

        self.__services = service_json
        self.__capabilities = capability_json

        return

    def __processRow(self, row):

        cols = row.find_all(['th','td'])

        doc = {
            'id': cols[0].text.strip().replace(u'\u2013', u'-'),
            # 'as-of': self.__created,
            'type': row['class'][0],
            'available': False,
            'preview': [],
            'planned-active': [],
            'categories': []   
        }
        
        for col in cols:
            if (col.has_attr('data-region-slug')):
                if (col.text.strip().__contains__ ("check")):
                    doc[ col['data-region-slug'] ] = True
                    doc['available'] = True
                elif (col.text.strip().__contains__ ("preview")):                
                    region = {}
                    region['region'] = col['data-region-slug']

                    p = col.find('p', attrs={'class':'ga-expected'})
                    if p:
                        region['ga-expected'] = p['ga-expected']
                    
                    doc['preview'].append(region)                   

                elif (col.text.strip().__contains__ ("planned-active")):
                    region = {}
                    region['region'] = col['data-region-slug']
                    
                    p = col.find('p')
                    region['ga-expected'] = p['ga-expected']

                    doc['planned-active'].append(region)
                
                # else:
                #     doc[ col['data-region-slug'] ] = False

        
        #print (doc)

        return doc

    def initialize(self):
        
        self.__soup = self.__getFromLocal()
        self.__soup = self.__soup.find(attrs={"class":"primary-table"})
        
        self.__soup = self.__replaceSoupImage("preview-active.svg", "preview-active")
        self.__soup = self.__replaceSoupImage("planned-active.svg", "planned-active")
        self.__soup = self.__replaceSoupImage("preview.svg", "preview")
        self.__soup = self.__replaceSoupImage("ga.svg", "check")     
        self.__soup = self.__removeToolTipContentFromSoup()

        self.__hydrateServiceAndCapabilityJsons()

        self.printAzGovProductAvailabilty()
        
        return 



    ## *********************************************************************
    ## public print methods

    def dumpSoup(self):
        print (self.__soup)

    def printAzGovProductAvailabilty(self):
        print (json.dumps({
            'services': self.__services,
            'capabilities': self.__capabilities
        }))