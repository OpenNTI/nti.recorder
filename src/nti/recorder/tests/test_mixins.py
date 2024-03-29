#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property
does_not = is_not

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from nti.recorder.interfaces import IRecordable
from nti.recorder.interfaces import IRecordableContainer

from nti.recorder.mixins import RecordableMixin
from nti.recorder.mixins import RecordableContainerMixin

from nti.recorder.tests import SharedConfiguringTestLayer


class TestMixins(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_recordable(self):
        c = RecordableMixin()
        assert_that(c, has_property('locked', is_(False)))
        assert_that(c, validly_provides(IRecordable))
        assert_that(c, verifiably_provides(IRecordable))
        c.lock()
        assert_that(c, has_property('locked', is_(True)))
        assert_that(c.is_locked(), is_(True))
        c.unlock()
        assert_that(c, has_property('locked', is_(False)))

    def test_recordable_container(self):
        c = RecordableContainerMixin()
        assert_that(c, has_property('child_order_locked', is_(False)))
        assert_that(c, validly_provides(IRecordableContainer))
        assert_that(c, verifiably_provides(IRecordableContainer))
        c.child_order_lock()
        assert_that(c, has_property('child_order_locked', is_(True)))
        assert_that(c.is_child_order_locked(), is_(True))
        c.child_order_unlock()
        assert_that(c, has_property('child_order_locked', is_(False)))
