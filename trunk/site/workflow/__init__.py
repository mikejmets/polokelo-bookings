import logging

from workflow import Workflow, State

logger = logging.getLogger('Init Workflow')

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.add_state('temporary')
    wfl.add_state('allocated')
    wfl.add_state('requiresintervention')
    wfl.add_state('depositpaid')
    wfl.add_state('paidinfull')

    wfl.add_trans('allocate', 'temporary', 'allocated')
    wfl.add_trans('assigntouser', 'temporary', 'requiresintervention')
    wfl.add_trans('paydeposit', 'allocated', 'depositpaid')
    wfl.add_trans('payfull', 'depositpaid', 'paidinfull')
    
    wfl.set_initstate('temporary')
    wfl.put()
    return wfl

ENQUIRY_WORKFLOW = Workflow.get_by_key_name('enquiry_workflow')
if not ENQUIRY_WORKFLOW:
    ENQUIRY_WORKFLOW = loadEquiryWorkflow()
