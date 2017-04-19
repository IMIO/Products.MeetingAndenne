from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView


class WelcomeUser(BrowserView):
    '''
      Manage the attendees deparatures for managing specific assembly members on each item of a meeting.
    '''
    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()
        self.userId = self.request.form.get('userId', '')
        self.welcomeType = self.request.form.get('welcomeType', '')
        self.canJoin = self.request.form.get('canJoin', False)

    def __call__(self):
        form = self.request.form
        submitted = form.get('form.buttons.save', False)
        cancelled = form.get('form.buttons.cancel', False)
        if submitted:
            if not self.userId:
                return self.request.RESPONSE.redirect(self.context.absolute_url())
            else:
                # welcome the user
                self.request.set('userId', self.userId)
                self.request.set('welcomeType', self.welcomeType)
                self.context.onWelcomePerson()
                self.request.RESPONSE.redirect(self.context.absolute_url())
        elif cancelled:
            # the only way to enter here is the popup overlay not to be shown
            # because while using the popup overlay, the jQ function take care of hidding it
            # while the Cancel button is hit
            self.request.response.redirect(form.get('form.HTTP_REFERER'))
        return self.index()
