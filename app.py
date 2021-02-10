from com.auditscope import AuditScopeList
# from com.mag_prod_availability import AzGovProductAvailabilty
from com.product_by_region import AzGovProductAvailabilty


def main ():
    """
    scopeList = AuditScopeList()
    scopeList.initialize()

    #scopeList.isAtAuditScope('API Management', 'DISA IL 2')
    #scopeList.isAtAuditScope('', 'DISA IL 2')
    #scopeList.isAtAuditScope('', '')
    #scopeList.isAtAuditScope('Azure Data Box', 'FedRAMP High')
    #scopeList.isAtAuditScope('Application Gateway', 'DISA IL 5')
    scopeList.writeJsonTempFile()
    """

    p = AzGovProductAvailabilty()
    p.initialize()
#    p.initializeAllRows()
#    p.writeJsonTempFile()
"""
    p.isProductAvailableInRegion('Azure Bot Service','usgov-non-regional')
    p.isProductAvailableInRegion('Azure Cognitive Services', 'usgov-non-regional')    
    p.isProductAvailableInRegion('Cognitive Search', 'usgov-virginia')
    p.isProductInPreview('Azure Databricks')
    p.getProductRegionStatus('Azure Databricks')
    p.getProductRegionStatus('Azure Bot Service')
    p.getProductRegionStatus('Anomaly Detector')
    p.getProductRegionStatus('Logic Apps')
    p.getProductRegionStatus('Edsv4-series')
    p.isProductAvailableInRegion('Azure Active Directory External Identities', 'usgov-non-regional',True)
    p.isProductInPreview('Azure Active Directory External Identities')
    p.getRegionProductList('usgov-non-regional', True)
    """

main ()
