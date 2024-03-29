#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import zlib
from io import BytesIO

import six
from six.moves import cPickle as pickle

import transaction
try:
    from transaction._compat import get_thread_ident
except ImportError:  # pragma: no cover
    def get_thread_ident():
        return id(transaction.get())

from ZODB.utils import serial_repr

from zope import lifecycleevent

from zope.security.interfaces import NoInteraction

from zope.security.management import getInteraction

from zope.security.management import system_user

from nti.externalization.externalization import isSyntheticKey

from nti.externalization.interfaces import StandardExternalFields

from nti.recorder.interfaces import TRX_TYPE_CREATE
from nti.recorder.interfaces import TRX_TYPE_UPDATE

from nti.recorder.interfaces import IRecordable
from nti.recorder.interfaces import ITransactionRecordHistory

from nti.recorder.record import TransactionRecord

ITEMS = StandardExternalFields.ITEMS
MIMETYPE = StandardExternalFields.MIMETYPE

logger = __import__('logging').getLogger(__name__)


def current_principal(system=True):
    try:
        result = getInteraction().participations[0].principal
    except (NoInteraction, IndexError, AttributeError):
        result = system_user if system else None
    return result
principal = currentPrincipal = current_principal  # BWC


def compress(obj):
    # pylint: disable=unused-variable,broad-except
    __traceback_info__ = obj
    try:
        bio = BytesIO()
        pickle.dump(obj, bio)
        bio.seek(0)
        result = zlib.compress(bio.read())
        return result
    except Exception:  # seen in tests
        logger.exception("Cannot pickle/compress external object")
        return None


def decompress(source):
    data = zlib.decompress(source)
    bio = BytesIO(data)
    bio.seek(0)
    result = pickle.load(bio)
    return result


def is_created(obj):
    history = ITransactionRecordHistory(obj, None)
    if history is not None:
        records = history.query(record_type=TRX_TYPE_CREATE)
        return bool(records)
    return False


def txn_id():
    return u"txn.%s" % get_thread_ident()


def get_attributes(descriptions):
    if      descriptions is not None \
        and not isinstance(descriptions, (tuple, list, set)):
        descriptions = (descriptions,)

    result = set()

    def _accum(vals):
        # Exclude synthetic keys, including mimetype.
        for val in vals:
            if      val \
                and (val == ITEMS or not isSyntheticKey(val)) \
                and val.lower() != MIMETYPE.lower():
                result.add(val)

    for a in descriptions or ():
        if hasattr(a, 'attributes'):
            _accum(a.attributes or ())
        elif isinstance(a, (tuple, list, set)):
            _accum(a)
        else:
            _accum((a,))
    return result
_get_attributes = get_attributes # BWC


# pylint: disable=redefined-outer-name
def record_transaction(recordable, principal=None, descriptions=(),
                       ext_value=None, type_=TRX_TYPE_UPDATE, history=None,
                       lock=True, createdTime=None):
    # pylint: disable=unused-variable
    __traceback_info__ = recordable, principal, ext_value
    attributes = get_attributes(descriptions)
    if not attributes and type_ == TRX_TYPE_UPDATE:
        # Take care not to record anything that's not an actual edit.
        return

    if history is None:
        history = ITransactionRecordHistory(recordable)

    tid = getattr(recordable, '_p_serial', None)
    tid = six.text_type(serial_repr(tid)) if tid else txn_id()
    tid = txn_id() if tid == u'0x00' else tid  # new object

    principal = current_principal(False) if principal is None else principal
    username = (   getattr(principal, 'id', None)
                or getattr(principal, 'usernane', None)
                or principal)

    if username is None:
        return  # tests

    # create record
    ext_value = compress(ext_value) if ext_value is not None else None
    record = TransactionRecord(principal=username, type=type_, tid=tid,
                               attributes=tuple(attributes),
                               external_value=ext_value)
    if createdTime is not None:
        record.lastModified = record.createdTime = createdTime

    lifecycleevent.created(record)
    history.add(record)
    if lock:
        if IRecordable.providedBy(recordable):
            recordable.lock()
        else:
            recordable.locked = True
    return record
recordTransaction = record_trax = record_transaction
