#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.event import notify

from nti.recorder.interfaces import IRecordable
from nti.recorder.interfaces import IRecordableContainer

from nti.recorder.interfaces import ObjectLockedEvent
from nti.recorder.interfaces import ObjectUnlockedEvent
from nti.recorder.interfaces import ObjectChildOrderLockedEvent
from nti.recorder.interfaces import ObjectChildOrderUnlockedEvent

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IRecordable)
class RecordableMixin(object):

    locked = False

    def __init__(self, *args, **kwargs):
        super(RecordableMixin, self).__init__(*args, **kwargs)

    def lock(self, event=True, **unused_kwargs):
        self.locked = True
        if event:
            notify(ObjectLockedEvent(self))

    def unlock(self, event=True, **unused_kwargs):
        self.locked = False
        if event:
            notify(ObjectUnlockedEvent(self))

    def isLocked(self):
        return self.locked
    is_locked = isLocked


@interface.implementer(IRecordableContainer)
class RecordableContainerMixin(RecordableMixin):

    child_order_locked = False

    def __init__(self, *args, **kwargs):
        super(RecordableContainerMixin, self).__init__(*args, **kwargs)

    def child_order_lock(self, event=True, **unused_kwargs):
        self.child_order_locked = True
        if event:
            notify(ObjectChildOrderLockedEvent(self))
    childOrderLock = child_order_lock

    def child_order_unlock(self, event=True, **unused_kwargs):
        self.child_order_locked = False
        if event:
            notify(ObjectChildOrderUnlockedEvent(self))
    childOrderUnlock = child_order_unlock

    def is_child_order_locked(self):
        return self.child_order_locked
    isChildOrderLocked = is_child_order_locked
