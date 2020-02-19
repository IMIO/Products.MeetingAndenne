from zope.component import getMultiAdapter
from zope.annotation import IAnnotations

from persistent.mapping import PersistentMapping
from plone import api
from plone.memoize.instance import memoize
from DateTime import DateTime
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.MeetingFile import convertToImages
from Products.PloneMeeting.interfaces import IAnnexable
from plone.app.async.interfaces import IAsyncService
from collective.documentviewer.async import isConversion
from zope.component import getUtility
from collective.documentviewer.settings import GlobalSettings, Settings
from Products.MeetingAndenne.config import CRON_BATCH_SIZE
from os.path import join

import os
import shutil
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
      This is a view that is called in order to launch OCR on annexes and mails by Products.cron4plone.
      This is used after a migration to update SearchableText on all files. After a migration, a
      cron4plone task is scheduled at 20:00 everyday. Each time this function is called, 2500 uncataloged
      items are added in docsplit queue to be processed.
    """
    def __call__(self):
        logger.info('Looking to see if there are still some blobs to convert.(max %d)' % CRON_BATCH_SIZE)

        catalog = getToolByName(self.context, 'portal_catalog')
        types = ('MeetingFile', 'CourrierFile')
        cpt = 0
        for type in types:
            if cpt >= CRON_BATCH_SIZE:
                break

            brains = catalog(meta_type=type)
            brainslen = len(brains)
            qcpt = 0
            for brain in brains:
                qcpt += 1
                try:
                    object = brain.getObject()
                    removeFlags = False
                    queueObject = False
                    annotations = IAnnotations(object)

                    needsOcr = getattr(object, 'needsOcr', None)
                    if needsOcr is None or needsOcr == False:
                        if hasattr(object, 'needsOcr'):
                            logger.info('Object has needsOcr = False : %s' % object.absolute_url())
                            delattr(object, 'needsOcr')
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
                        logger.info('Object number %d queued on %d %s' %(qcpt, brainslen, type))
                        cpt += 1
                        if cpt >= CRON_BATCH_SIZE:
                            break
                except AttributeError:
                    url = brain.getPath()
                    logger.info('Object doesn\'t exist anymore : ' + url)
                    catalog.uncatalog_object(url)

        logger.info('Added %d jobs in conversion queue' % cpt)

class ParseConvertedFilesView(BrowserView):
    """
      This is a view that is called as a maintenance task by Products.cron4plone.
      It will be launched at 0:30 every first day of month and will scavenge cataloged objects
      that don't exist anymore. At the same time, it will report annexes and mails which were
      not correctly processed by docsplit.
    """
    def __call__(self):
        portal = api.portal.get()
        gsettings = GlobalSettings(portal)
        catalog = portal.portal_catalog

        logger.info('Parsing UIDs in the portal_catalog to find deleted objects.')
        items = catalog.Indexes['UID'].referencedObjects()
        cpt = 0
        logger.info('Parsing ' + str(len(items)) + ' objects.')

        for item in items:
            url = catalog.getpath(item)
            try:
                obj = catalog.unrestrictedTraverse(url)
            except AttributeError:
                logger.info('Object doesn\'t exist anymore : ' + url)
                catalog.uncatalog_object(url)
            cpt += 1
        logger.info(str(cpt) + ' objects parsed.')

        logger.info('Parsing MeetingFiles and CourrierFiles to see if all is correctly converted.')
        annexUIDs = set()
        brains = catalog.searchResults(meta_type='MeetingFile',
                                       sort_on='Date',
                                       sort_order='ascending')
        for brain in brains:
            try:
                annex = brain.getObject()
                annexUID = annex.UID()
                path = join(gsettings.storage_location, annexUID[0], annexUID[1], annexUID)
                if not os.path.exists(path):
                    logger.info(annex.absolute_url() + ' : Annex not converted !')
                annexUIDs.add(annexUID)
            except AttributeError:
                url = brain.getPath()
                logger.info('Object doesn\'t exist anymore : ' + url)
                catalog.uncatalog_object(url)

        logger.info(str(len(annexUIDs)) + ' annexes in the database')

        mailUIDs = set()
        brains = catalog.searchResults(meta_type='CourrierFile',
                                       sort_on='Date',
                                       sort_order='descending')
        for brain in brains:
            mail = brain.getObject()
            mailUID = mail.UID()
            path = join(gsettings.storage_location, mailUID[0], mailUID[1], mailUID)
            if not os.path.exists(path):
                logger.info(mail.absolute_url() + ' : Mail not converted !')
            mailUIDs.add(mailUID)
        logger.info(str(len(mailUIDs)) + ' mails in the database')

        logger.info('Parsing all UIDs to see if all converted files are linked to objects.')
        cpt = 0
        convertedUIDs = annexUIDs.union(mailUIDs)
        hexachars = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
        for firstchar in hexachars:
            for secondchar in hexachars:
                path = join(gsettings.storage_location, firstchar, secondchar)
                if os.path.exists(path):
                    for uid in os.listdir(path):
                        uidpath = join(gsettings.storage_location, firstchar, secondchar, uid)
                        if not os.path.isdir(uidpath):
                            logger.info('There\'s something strange in the directories hierarchy : ' + uidpath)
                        else:
                            if not uid in convertedUIDs:
                                logger.info('Removing unused converted annex : ' + uidpath)
                                shutil.rmtree(uidpath)
                                cpt += 1
        logger.info(str(cpt) + ' directories removed from the conversion results')

class RepairAnnexesView(BrowserView):
    """
      This is a view that is called as a maintenance task by Products.cron4plone.
      It will be launched at 0:30 every first day of month and will scavenge cataloged objects
      that don't exist anymore. At the same time, it will report annexes and mails which were
      not correctly processed by docsplit.
    """
    def __call__(self):
        portal = api.portal.get()
        gsettings = GlobalSettings(portal)
        catalog = getToolByName(self.context, 'portal_catalog')
        cpt = 0

        brains = catalog.searchResults(meta_type='CourrierFile')
        print (len(brains))
        for brain in brains:
            object = brain.getObject()
            annexUID = object.UID()
            path = join(gsettings.storage_location, annexUID[0], annexUID[1], annexUID)
            if not os.path.exists(path):
                object.needsOcr = True
                object.toPrint = True

                annotations = IAnnotations(object)
                if 'collective.documentviewer' in annotations:
                    del annotations['collective.documentviewer']
                if 'Products.MeetingAndenne' in annotations:
                    del annotations['Products.MeetingAndenne']
                cpt += 1
                logger.info('%d : Object flagged for OCR : %s' % (cpt, object.absolute_url()))

        brains = catalog.searchResults(meta_type='MeetingFile')
        print (len(brains))
        for brain in brains:
            object = brain.getObject()
            annexUID = object.UID()
            path = join(gsettings.storage_location, annexUID[0], annexUID[1], annexUID)
            if not os.path.exists(path) and object.findRelatedTo() != 'item_pv':
                object.needsOcr = True
                object.toPrint = True

                annotations = IAnnotations(object)
                if 'collective.documentviewer' in annotations:
                    del annotations['collective.documentviewer']
                if 'Products.MeetingAndenne' in annotations:
                    del annotations['Products.MeetingAndenne']
                cpt += 1
                logger.info('%d : Object flagged for OCR : %s' % (cpt, object.absolute_url()))

        logger.info("flagging for OCR finished")

class RepairCourriersView(BrowserView):
    """
      This is a view that is called as a maintenance task by Products.cron4plone.
      It will be launched at 0:30 every first day of month and will scavenge cataloged objects
      that don't exist anymore. At the same time, it will report annexes and mails which were
      not correctly processed by docsplit.
    """
    def __call__(self):
        portal = api.portal.get()
        gsettings = GlobalSettings(portal)
        catalog = getToolByName(self.context, 'portal_catalog')
        cpt = 0

        brains = catalog.searchResults(meta_type='CourrierFile')
        print (len(brains))
        for brain in brains:
            mail = brain.getObject()
            if getattr(mail, 'saved_request', None) != None:
                cpt += 1
                del mail.saved_request

        logger.info("Corrected %d mails" % (cpt, ))
