#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from ZODB.interfaces import IConnection

from zope import component

from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from zope.security.management import queryInteraction

from nti.externalization.interfaces import IObjectModifiedFromExternalEvent

from nti.recorder.interfaces import IRecordable
from nti.recorder.interfaces import ITransactionRecordHistory

from nti.recorder.record import remove_transaction_history

from nti.recorder.utils import record_transaction

logger = __import__('logging').getLogger(__name__)


def disallow_recording(obj):
    return queryInteraction() is None or IConnection(obj, None) is None


@component.adapter(IRecordable, IObjectModifiedFromExternalEvent)
def _record_modification(obj, event):
    # don't process if batch update or new object
    if disallow_recording(obj):
        return
    history = ITransactionRecordHistory(obj)
    record_transaction(recordable=obj,
                       descriptions=event.descriptions,
                       ext_value=event.external_value,
                       history=history)


@component.adapter(IRecordable, IObjectRemovedEvent)
def _recordable_removed(obj, unused_event=None):
    remove_transaction_history(obj)
