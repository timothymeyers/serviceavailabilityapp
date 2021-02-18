from com.auditscope import AuditScopeList
# from com.mag_prod_availability import AzGovProductAvailabilty
from com.product_by_region import AzGovProductAvailabilty
from com.data_joiner import DataJoiner
import com.data_mapping as maps

import json


def main():

    dj = DataJoiner()
    data = dj.getJoinedData()
    #dj.qnaGetAvailable()
    dj.qnaGetScope()
    dj.qnaGetRegions()


    return

main()


"""
Is XXX available?
Is XXX ga?
Is XXX ga?in Azure Government?
Is XXX ga?in Azure Commercial?
Is XXX available in Azure Government?
Is XXX available in Azure Commercial?

Is XXX in preview?
Is XXX in preview in Azure Government?
Is XXX in preview in Azure Commercial?

When is XXX expected to be available?
When is XXX expected to be available in Azure Government?
When is XXX expected to be available in Azure Commercial?

What regions is XXX available in?
What regions is XXX available in Azure Commercial?
What regions is XXX available in Azure Government?

What can you tell me about XXX?"

What scopes is XXX available at?
What scopes is XXX available at in Azure Commercial?
What scopes is XXX available at in Azure Government?

What is available in XXX region?

What is available at XXX scope?
What is available at XXX scope in Azure Commercial?
What is available at XXX scope in Azure Government?
"""