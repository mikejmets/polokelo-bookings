import logging

from workflow import Workflow, State, Transition, ExpirationSetting

logger = logging.getLogger('Init Workflow')

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.addState('temporary', title='Temporary')
    wfl.addState('allocated', title='Allocated')
    wfl.addState('requiresintervention', title='Requires Intervention')
    wfl.addState('detailsreceieved', title='Details Received')
    wfl.addState('depositpaid', title='Deposit Paid')
    wfl.addState('paidinfull', title='Paid In Full')
    wfl.addState('expired', title='Expired')
    wfl.addState('cancelled', title='Cancelled')

    wfl.addTransition('expiretemporary', 'temporary', 'expired', 
        title='Expire')
    wfl.addTransition('allocate', 'temporary', 'allocated', title='Allocate')
    wfl.addTransition('assigntouser', 'temporary', 'requiresintervention', 
        title='Assign to user')

    wfl.addTransition('expiremanaully', 'requiresintervention', 'expired', 
        title='Expire')
    wfl.addTransition('allocatemanually', 'requiresintervention', 'allocated', 
        title='Allocate')

    wfl.addTransition('expireallocated', 'allocated', 'expired', 
        title='Expire')
    wfl.addTransition('receivedetails', 'allocated', 'detailsreceieved', 
        title='Receive Details')

    wfl.addTransition('expiredetails', 'detailsreceieved', 'expired', 
        title='Expire')
    wfl.addTransition('paydeposit', 'detailsreceieved', 'depositpaid', 
        title='Pay deposit')

    wfl.addTransition(
        'expiredeposit', 'depositpaid', 'expired', title='Expire')
    wfl.addTransition(
        'canceldeposit', 'depositpaid', 'cancelled', title='Cancel')
    wfl.addTransition(
        'payfull', 'depositpaid', 'paidinfull', title='Pay in full')

    wfl.addTransition('cancelfull', 'paidinfull', 'cancelled', title='Cancel')
    
    wfl.setInitialState('temporary')
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
    logger.info('Recreate enquiry workflow')
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
