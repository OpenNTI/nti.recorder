#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import component
from zope import interface

from zope.deprecation import deprecated

from zope.intid.interfaces import IIntIds

from zope.location import locate

from zope.mimetype.interfaces import IContentTypeAware

import BTrees

from nti.recorder.interfaces import IRecordable
from nti.recorder.interfaces import ITransactionRecord
from nti.recorder.interfaces import IRecordableContainer

from nti.traversal.location import find_interface

from nti.zope_catalog.catalog import Catalog

from nti.zope_catalog.datetime import TimestampToNormalized64BitIntNormalizer

from nti.zope_catalog.index import AttributeSetIndex
from nti.zope_catalog.index import AttributeValueIndex
from nti.zope_catalog.index import NormalizationWrapper
from nti.zope_catalog.index import IntegerAttributeIndex
from nti.zope_catalog.index import SetIndex as RawSetIndex
from nti.zope_catalog.index import ValueIndex as RawValueIndex
from nti.zope_catalog.index import IntegerValueIndex as RawIntegerValueIndex

from nti.zope_catalog.interfaces import IMetadataCatalog

from nti.zope_catalog.string import StringTokenNormalizer

RECORDABLE_CATALOG_NAME = 'nti.dataserver.++etc++recorder-catalog'
CATALOG_NAME = RECORDABLE_CATALOG_NAME  # BWC

TRX_RECORD_CATALOG_NAME = 'nti.dataserver.++etc++trxrecord-catalog'

#: Transaction ID index
IX_TID = 'tid'

#: Transaction type index
IX_TYPE = 'type'

#: Recordable object locked attribute index
IX_LOCKED = 'locked'

#: Recordable ID
IX_RECORDABLE = 'recordable'

#: Recordable container object child-order-locked attribute index
IX_CHILD_ORDER_LOCKED = 'childOrderLocked'

#: Recordable object MimeType
IX_MIMETYPE = 'mimeType'

#: Transaction attribute
IX_ATTRIBUTES = 'attributes'

#: Transaction time
IX_CREATEDTIME = 'createdTime'

#: Transaction principal
IX_USERNAME = IX_PRINCIPAL = 'principal'

logger = __import__('logging').getLogger(__name__)


deprecated('SiteIndex', 'No longer used')
class SiteIndex(RawSetIndex):
    pass


deprecated('TargetIntIDIndex', 'No longer used')
class TargetIntIDIndex(IntegerAttributeIndex):
    pass


# transactions


class ValidatingRecordableIntID(object):

    __slots__ = ('intid',)

    def __init__(self, obj, unused_default=None):
        if ITransactionRecord.providedBy(obj):
            source = find_interface(obj, IRecordable)
            intids = component.queryUtility(IIntIds)  # test mode
            if intids is not None and source is not None:
                self.intid = intids.queryId(source)

    def __reduce__(self):
        raise TypeError()


class RecordableIDIndex(IntegerAttributeIndex):
    default_field_name = 'intid'
    default_interface = ValidatingRecordableIntID


class PrincipalRawIndex(RawValueIndex):
    pass


def PrincipalIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name='principal',
                                interface=ITransactionRecord,
                                index=PrincipalRawIndex(family=family),
                                normalizer=StringTokenNormalizer())


class TIDIndex(AttributeValueIndex):
    default_field_name = 'tid'
    default_interface = ITransactionRecord


class TypeIndex(AttributeValueIndex):
    default_field_name = 'type'
    default_interface = ITransactionRecord


class AttributeSetIndex(AttributeSetIndex):
    default_field_name = 'attributes'
    default_interface = ITransactionRecord


class CreatedTimeRawIndex(RawIntegerValueIndex):
    pass


def CreatedTimeIndex(family=BTrees.family64):
    return NormalizationWrapper(field_name='createdTime',
                                interface=ITransactionRecord,
                                index=CreatedTimeRawIndex(family=family),
                                normalizer=TimestampToNormalized64BitIntNormalizer())


# recordables


class ValidatingMimeType(object):

    __slots__ = ('mimeType',)

    def __init__(self, obj, unused_default=None):
        if IRecordable.providedBy(obj):
            for source in (obj, IContentTypeAware(obj, None)):
                mimeType =  getattr(source, 'mimeType', None) \
                         or getattr(source, 'mime_type', None)
                if mimeType:
                    self.mimeType = mimeType
                    break

    def __reduce__(self):
        raise TypeError()


class MimeTypeIndex(AttributeValueIndex):
    default_field_name = 'mimeType'
    default_interface = ValidatingMimeType


class ValidatingLocked(object):

    __slots__ = ('locked',)

    def __init__(self, obj, unused_default=None):
        if IRecordable.providedBy(obj):
            self.locked = obj.isLocked()

    def __reduce__(self):
        raise TypeError()


