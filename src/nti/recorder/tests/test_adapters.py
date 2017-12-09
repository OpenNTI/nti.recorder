#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods
# pylint: disable=too-many-function-args

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from zope import interface

from zope.annotation.interfaces import IAttributeAnnotatable

from persistent.persistence import Persistent

from nti.base._compat import text_

from nti.recorder.adapters import NoOpTransactionRecordContainer

from nti.recorder.interfaces import TRX_TYPE_UPDATE

from nti.recorder.interfaces import ITransactionManager
from nti.recorder.interfaces import ITransactionRecordHistory

from nti.recorder.mixins import RecordableMixin

from nti.recorder.record import copy_records
from nti.recorder.record import append_records
from nti.recorder.record import remove_history
from nti.recorder.record import get_transactions
from nti.recorder.record import has_transactions
from nti.recorder.record import TransactionRecord

from nti.recorder.tests import SharedConfiguringTestLayer


@interface.implementer(IAttributeAnnotatable)
class Recordable(Persistent, RecordableMixin):
    pass


class TestAdapters(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_adapter(self):
        f = Recordable()
        history = ITransactionRecordHistory(f, None)
        assert_that(history, is_not(none()))
        assert_that(history, has_length(0))
        assert_that(history, has_property('__parent__', is_(f)))
        assert_that(bool(history), is_(False))
        record = TransactionRecord(tid=u'a',
                                   principal=u'ichigo',
                                   attributes=(u'shikai',))
        history.add(record)
        assert_that(history, has_length(1))
        assert_that(bool(history), is_(True))
        assert_that(list(history.records()), is_([record]))
        assert_that(record,
                    has_property('__parent__', is_(history)))

        assert_that(list(history.sublocations()),
                    has_length(1))

        history.remove(record)
        assert_that(history, has_length(0))

        record = TransactionRecord(tid=u'b',
                                   principal=u'ichigo',
                                   attributes=(u'bankai',))
        history.add(record)

        r = history.clear(False)
        assert_that(r, is_(1))
        assert_that(history, has_length(0))
        
        append_records(f, record)
        assert_that(history, has_length(1))
        
    def test_manager(self):
        f = Recordable()
        manager = ITransactionManager(f, None)
        assert_that(manager,
                    validly_provides(ITransactionManager))
        
        assert_that(manager,
                    verifiably_provides(ITransactionManager))
 
    def test_funcs(self):
        f = Recordable()
        assert_that(has_transactions(f), is_(False))
        history = ITransactionRecordHistory(f)
        record = TransactionRecord(tid=u'a',
                                   principal=u'ichigo',
                                   attributes=(u'Recordable',))
        history.add(record)

        records = list(history.records())
        assert_that(records, has_length(1))
        assert_that(has_transactions(f), is_(True))

        trxs = get_transactions(f, True)
        assert_that(trxs, has_length(1))
        assert_that(trxs[0], is_(record))

        f2 = Recordable()
        copy_records(f2, records)
        assert_that(has_transactions(f2), is_(True))

        assert_that(remove_history(f), is_(1))
        assert_that(has_transactions(f), is_(False))
        assert_that(remove_history(f), is_(0))

    def test_query(self):
        f = Recordable()
        history = ITransactionRecordHistory(f, None)
        for x in range(5):
            current = (x + 1) * 5
            principal = u'ichigo' if x % 2 == 0 else u'aizen'
            record = TransactionRecord(tid=text_(str(x)),
                                       principal=principal,
                                       attributes=(u'bankai',))
            record.createdTime = record.lastModified = current
            history.add(record)

        assert_that(history.query(tid=u'0'), has_length(1))
        assert_that(history.query(principal=u'ichigo'), has_length(3))
        assert_that(history.query(principal=u'aizen'), has_length(2))
        assert_that(history.query(record_type=TRX_TYPE_UPDATE),
                    has_length(5))

        assert_that(history.query(start_time=10), has_length(4))
        assert_that(history.query(start_time=5, end_time=10), has_length(2))
        assert_that(history.query(end_time=7), has_length(1))

    def test_noop(self):
        parent = object()
        record = Recordable()
        container = NoOpTransactionRecordContainer()
        
        container.__parent__ = parent
        assert_that(container, has_property('object', is_(parent)))
        
        container.add(record)
        container.extend((record,))
        assert_that(container, has_length(0))
        
        container.remove(record)
        assert_that(container, has_length(0))
        container.clear()
        
        assert_that(container, has_length(0))
        assert_that(container.records(), is_(()))
        assert_that(container.query(), is_(()))
