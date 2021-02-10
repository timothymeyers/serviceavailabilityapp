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
        
        self.__azureGovermentProductAvailablity = {}
        self.__categoriesList = []
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


    def initializeWeb(self):
        page = requests.get(AZGOV_PRODS_BY_REGION)
        soup = BeautifulSoup(page.content)
        print (soup)


    def __replaceSoupImage (self, soup, img_file_name, text):
        imgs = soup.find_all(name="img", attrs={
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

        return soup

    def __rowToDict (self, row):
        cols = row.find_all(['th','td'])

        hmm = [col.text.strip() for col in cols ]
        #rowDict = [ col['data-region-slug'] for col in cols ]
        
        rowDict = {}

        for col in cols:
            print (col.text.strip())
            if (col.has_attr('data-region-slug')):
                if (col.text.strip().__contains__ ("Expected")):
                    rowDict[ col['data-region-slug'] ] = col.text.strip()
                    print("bob", rowDict)
                elif (col.text.strip().__contains__ ("Preview")):
                    rowDict[ col['data-region-slug'] ] = "Preview"
                elif (col.text.strip().__contains__ ("GA")):
                    rowDict[ col['data-region-slug'] ] = True
                else:
                    rowDict[ col['data-region-slug'] ] = False
            

        print (rowDict)

        return hmm


    def __processRow(self, row):

        cols = row.find_all(['th','td'])
        hmm = [col.text.strip() for col in cols ]

        doc = {
            'id': cols[0].text.strip().replace(u'\u2013', u'-'),
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
        


    def __processRow2(self, row):

        cols = row.find_all(['th','td'])
        hmm = [col.text.strip() for col in cols ]

        doc = {
            'id': cols[0].text.strip(),
            'type': row['class'][0],
            'ga': [],
            'preview': [],
            'planned-active': []
        }
        
        for col in cols:
            if (col.has_attr('data-region-slug')):
                if (col.text.strip().__contains__ ("check")):
                    doc['ga'].append(col['data-region-slug'])
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
        
        return doc
        

    def initialize(self):
        
        soup = self.__getFromLocal()
        soup = soup.find(attrs={"class":"primary-table"})
        
        soup = self.__replaceSoupImage(soup,"preview-active.svg", "preview-active")
        soup = self.__replaceSoupImage(soup,"planned-active.svg", "planned-active")
        soup = self.__replaceSoupImage(soup,"preview.svg", "preview")
        soup = self.__replaceSoupImage(soup,"ga.svg", "check")           

        tooltips = soup.find_all("span",attrs={"class":"table-tooltip"}) + soup.find_all("span",attrs={"class":"tooltip-content"}) + soup.find_all("span",attrs={"class":"hide-text"})

        for tiptag in tooltips:
            tiptag.decompose()

        rows = soup.find_all('tr')

        table_as_list = []
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



        print (json.dumps({
            'services': service_json,
            'capabilities': capability_json
        }))
        
        return 

        primaryTable = soup.find(attrs={"class":"primary-table"})
        rows = primaryTable.find_all('tr')

        table_headers = self.__rowToDict(rows[1])
        
        table_headers.append("type")
        table_headers.append("Category")
        table_headers.append("Service")
        table_headers.append("Capability")

        # print ("Headers", table_headers)

        table_as_list = []
        category_list = []
        service_list = []
        capability_list = []

        lastCategory = ""
        lastService = ""
        for row in rows[2:]:
            rowDict = self.__rowToDict(row)
            if row['class'].__contains__('category-row'):                
                lastCategory = rowDict[0]
                rowDict.append("category")
                rowDict.append(lastCategory)
                rowDict.append('')
                rowDict.append('')
                # print ("   Category Row", rowDict)
                category_list.append(rowDict)
                
            elif row['class'].__contains__('service-row'):
                lastService = rowDict[0]
                rowDict.append("service")
                rowDict.append(lastCategory)
                rowDict.append(lastService)
                rowDict.append('')
                # print ("    Service Row", rowDict)
                table_as_list.append(rowDict)
                service_list.append(rowDict)

            elif row['class'].__contains__('capability-row'):
                rowDict.append("capability")
                rowDict.append(lastCategory)
                rowDict.append(lastService)
                rowDict.append(rowDict[0])                
                # print (" Capability Row", rowDict)
                table_as_list.append(rowDict)              
                capability_list.append(rowDict)

            else: 
                print (rowDict)

            #tmp = [dict(zip(table_headers, [item for item in rowDict] ))]
            
        # tmp = [dict(zip(table_headers, [col for col in row])) for row in table_as_list]
        categories = [dict(zip(table_headers, [col for col in row])) for row in category_list]
        services = [dict(zip(table_headers, [col for col in row])) for row in service_list]
        capabilities = [dict(zip(table_headers, [col for col in row])) for row in capability_list]
  
        out = {
            'categories': categories,
            'services': services,
            'capabilities': capabilities
        }

        # print (out)

        return

        #print (soup)

        tree = html.fromstring(soup)


        html_tables = tree.xpath('//table[@id="primary-table"]/tbody')
        category_rows = tree.xpath('//table[@id="primary-table"]/*/tr[@class="category-row"]')
        service_rows = tree.xpath('//table[@id="primary-table"]/*/tr[@class="service-row"]')
        capability_rows = tree.xpath('//table[@id="primary-table"]/*/tr[@class="capability-row"]')
        
        # ('//tableprimary-table tr.category-row')
        # /html/body/main/div[5]/div[2]/div[1]/div/table/tbody/tr[3]
        

        #rows = resp.html.find(
        #    'table.primary-table tr.category-row, table.primary-table tr.service-row, table.primary-table tr.capability-row')
        
        #category_rows = tree.xpath('//table.primary-table tr.category-row')
        # print (self.__getDictionaryFromTable (html_tables[0]))

        print (html_tables)
        print (len(category_rows))
        
        print (len(service_rows))
        print (len(capability_rows))

        self.__tmp(html_tables[0])

    def __tmp(self, table):
        table_as_list = list(table)

        table_headers = [col.text.strip() for col in table_as_list[1]]
        print (table_headers)
        
        # tmp = [dict(zip(table_headers, [replace_images(text(col)).strip() for col in row])) for row in table_as_list[2:]]
        # print (tmp)
        
        for row in table_as_list[2:]:
            values = [text(col).strip() for col in row]
            print (dict(zip(table_headers, values)))

            row.xpath ("//td[img[@src='//azurecomcdn.azureedge.net/cvt-94bb7ea5624702377c0fe0b7ed7771726181533628678b7df021a4dd7d2d400d/images/page/global-infrastructure/services/ga.svg']]")
            print (len(row))

           
        # /html/body/main/div[5]/div[2]/div[1]/div/table/tbody/tr[5]/td[1]/img





    def __getDictionaryFromTable(self, table):
        table_as_list = list(table)
        # print(table_as_list)
        table_headers = [col.text.strip() for col in table_as_list[0][0]]
       
        tmp = [dict(zip(table_headers, [text(col) for col in row])) for row in table_as_list[1][0:]]
        d = {}

        for i in tmp :
            x = i.pop('Azure Service')           
            d[x] = i


        return d    
