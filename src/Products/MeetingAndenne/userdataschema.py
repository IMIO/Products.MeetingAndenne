# -*- coding: utf-8 -*-
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema
from Products.CMFCore.utils import getToolByName
from Products.MeetingAndenne.utils import collateDisplayListsValues
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
from zope import schema
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from Products.CMFPlone import PloneMessageFactory as _

gender_options = SimpleVocabulary([
    SimpleTerm( value = 'homme', title = _(u'Male') ),
    SimpleTerm( value = 'femme', title = _(u'Female') ),
    ]) 


class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema

def possibleOrganizers(context):
    acl_users = api.portal.get_tool(name='acl_users')   
    group = acl_users.getGroupById('informatique_creators')
    terms = []

    if group is not None:
        for member_id in group.getMemberIds():
            user = acl_users.getUserById(member_id)
            if user is not None:
                member_name = user.getProperty('fullname') or member_id
                terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

    return SimpleVocabulary(terms)


def listProposingGroups(context):
        tool = api.portal.get_tool(name='portal_plonemeeting')   
        isDefinedInTool = True     
        terms = []   
        res = tool.getSelectableGroups(isDefinedInTool=isDefinedInTool)
        res = sorted(res, key=collateDisplayListsValues)
        for group in res:
            terms.append(SimpleVocabulary.createTerm(group[0], str(group[0]), unicode(group[1],'utf8')))

        return SimpleVocabulary(terms)
   
directlyProvides(listProposingGroups, IContextSourceBinder)

#defaultgroup_options=listProposingGroups()
class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """
        

    gender = schema.Choice(
        title = _(u'label_gender', default = u'Gender'),
        description = _(u'help_gender',
                        default = u"Your gender"),
        vocabulary = gender_options,
        required = False,
        )
    function = schema.TextLine(
        title = _(u'label_function', default = u'Function'),
        description = _(u'help_function',
                        default = u"Your function inside the company"),
        required = False,
        )
    defaultref = schema.TextLine(
        title = _(u'label_defaultref', default = u'Default Reference'),
        description = _(u'help_defaultref',
                        default = u"Your Default reference unsing new note"),
        required = False,
        )

    defaultgroup = schema.Choice(
        title = _(u'label_defaultgroup', default = u'Default Group'),
        description = _(u'help_defaultgroup',
                        default = u"Your Group when Proposing Group are multiple"),
        source=listProposingGroups,
        required = False,
        )