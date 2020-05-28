# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName

from Products.PloneMeeting.migrations import Migrator
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor

from Products.MeetingAndenne.profiles.andenne.import_data import collegeTemplates


# The migration class ----------------------------------------------------------
class Migrate_To_3_3_2(Migrator):

    def _removeInitItemDecisionIfEmptyOnDecide(self):
        '''Remove the useless initItemDecisionIfEmptyOnDecide attribute from every
           MeetingConfigs.'''
        logger.info('Removing useless attribute \'initItemDecisionIfEmptyOnDecide\' of every MeetingConfigs...')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if hasattr(cfg, 'initItemDecisionIfEmptyOnDecide'):
                delattr(cfg, 'initItemDecisionIfEmptyOnDecide')
        logger.info('Done.')

    def _createPODTemplates(self):
        '''Recreate the used POD templates'''
        logger.info('Recreating the used POD templates...')

        # find the templates path so we can read and store them in the PodTemplate objects
        mcProfilePath = [profile for profile in self.context.listProfileInfo() if 'id' in profile
                         and profile['id'] == u'Products.MeetingAndenne:andenne'][0]['path']
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id == 'meeting-config-college':
                templatesIds = cfg.podtemplates.keys()
                if len(templatesIds) > 0:
                    ids = list(templatesIds)
                    cfg.podtemplates.manage_delObjects(ids)

                for template in collegeTemplates:
                    cfg.addPodTemplate(template, mcProfilePath)

        logger.info('Done.')

    def _addAnnexesPVActions(self):
        '''Add actions on MeetingItems used to add annexes on PVs'''
        logger.info('Adding actions on MeetingItems used to add annexes on PVs...')

        types = self.portal.portal_types
        meetingItemType = getattr(types, 'MeetingItem')

        idx = None
        cpt = 0
        alreadyPresent = False
        for action in meetingItemType._actions:
            cpt += 1
            if action.id == 'annexes_pv_form':
                alreadyPresent = True
                break

            if action.id == 'annexes_decision_form':
                idx = cpt

        if not alreadyPresent:
            meetingItemType.addAction(id='annexes_pv_form',
                                      name='AnnexesPV',
                                      action='string:${object_url}/annexes_pv_form',
                                      condition='python:here.showAnnexesTab(pvRelated=True)',
                                      permission='',
                                      category='object'
                                     )
            actions = meetingItemType._cloneActions()
            if idx < len(actions):
                actions.insert(idx, actions.pop())
            meetingItemType._actions = tuple( actions )

        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id != 'courrierfake':
                cfg.updatePortalTypes()

        logger.info('Done.')

    def _addPVAnnexesTypes(self):
        '''Add MeetingItemTypes used with annexes on PVs'''
        logger.info('Adding MeetingItemTypes used with annexes on PVs...')

        mfts = []
        mfts.append(MeetingFileTypeDescriptor(id='noteExecution',
                                              title=u'Note d\'exécution signée',
                                              theIcon='executionNote.png',
                                              predefinedTitle='',
                                              relatedTo='item_pv',
                                              active=True))
        mfts.append(MeetingFileTypeDescriptor(id='deliberation',
                                              title=u'Délibération signée',
                                              theIcon='executionNote.png',
                                              predefinedTitle='',
                                              relatedTo='item_pv',
                                              active=True))
        # find the icon path so we can give it to MeetingConfig.addFileType
        mcProfilePath = [profile for profile in self.context.listProfileInfo() if 'id' in profile
                         and profile['id'] == u'Products.MeetingAndenne:andenne'][0]['path']
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id != 'meeting-config-college':
                continue
            for mft in mfts:
                if not hasattr(aq_base(cfg.meetingfiletypes), mft.id):
                    cfg.addFileType(mft, source=mcProfilePath)

        logger.info('Done.')

    def _updateItemWorkflow(self):
        '''Reapply modified workflow on MeetingItems'''
        logger.info('Reapplying modified workflow on MeetingItems...')

        catalog = getToolByName(self.portal, 'portal_catalog')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        ps = getToolByName(self.portal, 'portal_setup')
        ps.runImportStepFromProfile(u'profile-Products.MeetingAndenne:default', 'workflow')

        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            performWorkflowAdaptations(self.portal, cfg, logger)

        catalog.reindexIndex('allowedRolesAndUsers', None)
        wfTool.updateRoleMappings()

        logger.info('Done.')

    def _addPVAnnexEvent(self):
        '''Add a custom event to the list of item events that generates emails'''
        logger.info('Adding a custom event to the list of item events that generates emails...')

        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id != 'meeting-config-college':
                continue
            itemEvents = list(cfg.getMailItemEvents())
            if not 'event_add_pv_annex' in itemEvents:
                itemEvents.append('event_add_pv_annex')
                cfg.setMailItemEvents(tuple(itemEvents))

        logger.info('Done.')

    def _addNewFieldsLastMeetingNumberInParliamentaryTerm(self):
        '''Add a new field to MeetingConfig and Meeting objects used to number Meetings sequentially
           relating to a parliamentary term'''
        logger.info('Adding LastNumberInParliamentaryTerm field to every MeetingConfig and Meeting object...')

        catalog = getToolByName(self.portal, 'portal_catalog')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id == 'courrierfake':
                continue

            if hasattr(cfg, 'lastMeetingNumberInParliamentaryTerm'):
                continue

            brains = catalog.searchResults(portal_type=cfg.getMeetingTypeName())
            for brain in brains:
                meeting = brain.getObject()
                if not hasattr(meeting, 'meetingNumberInParliamentaryTerm'):
                    meeting.meetingNumberInParliamentaryTerm = -1

            cfg.lastMeetingNumberInParliamentaryTerm = 0

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.3.2...')
        self._removeInitItemDecisionIfEmptyOnDecide()
        self._createPODTemplates()
        self._addAnnexesPVActions()
        self._addPVAnnexesTypes()
        self._updateItemWorkflow()
        self._addPVAnnexEvent()
        self._addNewFieldsLastMeetingNumberInParliamentaryTerm()

        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1)  Remove useless attribute 'initItemDecisionIfEmptyOnDecide' field from every meetingConfigs
       2)  Recreate the used POD templates
       3)  Add actions on MeetingItems used to add annexes on PVs
       4)  Add MeetingItemTypes used with annexes on PVs
       5)  Reapply modified workflow on MeetingItems
       6)  Add a custom event to the list of item events that generates emails
       7)  Add LastNumberInParliamentaryTerm field to every MeetingConfig and Meeting object
    '''
    Migrate_To_3_3_2(context).run()
# ------------------------------------------------------------------------------
