# encoding: utf-8

import math

from zope.interface import implements
from collections import OrderedDict
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.Archetypes.interfaces import IVocabulary


# ------------------------------------------------------------------------------
# Vocabulary used for Sub Categories treeWidget
class SubCategoriesVocabulary(object):

    implements(IVocabulary)
    security = ClassSecurityInfo()

    security.declarePrivate('getVocabularyDict')
    def getVocabularyDict(self, instance):
        """ returns the vocabulary as a dictionary with a string key and a
            string value. If it is not a flat vocabulary, the value is a
            tuple with a string and a sub-dictionary with the same format
            (or None if its a leaf).

            The instance of the content is given as parameter.
        """
        terms = OrderedDict()
        tree = OrderedDict()
        res = []
        cfg = instance.portal_plonemeeting.getMeetingConfig(instance)

        for cat in cfg.getCategories():
            try:
                catnum = int(cat.id.split('-')[0])
            except ValueError:
                catnum = 0
            if catnum >= 100:
                res.append(cat.id)
                catname = cat.getName()
                catnum = str(int(math.floor(catnum / 100)) * 100)
                if catnum in terms:
                    terms[catnum][1].update( {cat.id: [catname.split('.')[0] + '.' + catname.split('>')[1], None]} )
                else:
                    terms[catnum] = [catname.split('>')[0], OrderedDict( [(cat.id, [catname.split('.')[0] + '.' + catname.split('>')[1], None] )] )]

        # make sure current category is listed
        if instance.getCategory() and not instance.getCategory() in res:
            current_cat = instance.getCategory(theObject=True)
            tree[current_cat.id] = [current_cat.getName(), None]

        for key, value in terms.iteritems():
            if len(value[1]) == 1:
                tree[value[1].keys()[0]] = [value[0], None]
            else:
                tree[key] = value

        return tree


# ------------------------------------------------------------------------------
InitializeClass(SubCategoriesVocabulary)
# ------------------------------------------------------------------------------
