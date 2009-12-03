from google.appengine.ext import db

from workflow.workflow import Workflow, ExpirationSetting

ENQUIRY_WORKFLOW = 'enquiry_workflow'

class EnquiryRoot(db.Model):
    """ Act as the glue for transactions living below it.
        All EnquiryCollection and Workflow instances must have the
        single instance of this class as their parent
    """

    @classmethod
    def getEnquiryRoot(cls):
        """ return a handle to the enquiry root instance
        """
        er = EnquiryRoot.get_by_key_name('enquiries_root')
        if not er:
            er = EnquiryRoot(key_name='enquiries_root')
            er.put()
        return er

    @classmethod
    def getEnquiryWorkflow(cls):
        """ return a handle to the enquiry workflow instance
        """
        er = EnquiryRoot.getEnquiryRoot()
        wfl = Workflow.get_by_key_name(ENQUIRY_WORKFLOW, parent=er)
        if not wfl:
            wfl = er._createWorkflow()
        return wfl

    def _createWorkflow(self):
        wfl = Workflow(key_name=ENQUIRY_WORKFLOW, parent=self)
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

        wfl.addTransition('expiretemporary', 'temporary', 'expired', title='Expire')
        wfl.addTransition('allocate', 'temporary', 'allocated', title='Allocate')
        wfl.addTransition('expiremanaully', 'temporary', 'expired', title='Expire')
        wfl.addTransition('putonhold', 'temporary', 'onhold', title='Put on Hold')

        wfl.addTransition('expireonhold', 'onhold', 'expired', title='Expire')
        wfl.addTransition('assigntouser', 'onhold', 'requiresintervention', \
                                title='Assign to user')
        wfl.addTransition('allocatefromhold', 'onhold', 'allocated', title='Allocate')

        wfl.addTransition('allocatemanually', 'requiresintervention', 'allocated', \
                                title='Allocate')
        wfl.addTransition('expireallocated', 'allocated', 'expired', title='Expire')
        wfl.addTransition('receivedetails', 'allocated', 'detailsreceieved', \
                                title='Receive Details')

        wfl.addTransition('expiredetails', 'detailsreceieved', 'expired', title='Expire')
        wfl.addTransition('paydeposit', 'detailsreceieved', 'depositpaid', \
                                title='Pay deposit')

        wfl.addTransition('expiredeposit', 'depositpaid', 'expired', title='Expire')
        wfl.addTransition('canceldeposit', 'depositpaid', 'cancelled', title='Cancel')
        wfl.addTransition('payall', 'detailsreceieved', 'paidinfull', \
                                title='Pay in full')
        wfl.addTransition('payfull', 'depositpaid', 'paidinfull', title='Pay in full')

        wfl.addTransition('cancelfull', 'paidinfull', 'cancelled', title='Cancel')
        wfl.put()
        
        wfl.setInitialState('temporary')
        wfl.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityState = 'temporary', 
            hours = 1)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityState = 'onhold', 
            hours = 2)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityTransition = 'allocate', 
            entityState = 'allocated', 
            hours = 6)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityTransition = 'receivedetails', 
            entityState = 'detailsreceieved', 
            hours = 24)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityTransition = 'paydeposit', 
            entityState = 'depositpaid', 
            hours = 72)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityTransition = 'payfull', 
            entityState = 'paidinfull', 
            hours = -1)
        bcs.put()

        return wfl

