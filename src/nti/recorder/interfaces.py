#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IObjectEvent

from zope.location.interfaces import IContained

from nti.base.interfaces import ICreated
from nti.base.interfaces import ILastModified

from nti.schema.field import Bool
from nti.schema.field import Object
from nti.schema.field import TextLine
from nti.schema.field import IndexedIterable

TRX_RECORD_HISTORY_KEY = 'nti.recorder.record.TransactionRecordHistory'

#: Created Transaction type
TRX_TYPE_CREATE = 'create'

#: Updated Transaction type
TRX_TYPE_UPDATE = 'update'

#: Imported Transaction type
TRX_TYPE_IMPORT = 'import'


class IRecordable(interface.Interface):
    """
    A marker interface for objects whose changes are to be recorded
    """
    locked = Bool("If this object is locked.", default=False, required=False)
    locked.setTaggedValue('_ext_excluded_out', True)

    def lock(event=True):
        """
        lock this object

        :param event: Notify lock event
        """

    def unlock(event=True):
        """
        unlock this object

        :param event: Notify unlock event
        """

    def isLocked():
        """
        return if this object is locked
        """
    is_locked = isLocked


class IRecordableContainer(IRecordable):
    """
    A marker interface for `IRecordable` container objects.
    """
    child_order_locked = Bool(title="If this children order/set of this container are locked.",
                              default=False, required=False)
    child_order_locked.setTaggedValue('_ext_excluded_out', True)

    def child_order_lock(event=True):
        """
        child order lock this object

        :param event: Notify lock event
        """
    childOrderLock = child_order_lock

    def child_order_unlock(event=True):
        """
        child order unlock this object

        :param event: Notify unlock event
        """
    childOrderUnlock = child_order_unlock

    def is_child_order_locked():
        """
        return if this object is child order locked
        """
    isChildOrderLocked = is_child_order_locked


class ITransactionRecord(IContained, ICreated, ILastModified):
    tid = TextLine(title="The transaction/serial id", required=False)

    type = TextLine(title="The transaction type",
                    required=False,
                    default=TRX_TYPE_UPDATE)

    principal = TextLine(title="The principal id", required=True)

    attributes = IndexedIterable(title="The modifed attributes",
                                 value_type=TextLine(
                                     title="The attribute name"),
                                 min_length=0,
                                 unique=True)

    external_value = Object(interface.Interface,
                            title="External value",
                            required=False)
    external_value.setTaggedValue('_ext_excluded_out', True)

    key = interface.Attribute('record key')
    key.setTaggedValue('_ext_excluded_out', True)


class ITransactionRecordHistory(IContained):

    def add(record):
        pass

    def extend(records):
        pass

    def remove(record):
        pass

    def clear(event=True):
        pass

    def records():
        pass

    def query(self, tid=None, principal=None, record_type=None,
              start_time=None, end_time=None):
        """
        Query the transaction history for record(s) matching
        the given filters.
        """

class IObjectLockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been locked
    """


class IObjectUnlockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been unlocked
    """


@interface.implementer(IObjectLockedEvent)
class ObjectLockedEvent(ObjectEvent):
    pass


@interface.implementer(IObjectUnlockedEvent)
class ObjectUnlockedEvent(ObjectEvent):
    pass


class IObjectChildOrderLockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been child-order-locked
    """


class IObjectChildOrderUnlockedEvent(IObjectEvent):
    """
    An event that is sent, when an object has been child-order-unlocked
    """


@interface.implementer(IObjectChildOrderLockedEvent)
class ObjectChildOrderLockedEvent(ObjectEvent):
    pass


@interface.implementer(IObjectChildOrderUnlockedEvent)
class ObjectChildOrderUnlockedEvent(ObjectEvent):
    pass
