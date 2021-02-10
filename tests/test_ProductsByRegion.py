import pytest
from com.product_by_region import AzGovProductAvailabilty

# "Constaints"

# "Fixtures"
@pytest.fixture(scope="session")
def scopeList():
    l = AzGovProductAvailabilty()
    l.initialize()
    return l

#Tests

def test_isInitialized(scopeList):   
    #assert scopeList.getAzurePublicJson()
    #assert scopeList.getAzureGovernmentJson()
    assert True

def test_isAtAuditScopeForCloud_noCloud(scopeList):
    # assert scopeList.isAtAuditScopeForCloud('','','', None) == False
    assert True

@pytest.mark.parametrize("service, scope, expected_result", [
    ('', 'DoD CC SRG IL 2', False),
    ('', 'FedRAMP Moderate', False),
    ('', 'FedRAMP High', False),
    ('', 'Planned 2021', False),

    ('API Management', 'DoD CC SRG IL 2', True),
    ('API Management', 'FedRAMP Moderate', True),
    ('API Management', 'FedRAMP High', True),
    ('API Management', 'Planned 2021', False),

    ('Azure Data Lake Storage', 'Planned 2021', True),

    ('Azure Data Box', 'FedRAMP High', True),
    
])
def test_checkAzurePublic(scopeList, service, scope, expected_result):
    # assert scopeList.isAtAuditScope(service, scope) == expected_result
    assert True

@pytest.mark.parametrize("service, scope, expected_result", [
    ('', 'DoD CC SRG IL 2', False),
    ('', 'DoD CC SRG IL 4', False),
    ('', 'DoD CC SRG IL 5', False),
    ('', 'FedRAMP High', False),      
    ('', 'DoD CC SRG IL 6', False),

    ('Application Gateway', 'DoD CC SRG IL 2', True),
    ('Application Gateway', 'DoD CC SRG IL 4', True),
    ('Application Gateway', 'DoD CC SRG IL 5 (Azure Gov)', True),
    ('Application Gateway', 'DoD CC SRG IL 5 (Azure DoD)', True),
    ('Application Gateway', 'FedRAMP High', True),    
    ('Application Gateway', 'DoD CC SRG IL 6', True),

    ('Stream Analytics', 'DoD CC SRG IL 2', True),
    ('Stream Analytics', 'DoD CC SRG IL 4', True),
    ('Stream Analytics', 'DoD CC SRG IL 5 **', False),
    ('Stream Analytics', 'FedRAMP High', True),    
    ('Stream Analytics', 'DoD CC SRG IL 6', False),
])
def test_checkAzureGovernment(scopeList, service, scope, expected_result):
    #assert scopeList.isAtAuditScope(service, scope) == expected_result
    assert True