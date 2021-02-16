from com.auditscope import AuditScopeList
# from com.mag_prod_availability import AzGovProductAvailabilty
from com.product_by_region import AzGovProductAvailabilty
from com.data_joiner import DataJoiner
import com.data_mapping as maps

import json


def main():

    sc = AuditScopeList()
    #sc.initialize()

    av = AzGovProductAvailabilty()
    #av.initialize()

    dj = DataJoiner(sc, av)

    # m = merge(sc, av)
    m = dj.getJoinedData()

    # list(d1.values())
    print(json.dumps(list(m.values())))

    return

main()
