import logging

from workflow import Workflow, State, Transition, ExpirationSetting

logger = logging.getLogger('Init Workflow')

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.add_state('temporary')
    wfl.add_state('allocated')
    wfl.add_state('requiresintervention')
    wfl.add_state('detailsreceieved')
    wfl.add_state('depositpaid')
    wfl.add_state('paidinfull')
    wfl.add_state('expired')
    wfl.add_state('cancelled')

    wfl.add_trans('expiretemporary', 'temporary', 'expired')
    wfl.add_trans('allocate', 'temporary', 'allocated')
    wfl.add_trans('assigntouser', 'temporary', 'requiresintervention')

    wfl.add_trans('expiremanaully', 'requiresintervention', 'expired')
    wfl.add_trans('allocatemanually', 'requiresintervention', 'allocated')

    wfl.add_trans('expireallocated', 'allocated', 'expired')
    wfl.add_trans('receivedetails', 'allocated', 'detailsreceieved')

    wfl.add_trans('expiredetails', 'detailsreceieved', 'expired')
    wfl.add_trans('paydeposit', 'detailsreceieved', 'depositpaid')

    wfl.add_trans('expiredeposit', 'depositpaid', 'expired')
    wfl.add_trans('canceldeposit', 'depositpaid', 'cancelled')
    wfl.add_trans('payfull', 'depositpaid', 'paidinfull')

    wfl.add_trans('cancelfull', 'paidinfull', 'cancelled')
    
    wfl.set_initstate('temporary')
    wfl.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityState = 'temporary', 
        hours = 1)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityTransition = 'allocate', 
        entityState = 'allocated', 
        hours = 6)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityTransition = 'receivedetails', 
        entityState = 'detailsreceieved', 
        hours = 24)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityTransition = 'paydeposit', 
        entityState = 'depositpaid', 
        hours = 72)
    bcs.put()

    bcs = ExpirationSetting(
        entityKind = 'Enquiry', 
        entityTransition = 'payfull', 
        entityState = 'paidinfull', 
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
