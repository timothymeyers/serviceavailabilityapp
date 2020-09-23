from lxml import html

import requests
#import pprint
import logging

# Constants

AZGOV_AUDIT_SCOPE_LIST = "https://docs.microsoft.com/en-us/azure/azure-government/compliance/azure-services-in-fedramp-auditscope#azure-government-services-by-audit-scope"

# Helpers

## Gets text from an HTML element
def text(elt):
    return elt.text_content().replace(u'\xa0', u' ').replace('✔️', "Check")


class AuditScopeList:
    def __init__(self):        
        self.__azurePublic = {}
        self.__azureGovt = {}

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

        logging.debug ("AuditScope - Initialized")

    
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