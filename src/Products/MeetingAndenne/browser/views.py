from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class MeetingAndenneMailTopicView(BrowserView):
    """
      This manage the view displaying list of items
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    @memoize
    def getTopicName(self):
        """
          Get the topicName from the request and returns it.
        """
        return self.request.get('search', None)

    @memoize
    def getPloneMeetingTool(self):
        '''Returns the tool.'''
        return getToolByName(self.portal, 'portal_plonemeeting')

    @memoize
    def getCurrentMeetingConfig(self):
        '''Returns the Courrierfake meetingConfig.'''
        tool = self.getPloneMeetingTool()
        res = tool.adapted().getCourrierfakeConfig()
        return res

    @memoize
    def getTopic(self):
        '''Return the concerned topic.'''
        return getattr(self.getCurrentMeetingConfig().topics, self.getTopicName())


class MeetingAndenneMailFolderView(BrowserView):
    """
      Manage the view to show to a user when entering the courrierfake meetingConfig in the application.
      Redirect to the correct mail_topic_view that use a specific topicId.
    """
    def __call__(self):
        '''
          Redirect to the right url.
        '''
        return self.request.RESPONSE.redirect(self.getFolderRedirectUrl())

    def getFolderRedirectUrl(self):
        """
          Return the link to redirect the user to.
          Either redirect to a folder_view or to the mail_topic_view with a given topicId.
        """
        tool = self.context.portal_plonemeeting
        default_view = tool.getMeetingConfig(self.context).getUserParam('meetingAppDefaultView', self.request)
        # find the topic that has been selected in the meetingConfig as the default view
        # as this kind of view is identified adding a 'topic_' at the beginning, we retrieve the
        # real view method removing the first 6 characters
        # check first if the wished default_view is available to current user...
        availableTopicIds = [topic.getId() for topic in self._getAvailableTopicsForCurrentUser()]
        topicId = default_view[6:]
        if not topicId in availableTopicIds:
            # the defined view is not useable by current user, take first available
            # from availableTopicIds or use 'searchallitems' if no availableTopicIds at all
            topicId = availableTopicIds and availableTopicIds[0] or 'searchmymails'
        return self.context.absolute_url() + '/mail_topic_view?search=%s' % topicId

    def _getAvailableTopicsForCurrentUser(self):
        """
          Returns a list of available topics for the current user
        """
        tool = self.context.portal_plonemeeting
        cfg = tool.getMeetingConfig(self.context)
        return cfg.getTopics('MeetingItem')
