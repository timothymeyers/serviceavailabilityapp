import datetime
import logging
import json

from ..com.product_by_region import AzGovProductAvailabilty

import azure.functions as func


# https://service.prerender.io/https://azure.microsoft.com/en-us/global-infrastructure/services/?products=all&regions=usgov-non-regional,us-dod-central,us-dod-east,usgov-arizona,usgov-texas,usgov-virginia


def main(mytimer: func.TimerRequest, azServicesOut: func.Out[func.Document], azCapabilitiesOut: func.Out[func.Document]) -> str:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    timestamp = datetime.datetime.now()


    if mytimer.past_due:
        logging.warn('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', timestamp)

    sl = AzGovProductAvailabilty()
    # sl.initialize()   

    try:
        svcList = sl.getServicesList()

        svcDocs = func.DocumentList()

        for service in svcList:
            logging.info( service ) 
            svcDocs.append(func.Document.from_dict(service))

        azServicesOut.set(svcDocs)           

        capList = sl.getCapabilitiesList()

        capDocs = func.DocumentList()

        for cap in capList:
            logging.info( cap ) 
            capDocs.append(func.Document.from_dict(cap))

        azCapabilitiesOut.set(capDocs)

    except Exception as e:
        logging.error('Error:' + e)
        return 0