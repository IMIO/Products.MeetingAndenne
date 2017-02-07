# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.PloneMeeting.migrations import Migrator


# The migration class ----------------------------------------------------------
class Migrate_To_3_1(Migrator):

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.1...')
        # reinstall so things overwritten by PloneMeeting profile are restored
#        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Reinstall MeetingAndenne default profile
    '''
    Migrate_To_3_1(context).run()
# ------------------------------------------------------------------------------
