import logging

from workflow import Workflow, State, Transition, ExpirationSetting

logger = logging.getLogger('Init Workflow')


# Define and load the enquiry workflow

def loadEquiryWorkflow():
    wfl = Workflow(key_name='enquiry_workflow')
    wfl.put()
    wfl.addState('temporary', title='Temporary')
    wfl.addState('onhold', title='On Hold')
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
    wfl.addTransition('expiremanaully', 'temporary', 'expired', title='Expire')
    wfl.addTransition('putonhold', 'temporary', 'onhold', title='Put on Hold')

    wfl.addTransition('expireonhold', 'onhold', 'expired', title='Expire')
    wfl.addTransition('assigntouser', 'onhold', 'requiresintervention', 
        title='Assign to user')
    wfl.addTransition('allocatefromhold', 'onhold', 'allocated', 
        title='Allocate')

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
        entityState = 'onhold', 
        hours = 2)
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


# Define workflow for payment trackers
# We define a workflow for the tracker on the enquiry collection
# and a workflow for the tracker on the enquiry itself.
# The VCS payment records will affect the workflow

# the collection tracker payment workflow
def loadCollectionTrackerPaymentWorkflow():
    wfl = Workflow(key_name='collection_tracker_payment_workflow')
    wfl.put()
    wfl.addState('nopayment', title='No payments received')
    wfl.addState('paymentinprogress', title='Payment in progress')
    wfl.addState('paidinfull', title='Paid in Full')

    wfl.addTransition('receivepayment', 'nopayment', 'paymentinprogress', 
                            title='Receive Payment')
    wfl.addTransition('payinfull', 'paymentinprogress', 'paidinfull', 
                            title='Pay in full')
    wfl.setInitialState('nopayment')
    wfl.put()
    return wfl

COLL_TRACK_PAY_WORKFLOW = Workflow.get_by_key_name( \
                                'collection_tracker_payment_workflow')
if COLL_TRACK_PAY_WORKFLOW:
    logger.info('Recreate collection tracker payment workflow')
    for s in State.all().ancestor(COLL_TRACK_PAY_WORKFLOW):
        s.delete()
    for t in Transition.all().ancestor(COLL_TRACK_PAY_WORKFLOW):
        t.delete()
    COLL_TRACK_PAY_WORKFLOW.delete()
    COLL_TRACK_PAY_WORKFLOW = None

if not COLL_TRACK_PAY_WORKFLOW:
    COLL_TRACK_PAY_WORKFLOW = loadCollectionTrackerPaymentWorkflow()


# the enquiry tracker payment workflow
def loadEnquiryTrackerPaymentWorkflow():
    wfl = Workflow(key_name='enquiry_tracker_payment_workflow')
    wfl.put()
    wfl.addState('nopayment', title='No payments received')
    wfl.addState('depositreceived', title='Deposit Received')
    wfl.addState('paidinfull', title='Paid in Full')

    wfl.addTransition('receivedeposit', 'nopayment', 'depositreceived', 
                            title='Receive Deposit')
    wfl.addTransition('payinfull', 'depositreceived', 'paidinfull', 
                            title='Pay outstanding amount')
    wfl.setInitialState('nopayment')
    wfl.put()
    return wfl

ENQRY_TRACK_PAY_WORKFLOW = Workflow.get_by_key_name('enquiry_tracker_payment_workflow')
if ENQRY_TRACK_PAY_WORKFLOW:
    logger.info('Recreate collection tracker payment workflow')
    for s in State.all().ancestor(ENQRY_TRACK_PAY_WORKFLOW):
        s.delete()
    for t in Transition.all().ancestor(ENQRY_TRACK_PAY_WORKFLOW):
        t.delete()
    ENQRY_TRACK_PAY_WORKFLOW.delete()
    ENQRY_TRACK_PAY_WORKFLOW = None

if not ENQRY_TRACK_PAY_WORKFLOW:
    ENQRY_TRACK_PAY_WORKFLOW = loadEnquiryTrackerPaymentWorkflow()
