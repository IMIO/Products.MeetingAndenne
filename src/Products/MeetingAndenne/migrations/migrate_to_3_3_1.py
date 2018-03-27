# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.PloneMeeting.config import MEETING_GROUP_SUFFIXES
from Products.PloneMeeting.migrations import Migrator

from Products.MeetingAndenne.profiles.default.import_data import collegeTemplates
from Products.MeetingAndenne.profiles.default.import_data import collegeCategories

# The migration class ----------------------------------------------------------
class Migrate_To_3_3_1(Migrator):

    def _installCollectiveDynatree(self):
        '''Install collective.dynatree and updated javascript from MeetingAndenne default profile'''
        logger.info('Installing collective.dynatree and updated javascript from MeetingAndenne default profile...')

        ps = self.portal.portal_setup
        ps.runAllImportStepsFromProfile('profile-collective.dynatree:default')
        ps.runImportStepFromProfile(u'profile-Products.MeetingAndenne:default', 'jsregistry')

        logger.info('Done.')

    def _createCollegeCategories(self):
        '''Create the new categories and sub-categories'''
        logger.info('Creating the new categories and sub-categorie...')

        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id == 'meeting-config-college':
                for cat in collegeCategories:
                    cfg.addCategory(cat)

        logger.info('Done.')

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

    def _updatePloneGroupsTitle(self):
        '''Make sure Plone groups linked to a MeetingGroup have a consistent title'''
        logger.info('Making sure Plone groups linked to a MeetingGroup have a consistent title...')

        for mGroup in self.portal.portal_plonemeeting.objectValues('MeetingGroup'):
            for suffix in MEETING_GROUP_SUFFIXES:
                mGroup._createOrUpdatePloneGroup(suffix, update=True)

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.3.1...')
        self._installCollectiveDynatree()
        self._createCollegeCategories()
        self._createPODTemplates()
        self._updatePloneGroupsTitle()
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Install collective.dynatree and updated javascript from MeetingAndenne default profile
       2) Create the new categories and sub-categorie
       3) Recreate the used POD templates
       4) Make sure Plone groups linked to a MeetingGroup have a consistent title
    '''
    Migrate_To_3_3_1(context).run()
# ------------------------------------------------------------------------------
