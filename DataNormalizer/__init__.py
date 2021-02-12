import logging

import azure.functions as func

from ..com.auditscope import AuditScopeList
from ..com.product_by_region import AzGovProductAvailabilty
import com.data_mapping as maps
import json


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

    # ***************************************************************

    sc = AuditScopeList()
    sc.initialize()

    av = AzGovProductAvailabilty()
    av.initialize()

    m = merge (sc, av)

    logging.debug(json.dumps(m))

    # ***************************************************************

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )


def merge (sc, av):

    merged_services = {svc: {} for svc in maps.service_list}
    merged_capabilities = {cap: {} for cap in maps.capability_list}

    scList = sc.getCosmosArray()
    avList = av.getProductAvailabilityJson()

    for p in (avList['services'] + avList['capabilities']):

        # ugh special Data Box capability case
        if (p['prod-id'] == "Data Box" and p['type'] == "capability-row"):
            pId = p['prod-id']
        else:
            pId = clean_product_name(p['prod-id'])

        pDoc = {}
        pDoc.update(p)
        pDoc['prod-id'] = pId
        pDoc.pop('docType')
        pDoc.pop('id')

        if (pId in maps.service_list):
            pDoc['type'] = "service"
            merged_services[pId].update(pDoc)

        if (pId in maps.capability_list):
            pDoc['type'] = "capability"

            if (pId in maps.capability_service_map):
                pDoc['service'] = maps.capability_service_map[pId]

            if "capabilities" in pDoc.keys():
                pDoc.pop('capabilities')

            merged_capabilities[pId].update(pDoc)

        # else:
        #     print ('Oh no! [avlist]', pId)

    for pId, p in scList.items():
        pId = clean_product_name(pId)

        pDoc = {}
        pDoc.update(p)
        pDoc['prod-id'] = pId
        pDoc.pop('docType')
        pDoc.pop('id')

        if (pId in maps.service_list):
            pDoc['type'] = "service"

            if (pId not in merged_services):
                merged_services[pId] = {}

            merged_services[pId].update(pDoc)

        if (pId in maps.capability_list):
            pDoc['type'] = "capability"

            if (pId in maps.capability_service_map):
                pDoc['service'] = maps.capability_service_map[pId]

            merged_capabilities[pId].update(pDoc)

        # else:
        #    print ('Oh no! [scopes]', pId)

    return map_capabilities_to_services(merged_services, merged_capabilities)


def map_capabilities_to_services(svc, caps):

    merged = {}
    merged_c = {}

    i = 0
    for s, doc in svc.items():
        merged[s] = {}
        merged[s].update(doc)
        merged[s]['id'] = 's-' + str(i)

        try:
            merged[s]['capabilities'].clear()
        except KeyError as e:
            merged[s]['capabilities'] = []

        i = i + 1

    i = 0
    for c, doc in caps.items():
        try:
            sId = doc['service']

            merged_c[c] = {}
            merged_c[c].update(doc)
            merged_c[c]['id'] = 'c-' + str(i)

            merged[sId]['capabilities'].append(c)
        except KeyError as e:
            print("KeyError:")
            print("\t", e)
            print("\t", c)
            print("\t", json.dumps(doc))

        i = i + 1

    return {**merged, **merged_c}


def clean_product_name(name):

    if (name in maps.service_map):
        return maps.service_map[name]
    elif (name in maps.capability_map):
        return maps.capability_map[name]

    return name
