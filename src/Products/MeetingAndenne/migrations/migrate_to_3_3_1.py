# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.PloneMeeting.config import MEETING_GROUP_SUFFIXES
from Products.PloneMeeting.migrations import Migrator

from Products.MeetingAndenne.profiles.default.import_data import collegeTemplates
from Products.MeetingAndenne.profiles.default.import_data import collegeCategories

meetingFormationFields = ( 'training_type', 'training_purpose', 'training_startDate', \
    'training_endDate', 'training_periodicity', 'training_organiser', 'training_place', \
    'training_users', 'training_additionalUsers', 'training_description', 'training_syllabusCosts', \
    'training_travelExpenses', 'training_parkingFees', 'training_accomodationExpenses', \
    'training_otherFees', 'training_paymentTerms', 'training_accountNumber', 'training_accountName', \
    'training_acceptanceGiro', 'template', 'templateStates'
)

# The migration class ----------------------------------------------------------
class Migrate_To_3_3_1(Migrator):

    def _installCollectiveDynatree(self):
        '''Install collective.dynatree and updated javascript from MeetingAndenne default profile'''
        logger.info('Installing collective.dynatree and updated javascript from MeetingAndenne default profile...')

        ps = self.portal.portal_setup
        ps.runAllImportStepsFromProfile('profile-collective.dynatree:default')
        ps.runImportStepFromProfile(u'profile-Products.MeetingAndenne:default', 'jsregistry')

        logger.info('Done.')

    def _migrateMeetingItemFormationObjects(self):
        '''Migrate MeetingItemFormation objects'''
        logger.info('Migrating MeetingItemFormation objects...')

        cpts = { 'formations': {}, 'others': {} }
        for attrName in meetingFormationFields:
            cpts['formations'][attrName] = 0
            cpts['others'][attrName] = 0

        brains = self.portal.portal_catalog(meta_type='MeetingItem')
        cptItem = 0
        cptFormations = 0
        cptNotFormations = 0
        for brain in brains:
            cptItem += 1
            item = brain.getObject()
            if hasattr(item, 'template'):
                cptFormations += 1
                enbois = 'formations'
                delattr(item, 'schema')
            else:
                cptNotFormations += 1
                enbois = 'others'

            for attrName in meetingFormationFields:
                if getattr(item, attrName, None):
                    cpts[enbois][attrName] += 1
                    delattr(item, attrName)

        print 'Number of Items : ' + str(len(brains))
        print 'Number of Formations : ' + str(cptFormations)
        print 'Number of normal Items : ' + str(cptNotFormations)

        print 'others :'
        for key, value in cpts['others'].iteritems():
            print '\t%s => %5d' % (key, value)

        print '\nformations :'
        for key, value in cpts['formations'].iteritems():
            print '\t%s => %5d' % (key, value)

        logger.info('Done.')

    def _migrateMeetingFormationTemplates(self):
        '''Migrate MeetingFormation template objects'''
        logger.info('Migrating MeetingFormation template objects...')

        collegeConfig = getattr(self.portal.portal_plonemeeting, 'meeting-config-college')
        folder = getattr(collegeConfig, 'itemtemplates')
        folders = []

        if hasattr(folder, 'demande-de-formation-1'):
            folders.append(folder['demande-de-formation-1'])

        while len(folders) > 0:
            folder = folders.pop()
            for item in folder:
                if folder[item].meta_type == 'ATFolder':
                    folders.append(folder[item])
                elif folder[item].meta_type == 'MeetingItem':
                    folder[item].category = u'4360-personnel-missions-de-service'

        logger.info('Done.')

    def _removeOldMeetingFormationTemplate(self):
        '''Remove the template that was used by MeetingItemFormation objects'''
        logger.info('Removing the template that was used by MeetingItemFormation object...')

        collegeConfig = getattr(self.portal.portal_plonemeeting, 'meeting-config-college')
        folder = getattr(collegeConfig, 'itemtemplates')

        if hasattr(folder, 'demande-de-formation'):
            folder.manage_delObjects( ['demande-de-formation', ] )

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
        self._migrateMeetingItemFormationObjects()
        self._migrateMeetingFormationTemplates()
        self._removeOldMeetingFormationTemplate()
        self._createCollegeCategories()
        self._createPODTemplates()
        self._updatePloneGroupsTitle()
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Install collective.dynatree and updated javascript from MeetingAndenne default profile
       2) Migrate MeetingItemFormation objects
       3) Migrate MeetingFormation template objects
       4) Remove the template that was used by MeetingItemFormation objects
       5) Create the new categories and sub-categorie
       6) Recreate the used POD templates
       7) Make sure Plone groups linked to a MeetingGroup have a consistent title
    '''
    Migrate_To_3_3_1(context).run()
# ------------------------------------------------------------------------------
