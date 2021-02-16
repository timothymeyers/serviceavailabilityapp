from com.auditscope import AuditScopeList
from com.product_by_region import AzGovProductAvailabilty
from com import data_mapping as maps

import json
import logging


class DataJoiner:

    def __init__(self, audit_scopes = AuditScopeList(), product_availability = AzGovProductAvailabilty()):
        #self.__product_availability = AzGovProductAvailabilty()
        #self.__audit_scopes = AuditScopeList()

        self.__product_availability = product_availability
        self.__audit_scopes = audit_scopes

        self.__joined_data = self.__join(
            self.__audit_scopes, self.__product_availability)

    def __join(self, sc, av):

        blankCloud = {
            "available": False,
            "scopes": [],
            "ga": [],
            "preview": [],
            "planned-active": []
        }

        merged_services = {svc: {
            'prod-id': svc,
            'type': 'service',
            'capabilities': [],
            'categories': [],
            'azure-public': blankCloud.copy(),
            'azure-government': blankCloud.copy()
        } for svc in maps.service_list}

        merged_capabilities = {cap: {
            'prod-id': cap,
            'type': 'capability',
            'service': maps.capability_service_map[cap],
            'categories': [],
            'azure-public': blankCloud.copy(),
            'azure-government': blankCloud.copy()
        } for cap in maps.capability_list}

        scList = sc.getCosmosJsonMerged()
        avList = av.getProductAvailabilityJson()

        # initialize using availability list

        for p in (avList['services'] + avList['capabilities']):

            # ugh special Data Box capability case
            if (p['prod-id'] == "Data Box" and p['type'] == "capability-row"):
                pId = p['prod-id']
            else:
                pId = maps.clean_product_name(p['prod-id'])

            try:
                if (pId in maps.service_list):

                    merged_services[pId]['capabilities'] = p['capabilities'][:]
                    merged_services[pId]['categories'] = list(p['categories'])

                    merged_services[pId]['azure-public']['ga'] = p['azure-public']['ga'][:]
                    merged_services[pId]['azure-public']['available'] = (
                        len(p['azure-public']['ga']) > 0)
                    merged_services[pId]['azure-public']['preview'] = list(
                        p['azure-public']['preview'])
                    merged_services[pId]['azure-public']['planned-active'] = list(
                        p['azure-public']['planned-active'])

                    merged_services[pId]['azure-government']['ga'] = list(
                        p['azure-government']['ga'])
                    merged_services[pId]['azure-government']['available'] = (
                        len(p['azure-government']['ga']) > 0)
                    merged_services[pId]['azure-government']['preview'] = list(
                        p['azure-government']['preview'])
                    merged_services[pId]['azure-government']['planned-active'] = list(
                        p['azure-government']['planned-active'])

                elif (pId in maps.capability_list):
                    merged_capabilities[pId]['categories'] = list(
                        p['categories'])

                    merged_capabilities[pId]['azure-public']['ga'] = list(
                        p['azure-public']['ga'])
                    merged_capabilities[pId]['azure-public']['available'] = (
                        len(p['azure-public']['ga']) > 0)
                    merged_capabilities[pId]['azure-public']['preview'] = list(
                        p['azure-public']['preview'])
                    merged_capabilities[pId]['azure-public']['planned-active'] = list(
                        p['azure-public']['planned-active'])

                    merged_capabilities[pId]['azure-government']['ga'] = list(
                        p['azure-government']['ga'])
                    merged_capabilities[pId]['azure-government']['available'] = (
                        len(p['azure-government']['ga']) > 0)
                    merged_capabilities[pId]['azure-government']['preview'] = list(
                        p['azure-government']['preview'])
                    merged_capabilities[pId]['azure-government']['planned-active'] = list(
                        p['azure-government']['planned-active'])

            except KeyError as e:
                print("Error")
                print('\te', e)
                print('\tpId', pId)

        for pId, p in scList.items():
            pId = maps.clean_product_name(pId)

            try:

                if (pId in maps.service_list and "azure-public" in p and len(p['azure-public']['scopes']) > 0):
                    merged_services[pId]['azure-public']['scopes'] = list(
                        p['azure-public']['scopes'])
                if (pId in maps.service_list and "azure-government" in p and len(p['azure-government']['scopes']) > 0):
                    merged_services[pId]['azure-government']['scopes'] = list(
                        p['azure-government']['scopes'])

                if (pId in maps.capability_list and "azure-public" in p and len(p['azure-public']['scopes']) > 0):
                    merged_capabilities[pId]['azure-public']['scopes'] = list(
                        p['azure-public']['scopes'])
                if (pId in maps.capability_list and "azure-government" in p and len(p['azure-government']['scopes']) > 0):
                    merged_capabilities[pId]['azure-government']['scopes'] = list(
                        p['azure-government']['scopes'])

            except KeyError as e:
                print("Error")
                print('\te', e)
                print('\tpId', pId)
                if (pId in maps.service_list):
                    print('\tsvc', merged_services[pId])
                if (pId in maps.capability_list):
                    print('\tcap', merged_capabilities[pId])
                print('\ts-p', p)

        # print(json.dumps({'svc': merged_services,'cap': merged_capabilities}))

        return self.__map_capabilities_to_services(merged_services, merged_capabilities)

    def __map_capabilities_to_services(self, svc, caps):

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

    def getJoinedData(self):
        return self.__joined_data
