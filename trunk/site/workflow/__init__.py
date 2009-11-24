import logging

from workflow import Workflow, State

logger = logging.getLogger('Init Workflow')

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.add_state('temporary')
    wfl.add_state('allocated')
    wfl.add_state('depositpaid')

    wfl.add_trans('allocate', 'temporary', 'allocated')
    wfl.add_trans('paydeposity', 'allocated', 'depositpaid')
    wfl.set_initstate('temporary')
    return wfl

ENQUIRY_WORKFLOW = Workflow.get_by_key_name('enquiry_workflow')
if ENQUIRY_WORKFLOW:
    for s in State.all().ancestor(ENQUIRY_WORKFLOW):
        s.delete()
    ENQUIRY_WORKFLOW.delete()
    ENQUIRY_WORKFLOW = None
if not ENQUIRY_WORKFLOW:
    ENQUIRY_WORKFLOW = loadEquiryWorkflow()
