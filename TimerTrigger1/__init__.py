import datetime
import logging

from ..com.auditscope import AuditScopeList

import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
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

    service = "API Management"
    scope = "DISA IL 2"

    flag = sl.isAtAuditScope(service,scope)
    logging.info ("Checking [%s] at Audit Scope [%s] - Flag: %s", service, scope, flag)
    
    service = "Azure Databricks"
    scope = "DISA IL 5"

    flag = sl.isAtAuditScope(service,scope)
    logging.info ("Checking [%s] at Audit Scope [%s] - Flag: %s", service, scope, flag)
    
