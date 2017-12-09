#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods,arguments-differ

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

import unittest

from zope import interface

from zope.annotation.interfaces import IAttributeAnnotatable

from persistent.persistence import Persistent

from nti.externalization.persistence import NoPickle

from nti.recorder.interfaces import ITransactionRecordHistory

from nti.recorder.mixins import RecordableMixin

from nti.recorder.record import copy_records
from nti.recorder.record import get_transactions

from nti.recorder.utils import txn_id
from nti.recorder.utils import compress
from nti.recorder.utils import decompress
from nti.recorder.utils import is_created
from nti.recorder.utils import current_principal
from nti.recorder.utils import record_transaction

from nti.recorder.tests import SharedConfiguringTestLayer


@interface.implementer(IAttributeAnnotatable)
class Recordable(Persistent, RecordableMixin):
    locked = False

    def lock(self):
        self.locked = True


class TestSubscriber(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_record_trax(self):
        recordable = Recordable()
        assert_that(recordable, has_property('locked', is_(False)))

        record = record_transaction(recordable, principal=u"ichigo",
                                    descriptions=(u'a',),
                                    ext_value={u"a": u"b"})

        assert_that(record, is_not(none()))
        assert_that(record, has_property('attributes', is_(('a',))))
        assert_that(record, has_property('principal', is_("ichigo")))
        assert_that(record, has_property('type', is_("update")))
        assert_that(record, has_property('external_value', is_not(none())))

        ext_value = decompress(record.external_value)
        assert_that(ext_value, is_({u"a": u"b"}))

        # we are locked
        assert_that(recordable, has_property('locked', is_(True)))

        # we have history
        records = get_transactions(recordable)
        assert_that(records, has_length(1))

        # No useful attributes in an update means we will not record tx.
        record = record_transaction(recordable, principal=u'aizen',
                                    descriptions=(u'MimeType',))
        assert_that(record, none())

        # No username
        record = record_transaction(recordable, principal=None, type_=u'create')
        assert_that(record, none())

        records = get_transactions(recordable)
        assert_that(records, has_length(1))

        record = record_transaction(recordable, principal=u'aizen',
                                    type_=u'xyz',
                                    descriptions=((u'test_attribute',),),
                                    createdTime=100)
        assert_that(record, is_not(none()))
        assert_that(record, has_property('type', is_('xyz')))
        assert_that(record, has_property('tid', is_(txn_id())))

        records = get_transactions(recordable)
        assert_that(records, has_length(2))

        other = Recordable()
        copy_records(other, records)
        records = get_transactions(other)
        assert_that(records, has_length(2))

        assert_that(is_created(other), is_(False))
        assert_that(is_created(None), is_(False))
        
        class Fake(object):
            locked = False
        fake = Fake()
        record = record_transaction(fake, principal=u'aizen',
                                    type_=u'coverage',
                                    descriptions=u'a',
                                    history=ITransactionRecordHistory(recordable))
        assert_that(fake, has_property('locked', is_(True)))

    def test_current_principal(self):
        assert_that(current_principal(False), is_(none()))

    def test_compress(self):
        @NoPickle
        class Foo(object):
            pass
        assert_that(compress(Foo()), is_(none()))
