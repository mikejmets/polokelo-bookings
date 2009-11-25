import logging

from workflow import Workflow, State, Transition, ExpirationSetting

logger = logging.getLogger('Init Workflow')

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.addState('temporary')
    wfl.addState('allocated')
    wfl.addState('requiresintervention')
    wfl.addState('detailsreceieved')
    wfl.addState('depositpaid')
    wfl.addState('paidinfull')
    wfl.addState('expired')
    wfl.addState('cancelled')

    wfl.addTransition('expiretemporary', 'temporary', 'expired')
    wfl.addTransition('allocate', 'temporary', 'allocated')
    wfl.addTransition('assigntouser', 'temporary', 'requiresintervention')

    wfl.addTransition('expiremanaully', 'requiresintervention', 'expired')
    wfl.addTransition('allocatemanually', 'requiresintervention', 'allocated')

    wfl.addTransition('expireallocated', 'allocated', 'expired')
    wfl.addTransition('receivedetails', 'allocated', 'detailsreceieved')

    wfl.addTransition('expiredetails', 'detailsreceieved', 'expired')
    wfl.addTransition('paydeposit', 'detailsreceieved', 'depositpaid')

    wfl.addTransition('expiredeposit', 'depositpaid', 'expired')
    wfl.addTransition('canceldeposit', 'depositpaid', 'cancelled')
    wfl.addTransition('payfull', 'depositpaid', 'paidinfull')

    wfl.addTransition('cancelfull', 'paidinfull', 'cancelled')
    
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
if False: #ENQUIRY_WORKFLOW:
    logger.info('Reseting the enquiry workflow')
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
