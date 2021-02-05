import datetime
import logging
import json

from ..com.auditscope import AuditScopeList

import azure.functions as func

def main(mytimer: func.TimerRequest, azPubOut: func.Out[func.Document], azGovOut: func.Out[func.Document]) -> str:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    timestamp = datetime.datetime.now()


    if mytimer.past_due:
        logging.warn('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', timestamp)

    sl = AuditScopeList()
    sl.initialize()   

    try:
        #outdata = {
        #    "id": "Audit Scopes",
        #    "clouds": [
        #        sl.getAzureGovernmentJson(),
        #        sl.getAzurePublicJson()
        #    ]
        #}

        #outdoc.set(func.Document.from_json(json.dumps(outdata)))

        # azPubOut.set(func.Document.from_json(json.dumps(sl.getAzurePublicJson())))
        # azGovOut.set(func.Document.from_json(json.dumps(sl.getAzureGovernmentJson())))

        cosmosArray = sl.getCosmosArray()

        newdocs = func.DocumentList()

        for service in cosmosArray:
            logging.info( service ) 
            
            # newdocs.append(func.Document.from_dict(json.dumps(service)))
            newdocs.append(func.Document.from_dict(service))
            
        
        # logging.info( newdocs )

        azPubOut.set(newdocs)




    except Exception as e:
        logging.error('Error:' + e)
        return 0