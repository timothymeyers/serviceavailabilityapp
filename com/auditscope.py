from lxml import html

import requests
#import pprint
import logging
from re import split

# Constants

AZGOV_AUDIT_SCOPE_LIST = "https://docs.microsoft.com/en-us/azure/azure-government/compliance/azure-services-in-fedramp-auditscope#azure-government-services-by-audit-scope"

# Helpers

## Gets text from an HTML element
def text(elt):
    return elt.text_content().replace(u'\xa0', u' ').replace('✔️', "Check")

def camelize(string):
    return ''.join(a.capitalize() for a in split('([^a-zA-Z0-9])', string)
       if a.isalnum())

class AuditScopeList:
    def __init__(self):        
        self.__azurePublic = {}
        self.__azureGovt = {}
        self.__azPubCosmos = {}
        self.__azGovCosmos = {}
        self.__azCosmos = []

        logging.debug ("AuditScope Created")

    def initialize(self):
        logging.debug ("AuditScope - Starting Initialization")
        
        page = requests.get(AZGOV_AUDIT_SCOPE_LIST)
        tree = html.fromstring(page.content)

        logging.debug ("AuditScope - Page retrieved")

        html_tables = tree.xpath('//table')

        logging.debug ("AuditScope - HTML Tables found: Length %d", len(html_tables))

        self.__azurePublic = self.__getDictionaryFromTable (html_tables[0])
        self.__azureGovt   = self.__getDictionaryFromTable (html_tables[1])

        # self.__azPubCosmos = self.__getCosmosDBDocuments("Azure Public", self.__azurePublic)
        # self.__azGovCosmos = self.__getCosmosDBDocuments("Azure Government", self.__azureGovt)

        self.__parseIntoComosDBDocuments("Azure Public", self.__azurePublic)
        self.__parseIntoComosDBDocuments("Azure Government", self.__azureGovt)

        logging.debug ("AuditScope - Initialized")


    def __parseIntoComosDBDocuments(self, cloud, dictionary):       
        
        i = 0
        for service in dictionary.keys():
            svcDoc = {
                'id': "sc-" + str(i),
                "docType": "audit-scope",
                'prod-id': service,
                'cloud':cloud
            }

            for scope in dictionary[service].keys():
                
                tmp = camelize(scope)
                scopeCamel = tmp[0].lower() + tmp[1:]

                if dictionary[service][scope] == "Check":
                    svcDoc[scopeCamel] = True

            self.__azCosmos.append(svcDoc)
        
            i = i+1
        # logging.debug (self.__azCosmos)

    def __getCosmosDBDocuments(self, id, dictionary):
        doc = {
            "id": id,
            "services": []
        }

        for service in dictionary.keys():
            
            if service == 'Import / Export':
                service = 'Import Export'
            
            svcDoc = {
                'serviceName': service
            }

            for scope in dictionary[service].keys():
                
                tmp = camelize(scope)
                scopeCamel = tmp[0].lower() + tmp[1:]

                if dictionary[service][scope] == "Check":
                    svcDoc[scopeCamel] = True

                """
                if scope == "DISA IL 2" and dictionary[service][scope] == "Check":
                    svcDoc['disaIL2'] = True
                if scope == "DISA IL 4" and dictionary[service][scope] == "Check":
                    svcDoc['disaIL4'] = True
                if scope == "DISA IL 5" and dictionary[service][scope] == "Check":
                    svcDoc['disaIL5'] = True
                if scope == "DISA IL 6" and dictionary[service][scope] == "Check":
                    svcDoc['disaIL6'] = True
                if scope == "FedRAMP High" and dictionary[service][scope] == "Check":
                    svcDoc['fedRampHigh'] = True
                if scope == "FedRAMP Moderate" and dictionary[service][scope] == "Check":
                    svcDoc['fedRampModerate'] = True
                if scope == "Planned 2020" and dictionary[service][scope] == "Check":
                    svcDoc['planned2020'] = True
                """

            doc['services'].append(svcDoc)

        return doc

    def getAzurePublicJson(self):
        return self.__azPubCosmos

    def getAzureGovernmentJson(self):
        return self.__azGovCosmos

    def getCosmosArray(self):
        return self.__azCosmos
    
    def isAtAuditScope(self, service, scope):
        logging.debug ('isAtAuditScope - Checking [' + service + '] at [' + scope + ']')

        azPub = self.isAtAuditScopeForCloud(service,scope, "Azure Public", self.__azurePublic)
        azGov = self.isAtAuditScopeForCloud(service,scope, "Azure Government", self.__azureGovt)

        logging.debug ('isAtAuditScope - [%s] at [%s]. Azure Public [%s], Azure Gov [%s]',
            service, scope, azPub, azGov)

        return (azPub | azGov)  
    
    def isAtAuditScopeForCloud(self, service, scope, cloudName, cloud):
        
        logging.debug ('isAtAuditScopeForCloud - Checking [%s] at [%s] in [%s]',
            service, scope, cloudName)

        if not cloud:
            logging.info ('isAtAuditScopeForCloud - [' + cloudName + '] Does not exist')
            return False

        if not cloud.get(service):
            logging.debug ('isAtAuditScopeForCloud - [' + service +'] Does not exist in [' + cloudName + ']')
            return False


        logging.debug ('isAtAuditScopeForCloud - Found [%s] in [%s]\n%s', 
            service,
            cloudName,
            str(cloud.get(service)))

        checkScope = cloud.get(service).get(scope)

        if str(checkScope).__contains__('Check'):
            logging.debug ('isAtAuditScopeForCloud - [%s] in [%s], Check', 
                service, cloudName)
            return True

        logging.debug ('isAtAuditScopeForCloud - [%s] in [%s], No', 
            service, cloudName)
        
        return False

    def __getDictionaryFromTable(self, table):
        table_as_list = list(table)
        
        table_headers = [col.text.strip() for col in table_as_list[0][0]]
       
        tmp = [dict(zip(table_headers, [text(col) for col in row])) for row in table_as_list[1][0:]]
        d = {}

        for i in tmp :
            x = i.pop('Azure Service')
            d[x] = i

        return d