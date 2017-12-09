#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_key
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from zope import interface

from zope.annotation.interfaces import IAttributeAnnotatable

from zope.location.interfaces import IContained

from nti.externalization.internalization import find_factory_for
from nti.externalization.externalization import to_external_object
from nti.externalization.internalization import update_from_external_object

from nti.recorder.interfaces import ITransactionRecord

from nti.recorder.mixins import RecordableMixin

from nti.recorder.record import TransactionRecord

from nti.recorder.record import get_transactions
from nti.recorder.record import has_transactions
from nti.recorder.record import copy_transaction_history

from nti.recorder.utils import record_transaction

from nti.recorder.tests import SharedConfiguringTestLayer


class TestRecord(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_record(self):
        assert_that(TransactionRecord(),
                    verifiably_provides(ITransactionRecord))
        ichigo = TransactionRecord(tid=u'a',
                                   principal=u'ichigo',
                                   attributes=(u'shikai',))
        assert_that(ichigo,
                    validly_provides(ITransactionRecord))

        ext = to_external_object(ichigo)
        assert_that(ext, has_entry('Class', is_('TransactionRecord')))
        assert_that(ext, has_entry('principal', is_('ichigo')))
        assert_that(ext, has_entry('CreatedTime', is_not(none())))
        assert_that(ext, has_entry('attributes', is_(['shikai'])))
        assert_that(ext, has_entry('tid', is_('a')))
        assert_that(ext, does_not(has_key('key')))
        assert_that(ext, has_entry('MimeType',
                                   is_('application/vnd.nextthought.recorder.transactionrecord')))

        factory = find_factory_for(ext)
        assert_that(factory, is_not(none()))
        obj = factory()
        update_from_external_object(obj, ext)
        assert_that(obj, has_property('tid', is_('a')))
        assert_that(obj, has_property('attributes', is_(['shikai'])))
        assert_that(obj, has_property('principal', is_('ichigo')))

        aizen = TransactionRecord(tid=u'b',
                                  principal=u'aizen',
                                  attributes=(u'bankai',))

        assert_that(sorted([aizen, ichigo]),
                    is_([ichigo, aizen]))
    
        assert_that(aizen.__gt__(ichigo), is_(True))

    def test_copy_records(self):

        @interface.implementer(IAttributeAnnotatable, IContained)
        class R(RecordableMixin):
            __parent__ = __name__ = None

        source = R()
        target = R()
        assert_that(get_transactions(source), is_([]))
        assert_that(copy_transaction_history(source, target),
                    is_(0))
        record_transaction(source, u'ichigo', type_=u'Shikai')
        assert_that(copy_transaction_history(source, target),
                    is_(1))

        assert_that(has_transactions(source), is_(False))
        assert_that(has_transactions(target), is_(True))
