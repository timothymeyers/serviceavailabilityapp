import logging

import azure.functions as func

from ..com.auditscope import AuditScopeList
from ..com.product_by_region import AzGovProductAvailabilty

def main(req: func.HttpRequest, cosmosDB: func.Out[func.Document]) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    ## ***************************************************************

    sc = AuditScopeList()
    sc.initialize()

    av = AzGovProductAvailabilty()
    av.initialize()

    ## ***************************************************************

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )


def normalize (sc, av):

    scList = sc.getCosmosArray()
    avList = av.getProductAvailabilityJson()  

    

    return {}