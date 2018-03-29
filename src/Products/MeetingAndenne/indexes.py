# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from Products.CMFPlone.CatalogTool import zero_fill, num_sort_regex
from Products.CMFPlone.utils import safe_callable, safe_unicode

from Products.MeetingAndenne.interfaces import ICourrierFile
from Products.PloneMeeting.interfaces import IMeetingItem

MAX_SORTABLE_SENDER = 40


@indexer(ICourrierFile)
def sortable_sender(obj):
    """
      Helper method used to provide a FieldIndex for destOrigin field
      in CourrierFile objects
    """
    sender = getattr(obj, 'getDestOrigin', None)
    if sender is not None:
        if safe_callable(sender):
            sender = sender()

        if isinstance(sender, basestring):
            # Ignore case, normalize accents, strip spaces
            sortablesender = mapUnicode(safe_unicode(sender)).lower().strip()
            # Replace numbers with zero filled numbers
            sortablesender = num_sort_regex.sub(zero_fill, sortablesender)
            # Truncate to prevent bloat, take bits from start and end
            if len(sortablesender) > MAX_SORTABLE_SENDER:
                start = sortablesender[:(MAX_SORTABLE_SENDER - 13)]
                end = sortablesender[-10:]
                sortablesender = start + '...' + end
            return sortablesender.encode('utf-8')
    return ''

@indexer(IMeetingItem)
def reviewProcessInfo(obj):
    """
      Compute a reviewProcessInfo, this concatenate the proposingGroup
      and the item review_state so it can be queryable in the catalog.
    """
    state = obj.queryState()
    catNum = obj.getCategory(theObject=True).adapted().getRootCatNum()
    if catNum in [4300, 45] and state == 'proposed':
        proposingGroup = 'personnel'
    else:
        proposingGroup = obj.getProposingGroup()
    return '%s__reviewprocess__%s' % (proposingGroup, state)
