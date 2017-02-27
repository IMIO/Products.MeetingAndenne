# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Acquisition import aq_base

from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.migrations import Migrator


# The migration class ----------------------------------------------------------
class Migrate_To_3_2(Migrator):

    def _removeUselessMailTopics(self):
        '''Remove useless mail topics added by PloneMeeting migration'''
        logger.info('Removing useless mail topics added by PloneMeeting migration...')

        mc = self.portal.portal_plonemeeting.adapted().getCourrierfakeConfig()
        ids = mc.topics.keys()
        if len(ids) > 0:
            ids = ['searchitemstoadvicewithdelay', 'searchitemstoadvicewithdexceededelay',
                   'searchalladviseditemswithdelay', 'searchitemstocorrect',
                   'searchcorrecteditems']
            mc.topics.manage_delObjects(ids)

        logger.info('Done.')

    def _addDefaultAdviceAnnexesFileTypes(self):
        '''Add some default MeetingFileType relatedTo 'advice' so we can add
           annexes on advices.'''
        logger.info('Addind default MeetingFileType relatedTo \'advice\'...')
        mfts = []
        mfts.append(MeetingFileTypeDescriptor(id='annexeAvis',
                                              title=u'Annexe à un avis',
                                              theIcon='attach.png',
                                              predefinedTitle='',
                                              relatedTo='advice',
                                              active=True))
        mfts.append(MeetingFileTypeDescriptor(id='annexeAvisLegal',
                                              title=u'Extrait article de loi',
                                              theIcon='legalAdvice.png',
                                              predefinedTitle='',
                                              relatedTo='advice',
                                              active=True))
        # find theIcon path so we can give it to MeetingConfig.addFileType
        mcProfilePath = [profile for profile in self.context.listProfileInfo() if 'id' in profile
                         and profile['id'] == u'Products.MeetingAndenne:default'][0]['path']
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id != 'meeting-config-college':
                continue
            for mft in mfts:
                if not hasattr(aq_base(cfg.meetingfiletypes), mft.id):
                    cfg.addFileType(mft, source=mcProfilePath)
        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.2...')
        self._removeUselessMailTopics()
        self._addDefaultAdviceAnnexesFileTypes()

        # reinstall so things overwritten by PloneMeeting profile are restored
#        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Remove useless mail topics added by PloneMeeting migration
       2) Add default MeetingFileType relatedTo 'advice'
    '''
    Migrate_To_3_2(context).run()
# ------------------------------------------------------------------------------
