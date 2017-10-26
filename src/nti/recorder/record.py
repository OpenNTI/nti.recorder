#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from functools import total_ordering

from zope import interface

from zope.cachedescriptors.property import readproperty

from zope.container.contained import Contained

from zope.deprecation import deprecated

from zope.mimetype.interfaces import IContentTypeAware

from persistent import Persistent

from nti.dublincore.datastructures import PersistentCreatedModDateTrackingObject

from nti.externalization.representation import WithRepr

from nti.recorder.interfaces import TRX_TYPE_UPDATE

from nti.recorder.interfaces import ITransactionRecord
from nti.recorder.interfaces import ITransactionManager
from nti.recorder.interfaces import ITransactionRecordHistory

from nti.property.property import alias

from nti.schema.eqhash import EqHash

from nti.schema.fieldproperty import createDirectFieldProperties

from nti.schema.schema import SchemaConfigured

logger = __import__('logging').getLogger(__name__)


@WithRepr
@total_ordering
@EqHash('principal', 'createdTime', 'tid')
@interface.implementer(ITransactionRecord, IContentTypeAware)
class TransactionRecord(PersistentCreatedModDateTrackingObject,
                        SchemaConfigured,
                        Contained):

    createDirectFieldProperties(ITransactionRecord)

    type = TRX_TYPE_UPDATE
    serial = alias('tid')
    username = alias('principal')

    parameters = {}  # IContentTypeAware

    def __init__(self, *args, **kwargs):
        SchemaConfigured.__init__(self, *args, **kwargs)
        PersistentCreatedModDateTrackingObject.__init__(self)

    @property
    def key(self):
        return "(%s,%s,%s)" % (self.createdTime, self.principal, self.tid)

    @readproperty
    def creator(self):
        return self.principal

    def __lt__(self, other):
        try:
            return (self.createdTime, self.principal) < (other.createdTime, other.principal)
        except AttributeError:  # pragma: no cover
            return NotImplemented

    def __gt__(self, other):
        try:
            return (self.createdTime, self.principal) > (other.createdTime, other.principal)
        except AttributeError:  # pragma: no cover
            return NotImplemented


deprecated('TransactionRecordHistory', 'No longer used')
class TransactionRecordHistory(Persistent, Contained):
    _records = ()


def has_transactions(obj):
    manager = ITransactionManager(obj, None)
    return manager is not None and manager.has_transactions()
hasTransactions = has_transactions


def get_transactions(obj, sort=False, descending=True):
    result = []
    history = ITransactionRecordHistory(obj, None)
    if history:
        result.extend(history.records())
    if sort:
        result.sort(reverse=descending)
    return result
getTransactions = get_transactions


def remove_transaction_history(obj):
    if has_transactions(obj):
        history = ITransactionRecordHistory(obj, None)
        return history.clear()
    return 0
removeTransactionHistory = remove_history = remove_transaction_history


def append_records(target, records=()):
    if ITransactionRecord.providedBy(records):
        records = (records,)
    history = ITransactionRecordHistory(target)
    history.extend(records)
    return len(records)
appendTransactions = append_transactions = append_records


def copy_transaction_history(source, target, clear=True):
    if not has_transactions(source):
        return 0
    source_history = ITransactionRecordHistory(source)
    records = list(source_history.records())
    append_records(target, records)
    if clear:
        source_history.clear(event=False)  # don't remove intids
    return len(records)
copyTransactionHistory = copy_history = copy_transaction_history


def copy_records(target, records=()):
    records = records or ()
    history = ITransactionRecordHistory(target)
    history.extend(records)
    return len(records)
copyRecords = copy_records
