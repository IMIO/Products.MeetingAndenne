# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.PloneMeeting.migrations import Migrator

from Products.MeetingAndenne.profiles.default.import_data import collegeTemplates


# The migration class ----------------------------------------------------------
class Migrate_To_3_3_2(Migrator):

    def _createPODTemplates(self):
        '''Recreate the used POD templates'''
        logger.info('Recreating the used POD templates...')

        # find the templates path so we can read and store them in the PodTemplate objects
        mcProfilePath = [profile for profile in self.context.listProfileInfo() if 'id' in profile
                         and profile['id'] == u'Products.MeetingAndenne:default'][0]['path']
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id == 'meeting-config-college':
                templatesIds = cfg.podtemplates.keys()
                if len(templatesIds) > 0:
                    ids = list(templatesIds)
                    cfg.podtemplates.manage_delObjects(ids)

                for template in collegeTemplates:
                    cfg.addPodTemplate(template, mcProfilePath)

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.3.2...')
        self._createPODTemplates()
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1)  Recreate the used POD templates
    '''
    Migrate_To_3_3_2(context).run()
# ------------------------------------------------------------------------------
