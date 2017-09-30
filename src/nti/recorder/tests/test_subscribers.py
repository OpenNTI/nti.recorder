#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that

import fudge
import unittest

from zope import interface
from zope import lifecycleevent

from zope.annotation.interfaces import IAttributeAnnotatable

from zope.location.interfaces import IContained

from nti.externalization.internalization import notifyModified

from nti.recorder.interfaces import ITransactionRecordHistory

from nti.recorder.mixins import RecordableMixin

from nti.recorder.subscribers import disallow_recording

from nti.recorder.tests import SharedConfiguringTestLayer


class TestSubscribers(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_disallow_recording(self):
        assert_that(disallow_recording(None), is_(True))

    @fudge.patch('nti.recorder.subscribers.disallow_recording',
                 'nti.recorder.utils.current_principal')
    def test_record_modification(self, mock_dr, mock_cp):
        mock_dr.is_callable().with_args().returns(True)

        @interface.implementer(IAttributeAnnotatable, IContained)
        class R(RecordableMixin):
            __parent__ = __name__ = None
        recordable = R()

        notifyModified(recordable, {u'key': u'value'})
        history = ITransactionRecordHistory(recordable)
        assert_that(history, has_length(0))

        mock_dr.is_callable().with_args().returns(False)
        mock_cp.is_callable().with_args().returns('ichigo')

        notifyModified(recordable, {u'key': u'value'})
        history = ITransactionRecordHistory(recordable)
        assert_that(history, has_length(1))

        lifecycleevent.removed(recordable)
        history = ITransactionRecordHistory(recordable)
        assert_that(history, has_length(0))
