# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.PloneMeeting.config import MEETING_GROUP_SUFFIXES
from Products.PloneMeeting.migrations import Migrator

from Products.MeetingAndenne.config import ADD_CONTENT_PERMISSIONS
from Products.MeetingAndenne.profiles.default.import_data import collegeTemplates
from Products.MeetingAndenne.profiles.default.import_data import collegeCategories

meetingFormationFields = ( 'training_type', 'training_purpose', 'training_startDate', \
    'training_endDate', 'training_periodicity', 'training_organiser', 'training_place', \
    'training_users', 'training_additionalUsers', 'training_description', 'training_syllabusCosts', \
    'training_travelExpenses', 'training_parkingFees', 'training_accomodationExpenses', \
    'training_otherFees', 'training_paymentTerms', 'training_accountNumber', 'training_accountName', \
    'training_acceptanceGiro', 'template', 'templateStates'
)

templateDirectories = { 'cpas'                  : u'2040-cpas-tutelle', \
                        'finances'              : u'3330-finances-f.o.v.', \
                        'marches-publics'       : u'3900-marches-publics-autres', \
                        'demande-de-formation-1': u'4360-personnel-missions-de-service',
                      }

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

    def _updateMeetingConfigs(self):
        '''Enable subcategories on College meetingConfig'''
        logger.info('Enabling subcategories on College meetingConfig...')

        for mc in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if mc.getId() == 'meeting-config-college':
                setattr(mc, 'useSubCategories', True)

        logger.info('Done.')

    def _updateCollegeTemplateCategories(self):
        '''Change categories to College template present in subdirectories'''
        logger.info('Changing categories to College template present in subdirectories...')

        collegeConfig = getattr(self.portal.portal_plonemeeting, 'meeting-config-college')
        mainFolder = getattr(collegeConfig, 'itemtemplates')
        folders = []

        for directory, category in templateDirectories.iteritems():
            if hasattr(mainFolder, 'demande-de-formation-1'):
                folders.append(mainFolder[directory])

                while len(folders) > 0:
                    folder = folders.pop()
                    for item in folder:
                        if folder[item].meta_type == 'ATFolder':
                            folders.append(folder[item])
                        elif folder[item].meta_type == 'MeetingItem':
                            folder[item].category = category

        logger.info('Done.')

    def _updatePloneGroupsTitle(self):
        '''Make sure Plone groups linked to a MeetingGroup have a consistent title'''
        logger.info('Making sure Plone groups linked to a MeetingGroup have a consistent title...')

        for mGroup in self.portal.portal_plonemeeting.objectValues('MeetingGroup'):
            for suffix in MEETING_GROUP_SUFFIXES:
                mGroup._createOrUpdatePloneGroup(suffix, update=True)

        logger.info('Done.')

    def _refreshReviewProcessInfoIndex(self):
        '''Refresh reviewProcessInfo index so that personnel points are correctly managed'''
        logger.info('Refreshing reviewProcessInfo index so that personnel points are correctly managed...')

        self.portal.portal_catalog.manage_reindexIndex(ids=['reviewProcessInfo'])

        logger.info('Done.')

    def _adaptMailFolder(self):
        '''Changing security settings set on the mail root folder'''
        logger.info('Changing security settings set on the mail root folder...')

        folderPath = self.portal.portal_plonemeeting.adapted().getCourrierfakeFolder()
        folder = self.portal.restrictedTraverse(folderPath)

        groupId = 'courrierfake_meetingmanagers'
        folder.manage_permission(ADD_CONTENT_PERMISSIONS['CourrierFile'], ('MeetingManager', 'Manager', ), acquire=0)
        folder.manage_addLocalRoles(groupId, ('MeetingManager',))

        logger.info('Done.')

    def _adaptMailWorkflow(self):
        '''Changing workflow so that MailViewers can not modifiy mails anymore'''
        logger.info('Changing workflow so that MailViewers can not modifiy mails anymore...')

        workflowTool = self.portal.portal_workflow
        mailWorkflow = getattr(workflowTool, 'courrierfile_workflow', None)
        if not mailWorkflow:
            logger.warning("courrierfile_workflow doesn't exist")
            return

        state = mailWorkflow.states['not_processed']
        state.setPermission('Modify portal content', 0, ['Manager', 'MeetingManager', 'Owner'])

        logger.info('Done.')

    def _updateMailRoleMappings(self):
        '''Updating role-permission mappings on CourrierFile objects'''
        logger.info('Updating role-permission mappings on CourrierFile objects...')

        wfs = {}
        workflowTool = self.portal.portal_workflow
        mailWorkflow = getattr(workflowTool, 'courrierfile_workflow', None)
        if not mailWorkflow:
            logger.warning("courrierfile_workflow doesn't exist")
            return

        wfs['courrierfile_workflow'] = mailWorkflow
        count = workflowTool._recursiveUpdateRoleMappings(self.portal, wfs)
        logger.info('%d objects have been updated.' % count)

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.3.1...')
        self._installCollectiveDynatree()
        self._migrateMeetingItemFormationObjects()
        self._removeOldMeetingFormationTemplate()
        self._createCollegeCategories()
        self._createPODTemplates()
        self._updateMeetingConfigs()
        self._updateCollegeTemplateCategories()
        self._updatePloneGroupsTitle()
        self._refreshReviewProcessInfoIndex()
        self._adaptMailFolder()
        self._adaptMailWorkflow()
        self._updateMailRoleMappings()
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1)  Install collective.dynatree and updated javascript from MeetingAndenne default profile
       2)  Migrate MeetingFormation template objects
       3)  Remove the template that was used by MeetingItemFormation objects
       4)  Create the new categories and sub-categorie
       5)  Recreate the used POD templates
       6)  Enable subcategories on College meetingConfig
       7)  Change categories to College template present in subdirectories
       8)  Make sure Plone groups linked to a MeetingGroup have a consistent title
       9)  Refresh reviewProcessInfo index so that personnel points are correctly managed
       10) Change security settings set on the mail root folder
       11) Change workflow so that MailViewers can not modifiy mails anymore
       12) Update role-permission mappings on CourrierFile objects
    '''
    Migrate_To_3_3_1(context).run()
# ------------------------------------------------------------------------------
