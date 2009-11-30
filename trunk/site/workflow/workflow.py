# -*- coding: UTF-8 -*-
# Copyright (C) 2002 Thilo Ernst <Thilo.Ernst@dlr.de>
# Copyright (C) 2002-2004, 2006-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007 David Versmisse <david.versmisse@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The workflow module simplifies the task of writing workflow systems.

The development of a workflow system can be splitted in three steps:

 1. Define the workflow as a graph with the 'Workflow' class:

    1.1 Create an instance of the 'Workflow' class;

    1.2 Add to this instance the different states and optionally
        set the initial state;

    1.3 Add the transitions that let to go from one state to another.

 2. Define the objects that will follow the workflow:

    2.1 inherite from the 'WorkflowAware' class;

    2.2 introduce each object into the workflow with the 'enterWorkflow'
        method.

 3. Associate the application semantics to the workflow aware objects
    by implementing the 'onenter', 'onleave' and 'ontrans' methods.

    Examples of "application semantics" are:

    - change the security settings of an object so it becomes public or
      private;

    - send an email to a user or a mailing list;
"""

import sys
import logging
from datetime import datetime, timedelta
from google.appengine.ext import db

logger = logging.getLogger('Worlflow')

class WorkflowError(Exception):
    pass


class Workflow(db.Model):
    """This class is used to describe a workflow.

    Actually it's just a graph. A workflow has states (one of them
    is the initial state), and states have transitions that go to
    another state.
    """

    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    initialState = db.StringProperty()

    def addState(self, name, title=None):
        """Adds a new state.
        """
        state = State(parent=self, key_name=name)
        if title:
            state.title = title
        state.put()


    def findState(self, name):
        """Find existing state.
        """
        states = State.get_by_key_name([name], parent=self)
        if len(states) == 1:
            return states[0]

    def findTransition(self, name):
        """Find existing transition.
        """
        transitions = Transition.get_by_key_name([name], parent=self)
        if len(transitions) == 1:
            return transitions[0]

    def setInitialState(self, name):
        """Sets the default initial state.
        """
        if not self.findState(name):
            raise WorkflowError, "invalid initial state: '%s'" % name
        self.initialState = name
        self.put()


    def addTransition(self, name, state_from, state_to, title=None):
        """Adds a new transition.

        'state_from' and 'state_to' are respectively the origin
        and destination states of the transition.
        """
        state_from = self.findState(state_from)
        if not state_from:
            raise WorkflowError, "unregistered state: '%s'" % state_from
        state_to = self.findState(state_to)
        if not state_to:
            raise WorkflowError, "unregistered state: '%s'" % state_to
        transition = Transition(parent=self, 
            key_name=name, stateFrom=state_from, stateTo=state_to)
        if title:
            transition.title = title
        transition.put()
        #state_from.addTransition(name, transition)
        #state_from.put()



class State(db.Expando):
    """This class is used to describe a state.

    An state has transitions to other states.
    """

    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()

    def addTransition(self, name, transition):
        """Adds a new transition.
        """
        self.transitions_from.append(transition)


class Transition(db.Expando):
    """This class is used to describe transitions.

    Transitions come from one state and go to another.
    """

    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    stateFrom = db.ReferenceProperty(State, collection_name='transitions_from')
    stateTo = db.ReferenceProperty(State, collection_name='transitions_to')


class WorkflowAware(db.Model):
    """Mixin class to be used for workflow aware objects.

    The instances of a class that inherits from WorkflowAware can be
    "within" the workflow, this means that they keep track of the
    current state of the object.

    Specific application semantics for states and transitions can be
    implemented as methods of the WorkflowAware-derived "developer
    class". These methods get associated with the individual
    states and transitions by a simple naming scheme. For example,
    if a workflow has two states 'private' and 'public', and a
    transition 'publish' that goes from 'private' to 'public',
    the following happens when the transition is executed:

      1. if implemented, the method 'onleave_private' is called
         (it is called each time the object leaves the 'private' state)

      2. if implemented, the method 'ontrans_publish' is called
         (it is called whenever this transition is executed)

      3. if implemented, the method 'onenter_public' is called
         (it is called each time the object enters the 'public' state)

    These state/transition "handlers" can also be passed arguments
    from the caller of the transition; for instance, in a web-based
    system it might be useful to have the HTTP request that triggered
    the current transition available in the handlers.

    A simple stack with three methods, 'pushdata', 'popdata' adn 'getdata',
    is implemented. It can be used, for example, to keep record of the states
    the object has been in.
    """

    workflow = db.ReferenceProperty(Workflow)
    workflowState = db.StringProperty()

    def enterWorkflow(self, workflow=None, initstate=None, *args, **kw):
        """[Re-]Bind this object to a specific workflow.

        If the 'workflow' parameter is omitted then the object associated
        workflow is kept. This lets, for example, to specify the associate
        workflow with a class varible instead of with an instance attribute.

        The 'initstate' parameter is the workflow state that should be
        taken on initially (if omitted or None, the workflow must provide
        a default initial state).

        Extra arguments args are passed to the enter-state handler (if any)
        of the initial state.
        """
        # Set the associated workflow
        if workflow is not None:
            self.workflow = workflow

        # Set the initial state
        if initstate is None:
            initstate = self.workflow.initialState

        if not initstate:
            raise WorkflowError, 'undefined initial state'

        if not self.workflow.findState(initstate):
            raise WorkflowError, "invalid initial state: '%s'" % initstate

        self.workflowState = initstate

        # Call app-specific enter-state handler for initial state, if any
        name = 'onenter_%s' % initstate
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

        #Set expiry date
        exp_date = ExpirationSetting.getExpirationDate(
            self.kind(),
            self.workflowState)
        self.expiryDate = exp_date

        self.put()


    def doTransition(self, transname, *args, **kw):
        """Performs a transition.

        Changes the state of the object and
        runs any defined state/transition handlers. Extra
        arguments are passed down to all handlers called.
        """
        # Get the workflow
        workflow = self.workflow

        # Get the transition
        transition = workflow.findTransition(transname)
        if not transition:
            error = "transition '%s' not in '%s'"
            raise WorkflowError, error % (transname, self.workflow.key().name())

        # Get the current state
        state = workflow.findState(self.workflowState)
        if transname not in [t.key().name() for t in state.transitions_from]:
            error = "transition '%s' is invalid from state '%s'"
            raise WorkflowError, error % (transname, self.workflowState)

        new_state = transition.stateTo

        # call app-specific leave- state  handler if any
        name = 'onleave_%s' % self.workflowState
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

        # Set the new state
        self.workflowState = new_state.key().name()

        # call app-specific transition handler if any
        name = 'ontransition_%s' % transname
        if hasattr(self, name):
            try:
                getattr(self, name)(*args, **kw)
            except:
                self.workflowState = state.key().name()
                msg = "Error '%s' occurred on transition"
                error = sys.exc_info()[1]
                raise WorkflowError, msg % (error)

        # call app-specific enter-state handler if any
        name = 'onenter_%s' % new_state.key().name()
        if hasattr(self, name):
            getattr(self, name)(*args, **kw)

        #Set expiry date
        exp_date = ExpirationSetting.getExpirationDate(
            self.kind(),
            self.workflowState,
            transname)
        self.expiryDate = exp_date

        self.put()


    def getStateName(self):
        """Return the name of the current state.
        """
        return self.workflowState


    def getState(self):
        """Returns the current state instance.
        """
        statename = self.getStateName()
        return self.workflow.findState(statename)

    def getPossibleTransitions(self):
        """Returns the list of transition from the current state
        """
        return self.getState().transitions_from

class ExpirationSetting(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty()
    entityKind = db.StringProperty() 
    entityState = db.StringProperty() 
    entityTransition = db.StringProperty() 
    hours = db.IntegerProperty(default=1) 

    @classmethod
    def getExpirationDate(cls, entityKind, entityState, entityTransition=None):
        setting = ExpirationSetting.all()
        setting.filter('entityKind =', entityKind)
        setting.filter('entityState =', entityState)
        if entityTransition:
            setting.filter('entityTransition =', entityTransition)
        records = setting.fetch(1)
        if records and records[0].hours >= 0:
            logger.info('Expire in %s hours time', records[0].hours)
            return datetime.now() + timedelta(hours=records[0].hours)

##    # Implements a stack that could be used to keep a record of the
##    # object way through the workflow.
##    # A tuple is used instead of a list so it will work nice with
##    # the ZODB.
##    workflow_history = ()


##    def pushdata(self, data):
##        """
##        Adds a new element to the top of the stack.
##        """
##        self.workflow_history = self.workflow_history + (data,)


##    def popdata(self):
##        """
##        Removes and returns the top stack element.
##        """
##        if len(self.workflow_history) == 0:
##            return None
##        data = self.workflow_history[-1]
##        self.workflow_history = self.workflow_history[:-1]
##        return data


##    def getdata(self):
##        """
##        Returns the data from the top element without removing it.
##        """
##        if len(self.workflow_history) == 0:
##            return None
##        return self.workflow_history[-1]


##class Token(WorkflowAware):
##    """
##    This class should be used when the document can be in different
##    states at the same time (likely states that belong to different
##    workflows).

##    In this situation the class shouldn't inherit from WorkflowAware,
##    instead it should contain as many tokens as needed, which would
##    be the ones that follow the workflow.
##    """
