from lxml import html

import requests
import pprint
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

        logging.debug ("[+===+] AuditScope Initialized")

    def initialize(self):
        page = requests.get(AZGOV_AUDIT_SCOPE_LIST)
        tree = html.fromstring(page.content)

        logging.debug ("[+===+] Page retrieved")

        html_tables = tree.xpath('//table')

        logging.debug ("[+===+] HTML Tables found: Length %d", len(html_tables))

        self.__azurePublic = self.__getDictionaryFromTable (html_tables[0])
        self.__azureGovt   = self.__getDictionaryFromTable (html_tables[1])

    
    def isAtAuditScope(self, service, scope):
        logging.debug ('[+===+] Checking [' + service + '] at Audit Scope [' + scope + ']')

        azPub = self.isAtAuditScopeForCloud(service,scope, "Azure Public", self.__azurePublic)
        azGov = self.isAtAuditScopeForCloud(service,scope, "Azure Government", self.__azureGovt)

        return (azPub | azGov)  
    
    def isAtAuditScopeForCloud(self, service, scope, cloudName, cloud):
        
        if not cloud:
            logging.debug ('[+=====+] [' + cloudName + '] Does not exist')
            return False

        if not cloud.get(service):
            logging.debug ('[+=====+] [' + service +'] Does not exist in [' + cloudName + ']')
            return False

        logging.debug ('[+=====+] ' + str(cloud.get(service)))


        checkScope = cloud.get(service).get(scope)

        if str(checkScope).__contains__('Check'):
            logging.debug ('[+=====+] [' + cloudName + '] Check')
            return True

        logging.debug ('[+=====+] [' + cloudName + '] No')
        
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