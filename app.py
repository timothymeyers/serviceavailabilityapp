from com.auditscope import AuditScopeList
# from com.mag_prod_availability import AzGovProductAvailabilty
from com.product_by_region import AzGovProductAvailabilty
import com.data_mapping as maps

import json


def main():

    sc = AuditScopeList()
    sc.initialize()

    av = AzGovProductAvailabilty()
    av.initialize()

    m = merge(sc, av)

    # list(d1.values())
    print(json.dumps(list(m.values())))

    return


def merge2(sc, av):

    merged = {}

    scList = sc.getCosmosJsonMerged()
    avList = av.getProductAvailabilityJson()

    # start with services
    for svc in avList['services']:
        d = {}
        d.update(svc)

        merged[svc['prod-id']] = d

    for id, prod in scList.items():
        print(id)
        if id in merged:
            merged[id].update(prod)
            merged[id]['docType'] = "merged"
            merged[id].pop('type')
        else:
            a = 0

    for cap in avList['capabilities']:
        lookupId = cap['service'] + ' ' + cap['prod-id']
        #print ("cap:", cap['prod-id'])

    # print (json.dumps(merged))

    return


def merge(sc, av):

    merged_services = {svc: {} for svc in maps.service_list}
    merged_capabilities = {cap: {} for cap in maps.capability_list}

    scList = sc.getCosmosJsonMerged()
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


main()
