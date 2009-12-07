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
        wfl.addState('allocated', title='Allocated')
        wfl.addState('confirmed', title='Confirmed')
        wfl.addState('receiveddeposit', title='Received Deposit')
        wfl.addState('receivedfull', title='Received Full Payment')
        wfl.addState('onhold', title='On Hold')
        wfl.addState('awaitingagent', title='Awaiting Agent')
        wfl.addState('awaitingclient', title='Awaiting Guest')
        wfl.addState('expired', title='Expired')
        wfl.addState('cancelled', title='Cancelled')

        #Grouped my paths
        #Auto allocate full payment
        wfl.addTransition('allocatetemporary', 'temporary', 'allocated', 
            title='Allocate')
        wfl.addTransition('confirmfromallocated', 'allocated', 'confirmed', \
            title='Confirm')
        wfl.addTransition('receiveall', 'confirmed', 'receivedfull', \
            title='Receive whole payment')

        #Auto allocate deposit and final payment
        wfl.addTransition('receivedeposit', 'confirmed', 'receiveddeposit', \
            title='Receive deposit')
        wfl.addTransition('receivefinal', 'receiveddeposit', 'receivedfull', \
            title='Receive final payment')

        #Auto allocate unsuccessful
        wfl.addTransition('putonhold', 'temporary', 'onhold', 
            title='Put on hold')
        wfl.addTransition('assigntoagent', 'onhold', 'awaitingagent', \
            title='Assign to agent')
        wfl.addTransition('allocatebyagent', 'awaitingagent', 'allocated', \
            title='Allocate')

        #Agent allocation
        wfl.addTransition('temptoagent', 'temporary', 'awaitingagent', \
            title='Temporary to agent')
        wfl.addTransition('assigntoclient', 'allocated', 'awaitingclient', \
            title='Assign to guest')
        wfl.addTransition('confirmfromawaiting', 'awaitingclient','confirmed', \
            title='Confirm')

        #Expiries
        wfl.addTransition('expiretemporary', 'temporary', 'expired', \
            title='Expire')
        wfl.addTransition('expireallocated', 'allocated', 'expired', \
            title='Expire')
        wfl.addTransition('expireconfirmed', 'confirmed', 'expired', \
            title='Expire')
        wfl.addTransition('expiredeposit', 'receiveddeposit', 'expired', 
            title='Expire')
        wfl.addTransition('expireonhold', 'onhold', 'expired', \
            title='Expire')
        wfl.addTransition('expireawaitingagent', 'awaitingagent', 'expired', \
            title='Expire')
        wfl.addTransition('expireawaitingclient', 'awaitingclient', 'expired', \
            title='Expire')

        #Cancellation
        wfl.addTransition('canceldeposit', 'receiveddeposit', 'cancelled', \
            title='Cancel')
        wfl.addTransition('cancelfull', 'receivedfull', 'cancelled', \
            title='Cancel')

        wfl.put()
        
        wfl.setInitialState('temporary')
        wfl.createWorkFlowDict()
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
            entityState = 'awaitingagent', 
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
            entityState = 'allocated', 
            hours = 6)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityState = 'confirmed', 
            hours = 24)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityState = 'awaitingclient', 
            hours = 24)
        bcs.put()

        bcs = ExpirationSetting(
            parent=wfl,
            entityKind = 'Enquiry', 
            entityState = 'receiveddeposit', 
            hours = 72)
        bcs.put()

        return wfl

