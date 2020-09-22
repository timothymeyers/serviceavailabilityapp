import datetime
import logging

import azure.functions as func

from serviceavailabilityapp.com.auditscope import AuditScopeList

def main(mytimer: func.TimerRequest) -> None:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.warn('The timer is past due!')

    logging.info ("TimeTrigger1 ran at %s", utc_timestamp)

    sl = AuditScopeList()
    #sl.initialize()

    #service = "API Management"
    #scope = "DISA IL 2"

    #flag = sl.isAtAuditScope(service,scope)
    #logging.info ("Checking [%s] at Audit Scope[%s]: %s", service, scope, flag)
    
