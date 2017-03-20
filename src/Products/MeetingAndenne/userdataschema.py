# -*- coding: utf-8 -*-
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import implements
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("PloneMeeting")

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
