#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_in
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

import fudge
import unittest

import BTrees

from zope import component

from nti.zope_catalog.interfaces import IMetadataCatalog

from nti.recorder.index import RECORDABLE_CATALOG_NAME
from nti.recorder.index import TRX_RECORD_CATALOG_NAME

from nti.recorder.index import get_recordables
from nti.recorder.index import get_transactions
from nti.recorder.index import create_recorder_catalog
from nti.recorder.index import install_recorder_catalog
from nti.recorder.index import create_transaction_catalog
from nti.recorder.index import install_transaction_catalog

from nti.recorder.index import MetadataRecorderCatalog
from nti.recorder.index import MetadataTransactionCatalog

from nti.recorder.mixins import RecordableMixin

from nti.recorder.record import TransactionRecord

from nti.recorder.tests import SharedConfiguringTestLayer


class TestIndex(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_get_recordables(self):
        recordable = RecordableMixin()
        recordable.lock()
        # test catalog
        catalog = create_recorder_catalog(family=BTrees.family64)
        assert_that(isinstance(catalog, MetadataRecorderCatalog),
                    is_(True))
        assert_that(catalog, has_length(3))
        # test index
        catalog.super_index_doc(1, recordable)
        uids = list(get_recordables(catalog=catalog))
        assert_that(uids, has_length(1))
        assert_that(1, is_in(uids))

    def test_get_trasanction(self):
        record = TransactionRecord(principal=u'ichigo',
                                   type=u'create',
                                   tid=u'tx123',
                                   attributes=(u'bankai',),
                                   external_value={u'name': u'tensa'})
        record.lastModified = record.createdTime = 100000
        # test catalog
        catalog = create_transaction_catalog(family=BTrees.family64)
        assert_that(isinstance(catalog, MetadataTransactionCatalog),
                    is_(True))
        assert_that(catalog, has_length(6))
        # text index
        catalog.super_index_doc(1, record)
        uids = list(get_transactions(catalog))
        assert_that(uids, has_length(1))
        assert_that(1, is_in(uids))

        uids = list(get_transactions(catalog=catalog))
        intids = fudge.Fake().provides('queryObject').returns(record)
        objs = list(get_transactions(catalog, intids))
        assert_that(objs, has_length(1))

    def test_install_recorder_catalog(self):
        intids = fudge.Fake().provides('register').has_attr(family=BTrees.family64)
        catalog = install_recorder_catalog(component, intids)
        assert_that(catalog, is_not(none()))
        assert_that(install_recorder_catalog(component, intids),
                    is_(catalog))
        component.getGlobalSiteManager().unregisterUtility(catalog, IMetadataCatalog,
                                                           RECORDABLE_CATALOG_NAME)

    def test_install_transaction_catalog(self):
        intids = fudge.Fake().provides('register').has_attr(family=BTrees.family64)
        catalog = install_transaction_catalog(component, intids)
        assert_that(catalog, is_not(none()))
        assert_that(install_transaction_catalog(component, intids),
                    is_(catalog))
        component.getGlobalSiteManager().unregisterUtility(catalog, IMetadataCatalog,
                                                           TRX_RECORD_CATALOG_NAME)
