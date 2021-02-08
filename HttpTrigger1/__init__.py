import logging

import azure.functions as func

from requests_html import HTMLSession

AZGOV_PRODS_BY_REGION = "https://azure.microsoft.com/en-us/global-infrastructure/services/"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )

    session = HTMLSession()
    resp = session.get(AZGOV_PRODS_BY_REGION, params={
                        'products': 'all', 'regions': 'usgov-non-regional,us-dod-central,us-dod-east,usgov-arizona,usgov-texas,usgov-virginia'})
    resp.html.render(sleep=3)

    rows = resp.html.find(
        'table.primary-table tr.category-row, table.primary-table tr.service-row, table.primary-table tr.capability-row')

    print (rows)


