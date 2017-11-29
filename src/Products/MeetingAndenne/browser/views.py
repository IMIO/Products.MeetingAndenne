from zope.component import getMultiAdapter
from zope.annotation import IAnnotations

from persistent.mapping import PersistentMapping
from plone.memoize.instance import memoize
from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.MeetingFile import convertToImages
from plone.app.async.interfaces import IAsyncService
from collective.documentviewer.async import isConversion
from zope.component import getUtility
from collective.documentviewer.settings import Settings
from Products.MeetingAndenne.config import CRON_BATCH_SIZE

import logging
logger = logging.getLogger( 'MeetingAndenne' )


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


class RunDocsplitOnBlobsView(BrowserView):
    """
      This is a view that is called as a maintenance task by Products.cron4plone.
      As we use clear days to compute advice delays, it will be launched at 0:00
      each night and update relevant items containing delay-aware advices still addable/editable.
      It will also update the indexAdvisers portal_catalog index.
    """
    def __call__(self):
        logger.info('Looking to see if there are still some blobs to convert.(max %d)' % CRON_BATCH_SIZE)

        catalog = getToolByName(self.context, 'portal_catalog')
        types = ('MeetingFile', 'CourrierFile')
        cpt = 0
        date_range = {'query': (DateTime('2017-08-31 23:16:17'),),'range': 'max',}
        for type in types:
            if cpt >= CRON_BATCH_SIZE:
                break
             
            brains = catalog.queryCatalog({"meta_type":type,"created" : date_range})
            acpt=len(brains)
            qcpt = 1
            for brain in brains:
                object = brain.getObject()
                removeFlags = False
                queueObject = False
                annotations = IAnnotations(object)

                needsOcr = getattr(object, 'needsOcr', None)
                if needsOcr is None or needsOcr == False:
                    if hasattr(object, 'needsOcr'):
                        logger.info('Object has needsOcr = False : %s' % object.absolute_url())
                        delattr(object, 'needsOcr')
                    qcpt += 1
                    continue

                if not object.isConvertable():
                    logger.info('Object not convertable : %s' % object.absolute_url())
                    removeFlags = True
                else:
                    if not 'collective.documentviewer' in annotations:
                        queueObject = True
                    else:
                        results = annotations['collective.documentviewer']
                        if 'converting' in results and results['converting']:
                            if not 'Products.MeetingAndenne' in annotations:
                                annotations['Products.MeetingAndenne'] = PersistentMapping()
                            if 'converting' not in annotations['Products.MeetingAndenne']:
                                annotations['Products.MeetingAndenne']['converting'] = True
                                logger.warning('Object still under conversion : %s' % object.absolute_url())
                                cpt += 1
                                qcpt += 1
                                continue
                            else:
                                logger.warning('Object conversion stuck : %s' % object.absolute_url())
                                queueObject = True
                                if object.meta_type == 'MeetingFile' and 'toPrint' in annotations['Products.MeetingAndenne']:
                                    object.toPrint = annotations['Products.MeetingAndenne']['toPrint']
                                if 'stuckCount' not in annotations['Products.MeetingAndenne']:
                                    annotations['Products.MeetingAndenne']['stuckCount'] = 1
                                else:
                                    stuckCount = annotations['Products.MeetingAndenne']['stuckCount'] + 1
                                    if stuckCount <= 3:
                                        annotations['Products.MeetingAndenne']['stuckCount'] = stuckCount
                                    else:
                                        logger.error('Object not convertable after three trials : %s' % object.absolute_url())
                                        object.toPrint = False
                                        queueObject = False
                                        removeFlags = True
                        if 'successfully_converted' in results and results['successfully_converted']:
                            removeFlags = True
                        else:
                            if 'successfully_converted' in results:
                                logger.error('Object conversion failed : %s' % object.absolute_url())
                            queueObject = True
                            if object.meta_type == 'MeetingFile':
                                if 'Products.MeetingAndenne' in annotations and 'toPrint' in annotations['Products.MeetingAndenne']:
                                    object.toPrint = annotations['Products.MeetingAndenne']['toPrint']

                if removeFlags:
                    delattr(object, 'needsOcr')
                    if object.meta_type == 'MeetingFile' and 'Products.MeetingAndenne' in annotations:
                        del annotations['Products.MeetingAndenne']
                    continue

                if queueObject:
                    if object.meta_type == "MeetingFile":
                        if not 'Products.MeetingAndenne' in annotations:
                            annotations['Products.MeetingAndenne'] = PersistentMapping()
                            annotations['Products.MeetingAndenne']['toPrint'] = object.toPrint
                    
                    convertToImages(object, None, force=True)
                    logger.info('Object number %d queued on %d %s' %(qcpt,acpt,type))
                    cpt += 1
                    if cpt >= CRON_BATCH_SIZE:
                        break
                qcpt +=1
        logger.info('Added %d jobs in conversion queue' % cpt)

class RunDocsplitdelete(BrowserView):
    """
      This is a view that is called as a maintenance task by Products.cron4plone.
      As we use clear days to compute advice delays, it will be launched at 0:00
      each night and update relevant items containing delay-aware advices still addable/editable.
      It will also update the indexAdvisers portal_catalog index.
    """
    def __call__(self):
        logger.info('Looking to see if there are  some items to delete in conversion queue.')
        catalog = getToolByName(self.context, 'portal_catalog')
        types = ('MeetingFile', 'CourrierFile')
        cpt = 0
        sitepath = self.context.getPhysicalPath()
        async = getUtility(IAsyncService)
        queue = async.getQueues()['']
        date_range = {'query': (DateTime('2017-08-31 23:16:17'),),'range': 'max',}
        for type in types:
                         
            brains = catalog.queryCatalog({"meta_type":type,"created" : date_range})
            acpt=len(brains)
            qcpt = 1
            for brain in brains:
                if cpt >= 10:
                        break
                object = brain.getObject()
                removeFlags = False
                queueObject = False
                annotations = IAnnotations(object)
                objpath = object.getPhysicalPath()            
                if not object.isConvertable():
                    logger.info('Object not convertable : %s' % object.absolute_url())
                    removeFlags = True
                else:
                    if not 'collective.documentviewer' in annotations:
                        continue
                    else:
                        results = annotations['collective.documentviewer']
                        if 'converting' in results and results['converting']:                    
                            # find the job		    
                            jobs = [job for job in queue]
                            for job in jobs:
                                if isConversion(job, sitepath) and \
                                        job.args[0] == objpath and job.args[3]=='admin':
                                    try:
                                        queue.remove(job)
                                        settings = Settings(object)
                                        settings.converting = False
                                        cpt +=1
                                        logger.info('remove from queue : %s in state %s ' % (job.args,job.status))
                                    except LookupError:
                                        pass                   
                    
        logger.info('%d item deleted in queue ' % cpt)

