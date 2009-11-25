import logging

from workflow import Workflow, State, Transition, ExpirationSetting

logger = logging.getLogger('Init Workflow')

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.add_state('temporary')
    wfl.add_state('allocated')
    wfl.add_state('requiresintervention')
    wfl.add_state('depositpaid')
    wfl.add_state('paidinfull')
    wfl.add_state('expired')
    wfl.add_state('cancelled')

    wfl.add_trans('expire', 'temporary', 'expired')
    wfl.add_trans('allocate', 'temporary', 'allocated')
    wfl.add_trans('expire', 'allocated', 'expired')
    wfl.add_trans('assigntouser', 'temporary', 'requiresintervention')
    wfl.add_trans('paydeposit', 'allocated', 'depositpaid')
    wfl.add_trans('expire', 'depositpaid', 'expired')
    wfl.add_trans('cancel', 'depositpaid', 'cancelled')
    wfl.add_trans('payfull', 'depositpaid', 'paidinfull')
    wfl.add_trans('cancel', 'paidinfull', 'cancelled')
    
    wfl.set_initstate('temporary')
    wfl.put()
    logger.info('-------------Ini %s', wfl.initstate)

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityState = 'temporary', 
        hours = 1)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityState = 'allocated', 
        entityTransition = 'allocate', 
        hours = 24)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityState = 'depositpaid', 
        entityTransition = 'paydeposit', 
        hours = 72)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityState = 'paidinfull', 
        entityTransition = 'payfull', 
        hours = -1)
    bcs.put()

    return wfl

ENQUIRY_WORKFLOW = Workflow.get_by_key_name('enquiry_workflow')
if ENQUIRY_WORKFLOW:
    for s in State.all().ancestor(ENQUIRY_WORKFLOW):
        s.delete()
    for t in Transition.all().ancestor(ENQUIRY_WORKFLOW):
        t.delete()
    ENQUIRY_WORKFLOW.delete()
    for e in ExpirationSetting.all():
        e.delete()

    ENQUIRY_WORKFLOW = None
if not ENQUIRY_WORKFLOW:
    ENQUIRY_WORKFLOW = loadEquiryWorkflow()
