#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import has_length
from hamcrest import assert_that

import unittest

from zope import component
from zope import interface

from nti.recorder.interfaces import IRecordables
from nti.recorder.interfaces import get_recordables

from nti.recorder.mixins import RecordableMixin


@interface.implementer(IRecordables)
class FakeRecordables(object):

    def iter_objects(self):
        return (RecordableMixin(),)


class TestInterfaces(unittest.TestCase):

    def test_get_recordables(self):
        recordables = FakeRecordables()
        component.getGlobalSiteManager().registerUtility(recordables, IRecordables)
        assert_that(list(get_recordables()),
                    has_length(1))
        component.getGlobalSiteManager().unregisterUtility(recordables, IRecordables)