class LockedIndex(AttributeValueIndex):
    field_name = default_field_name = 'locked'
    interface = default_interface = ValidatingLocked


class ValidatingChildOrderLocked(object):

    __slots__ = ('child_order_locked',)

    def __init__(self, obj, unused_default=None):
        if IRecordableContainer.providedBy(obj):
            self.child_order_locked = obj.isChildOrderLocked()

    def __reduce__(self):
        raise TypeError()


class ChildOrderLockedIndex(AttributeValueIndex):
    field_name = default_field_name = 'child_order_locked'
    interface = default_interface = ValidatingChildOrderLocked


@interface.implementer(IMetadataCatalog)
class MetadataRecorderCatalog(Catalog):

    super_index_doc = Catalog.index_doc

    def index_doc(self, docid, ob):
        pass

    def force_index_doc(self, docid, ob):
        self.super_index_doc(docid, ob)


def create_recorder_catalog(catalog=None, family=BTrees.family64):
    if catalog is None:
        catalog = MetadataRecorderCatalog(family=family)
    for name, clazz in ((IX_LOCKED, LockedIndex),
                        (IX_MIMETYPE, MimeTypeIndex),
                        (IX_CHILD_ORDER_LOCKED, ChildOrderLockedIndex)):
        index = clazz(family=family)
        locate(index, catalog, name)
        catalog[name] = index
    return catalog


def get_recorder_catalog(registry=component):
    return registry.queryUtility(IMetadataCatalog, name=RECORDABLE_CATALOG_NAME)
get_catalog = get_recorder_catalog


def install_recorder_catalog(site_manager_container, intids=None):
    lsm = site_manager_container.getSiteManager()
    intids = lsm.getUtility(IIntIds) if intids is None else intids
    catalog = get_recorder_catalog(registry=lsm)
    if catalog is not None:
        return catalog

    catalog = create_recorder_catalog(family=intids.family)
    locate(catalog, site_manager_container, RECORDABLE_CATALOG_NAME)
    intids.register(catalog)
    lsm.registerUtility(catalog,
                        provided=IMetadataCatalog,
                        name=RECORDABLE_CATALOG_NAME)

    for index in catalog.values():
        intids.register(index)
    return catalog


@interface.implementer(IMetadataCatalog)
class MetadataTransactionCatalog(Catalog):

    super_index_doc = Catalog.index_doc

    def index_doc(self, docid, ob):
        pass

    def force_index_doc(self, docid, ob):
        self.super_index_doc(docid, ob)


def get_transaction_catalog(registry=component):
    catalog = registry.queryUtility(IMetadataCatalog,
                                    name=TRX_RECORD_CATALOG_NAME)
    return catalog


def create_transaction_catalog(catalog=None, family=BTrees.family64):
    if catalog is None:
        catalog = MetadataTransactionCatalog(family=family)
    for name, clazz in ((IX_TID, TIDIndex),
                        (IX_TYPE, TypeIndex),
                        (IX_PRINCIPAL, PrincipalIndex),
                        (IX_ATTRIBUTES, AttributeSetIndex),
                        (IX_CREATEDTIME, CreatedTimeIndex),
                        (IX_RECORDABLE, RecordableIDIndex)):
        index = clazz(family=family)
        locate(index, catalog, name)
        catalog[name] = index
    return catalog


def install_transaction_catalog(site_manager_container, intids=None):
    lsm = site_manager_container.getSiteManager()
    intids = lsm.getUtility(IIntIds) if intids is None else intids
    catalog = get_transaction_catalog(registry=lsm)
    if catalog is not None:
        return catalog

    catalog = create_transaction_catalog(family=intids.family)
    locate(catalog, site_manager_container, TRX_RECORD_CATALOG_NAME)
    intids.register(catalog)
    lsm.registerUtility(catalog,
                        provided=IMetadataCatalog,
                        name=TRX_RECORD_CATALOG_NAME)

    for index in catalog.values():
        intids.register(index)
    return catalog


def get_objects(index, provided, catalog, intids=None):
    pivot_index = catalog[index]
    intids = component.queryUtility(IIntIds) if intids is None else intids
    for uid in set(pivot_index.documents_to_values.keys()):
        if intids is None:  # tests
            yield uid
        else:
            obj = intids.queryObject(uid)
            if provided.providedBy(obj):
                yield obj


def get_transactions(catalog=None, intids=None):
    """
    return the transaction records in the catalog
    """
    catalog = get_transaction_catalog() if catalog is None else catalog
    return get_objects(IX_TID, ITransactionRecord, catalog, intids)


def get_recordables(catalog=None, intids=None):
    """
    return the recordable objects in the catalog
    """
    catalog = get_recorder_catalog() if catalog is None else catalog
    return get_objects(IX_LOCKED, IRecordable, catalog, intids)
