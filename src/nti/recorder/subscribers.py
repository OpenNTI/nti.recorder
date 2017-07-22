#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from zope.security.management import queryInteraction

from ZODB.interfaces import IConnection

from nti.externalization.interfaces import IObjectModifiedFromExternalEvent

from nti.recorder.interfaces import IRecordable
from nti.recorder.interfaces import ITransactionRecordHistory

from nti.recorder.record import remove_transaction_history

from nti.recorder.utils import record_transaction


@component.adapter(IRecordable, IObjectModifiedFromExternalEvent)
def _record_modification(obj, event):
    # XXX: don't process if batch update or new object
    if queryInteraction() is None or IConnection(obj, None) is None:
        return
    history = ITransactionRecordHistory(obj)
    record_transaction(recordable=obj,
                       descriptions=event.descriptions,
                       ext_value=event.external_value,
                       history=history)


@component.adapter(IRecordable, IObjectRemovedEvent)
def _recordable_removed(obj, _):
    remove_transaction_history(obj)
