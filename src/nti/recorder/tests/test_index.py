#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_in
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

import BTrees
import unittest

from nti.recorder.index import get_recordables
from nti.recorder.index import get_transactions
from nti.recorder.index import create_recorder_catalog
from nti.recorder.index import create_transaction_catalog

from nti.recorder.mixins import RecordableMixin

from nti.recorder.record import TransactionRecord

from nti.recorder.tests import SharedConfiguringTestLayer


class TestAdapters(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_get_recordables(self):
        recordable = RecordableMixin()
        recordable.lock()
        catalog = create_recorder_catalog(family=BTrees.family64)
        catalog.super_index_doc(1, recordable)
        uids = list(get_recordables(catalog=catalog))
        assert_that(uids, has_length(1))
        assert_that(1, is_in(uids))

    def test_get_trasanction(self):
        record = TransactionRecord(principal='ichigo', type='create',
                                   tid='tx123', 
                                   attributes=('bankai',),
                                   external_value={'name':'tensa'})
        record.lastModified = record.createdTime = 100000
        catalog = create_transaction_catalog(family=BTrees.family64)
        catalog.super_index_doc(1, record)
        uids = list(get_transactions(catalog=catalog))
        assert_that(uids, has_length(1))
        assert_that(1, is_in(uids))
