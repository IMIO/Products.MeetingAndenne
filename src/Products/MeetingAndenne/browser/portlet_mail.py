from zope.component import getMultiAdapter
from zope.interface import implements
from zope.formlib import form

from plone.memoize.instance import memoize
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('PloneMeeting')

class IMailPortlet(IPortletDataProvider):
    """ 
      A portlet that shows mail-specific topics
    """


class Assignment(base.Assignment):
    implements(IMailPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        return _(u"Mail")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('templates/portlet_mail.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    @property
    def available(self):
        """
          Defines if the portlet is available in the context
        """
        return True

    def render(self):
        return self._template()

    @memoize
    def getPloneMeetingTool(self):
        """
          Returns the portal_plonemeeting
        """
        return getToolByName(self.portal, 'portal_plonemeeting')


class AddForm(base.AddForm):
    form_fields = form.Fields(IMailPortlet)
    label = _(u"Add Mail Portlet")
    description = _(u"This portlet shows mails.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IMailPortlet)
    label = _(u"Edit Mail Portlet")
    description = _(u"This portlet shows mails.")
