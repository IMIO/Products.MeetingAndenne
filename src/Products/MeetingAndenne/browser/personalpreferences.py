# -*- coding: utf-8 -*-
from plone.app.users.browser.personalpreferences import IPersonalPreferences
from plone.app.users.browser.personalpreferences import PersonalPreferencesPanel
from plone.app.users.browser.personalpreferences import LanguageWidget
from plone.app.users.browser.personalpreferences import WysiwygEditorWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.formlib import form

from Products.CMFPlone import PloneMessageFactory as _


class IEnhancedPersonalPreferences(IPersonalPreferences):
    """ Use all the fields from the default personal preferences and add various
        extra fields.
    """
    listed = schema.Bool(
        title = _(u'label_listed', default = u'Listed in searches'),
        description = _(u'help_listed',
                        default = u"Determines if your user name is listed in "
                                   "user searches done on this site."),
        required = False
        )


class EnhancedPersonalPreferencesPanel(PersonalPreferencesPanel):
    """
    """
    form_fields = form.FormFields(IEnhancedPersonalPreferences)
    # Apply same widget overrides as in the base class
    form_fields['language'].custom_widget = LanguageWidget
    form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget


class EnhancedPersonalPreferencesConfiglet(EnhancedPersonalPreferencesPanel):
    """
    """
    template = ViewPageTemplateFile('templates/account-configlet.pt')
