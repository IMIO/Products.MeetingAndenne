# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.PloneMeeting.migrations import Migrator


# The migration class ----------------------------------------------------------
class Migrate_To_3_1(Migrator):

    def _removeUselessMailTopics(self):
        '''Remove useless mail topics added by PloneMeeting migration'''
        logger.info('Removing useless mail topics added by PloneMeeting migration...')

        mc = self.portal.portal_plonemeeting.adapted().getCourrierfakeConfig()
        ids = mc.topics.keys()
        if len(ids) > 0:
            ids = ['searchitemstoprevalidate', 'searchitemstovalidate']
            mc.topics.manage_delObjects(ids)

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.1...')
        self._removeUselessMailTopics()

        # reinstall so things overwritten by PloneMeeting profile are restored
#        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Remove useless mail topics added by PloneMeeting migration
    '''
    Migrate_To_3_1(context).run()
# ------------------------------------------------------------------------------
