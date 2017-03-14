# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

import mimetypes
from OFS.Image import File
from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.config import MEETING_GROUP_SUFFIXES
from Products.PloneMeeting.migrations import Migrator
from Products.PloneMeeting.profiles import PodTemplateDescriptor

from Products.MeetingAndenne.profiles.default.import_data import collegeTemplates

topicsToRemove = { 'meeting-config-college': ['searchallitemstovalidate', 'searchallitemsingroup'],
                   'courrierfake': ['searchmyitems', 'searchitemsofmygroups', 'searchmyitemstakenover',
                                    'searchallitems', 'searchallitemsincopy', 'searchitemstovalidate',
                                    'searchitemstoprevalidate', 'searchallitemstoadvice', 'searchitemstoadvicewithoutdelay',
                                    'searchitemstoadvicewithdelay', 'searchitemstoadvicewithdexceededelay',
                                    'searchalladviseditems', 'searchalladviseditemswithdelay', 'searchitemstocorrect',
                                    'searchcorrecteditems', 'searchdecideditems', 'searchallmeetings',
                                    'searchalldecisions']
}


# The migration class ----------------------------------------------------------
class Migrate_To_3_3(Migrator):

    def _migrateItemDecisionReportTextAttributeOnConfigs(self):
        '''
          The attribute is now managed by the MeetingConfig.onTransitionFieldTransforms functionnality, so :
          - if it was used, migrate it to MeetingConfig.onTransitionFieldTransforms;
          - removes the obsolete 'itemDecisionReportText' attribute.'''
        logger.info('Removing obsolete attribute \'itemDecisionReportText\' of every MeetingConfigs...')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if hasattr(cfg, 'itemDecisionReportText'):
                if cfg.itemDecisionReportText.raw.strip():
                    # attribute was used, migrate to MeetingConfig.onTransitionFieldTransforms
                    cfg.setOnTransitionFieldTransforms(
                        ({'transition': 'delay',
                          'field_name': 'MeetingItem.decision',
                          'tal_expression': cfg.itemDecisionReportText.raw.strip()},))
                delattr(cfg, 'itemDecisionReportText')
        logger.info('Done.')

    def _updateOnMeetingTransitionItemTransitionToTrigger(self):
        '''Set a value for each MeetingConfig.onMeetingTransitionItemTransitionToTrigger
           attribute so it behaves like before.'''
        logger.info('Updating attribute \'onMeetingTransitionItemTransitionToTrigger\' of every MeetingConfigs...')
        wfTool = getToolByName(self.portal, 'portal_workflow')
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            onMeetingTransitionItemTransitionToTrigger = cfg.getOnMeetingTransitionItemTransitionToTrigger()
            if not onMeetingTransitionItemTransitionToTrigger:
                meetingWFTransitions = wfTool.getWorkflowsFor(cfg.getMeetingTypeName())[0].transitions
                newValue = [{'meeting_transition': 'freeze',
                             'item_transition': 'itemfreeze'}, ]
                # if we have a 'publish' transition in the meeting workflow
                # we take it into account
                if 'publish' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'publish',
                                     'item_transition': 'itemfreeze'})
                    newValue.append({'meeting_transition': 'publish',
                                     'item_transition': 'itempublish'})
                # manage the 'decide' meeting transition
                newValue.append({'meeting_transition': 'decide',
                                 'item_transition': 'itemfreeze'})
                if 'publish' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'decide',
                                     'item_transition': 'itempublish'})
                if 'publish_decisions' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'publish_decisions',
                                     'item_transition': 'itemfreeze'})
                    if 'publish' in meetingWFTransitions:
                        newValue.append({'meeting_transition': 'publish_decisions',
                                         'item_transition': 'itempublish'})
                    newValue.append({'meeting_transition': 'publish_decisions',
                                     'item_transition': 'accept'})
                # manage the 'close' meeting transition
                newValue.append({'meeting_transition': 'close',
                                 'item_transition': 'itemfreeze'})
                if 'publish' in meetingWFTransitions:
                    newValue.append({'meeting_transition': 'close',
                                     'item_transition': 'itempublish'})
                newValue.append({'meeting_transition': 'close',
                                 'item_transition': 'accept'})
                cfg.setOnMeetingTransitionItemTransitionToTrigger(newValue)
        logger.info('Done.')

    def _addCDLDTopics(self):
        '''
          Add CDLD topics for synthesis of all advice.'''
        logger.info('Adding CDLD topics...')
        # add some extra topics to each MeetingConfig
        topicsInfo = (
            # Items for cdld synthesis
            ('searchcdlditems',
            (('Type', 'ATPortalTypeCriterion', ('MeetingItem',)),
             ),
            'created',
            'searchCDLDItems',
            "python: '%s_budgetimpacteditors' % here.portal_plonemeeting.getMeetingConfig(here)"
            ".getId() in member.getGroups() or here.portal_plonemeeting.isManager(here)", ),
        )

        site = self.portal
        for cfg in site.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id != 'meeting-config-college':
                continue
            cfg.createTopics(topicsInfo)
        logger.info('Done.')

    def _migrateMailRoles(self):
        '''Migrate mail roles'''
        logger.info('Migrating mail roles...')

        globalMailManagers = [member for member in self.portal.portal_membership.listMembers() if member.has_role('CourrierManager')]
        mc = self.portal.portal_plonemeeting.adapted().getCourrierfakeConfig()
        groupTool = self.portal.portal_groups
        mmgId = 'courrierfake_meetingmanagers'
        mmg = groupTool.getGroupById('courrierfake_meetingmanagers')

        # move relevant MailManagers to the corresponding group
        if globalMailManagers:
            for member in groupTool.getGroupMembers(mmgId):
                groupTool.removePrincipalFromGroup(member, mmgId)

            for member in globalMailManagers:
                groupTool.addPrincipalToGroup(member.getId(), mmgId)

            # now remove global role 'CourrierManager' given to globalMeetingManagers
            for member in globalMailManagers:
                self.portal.acl_users.portal_role_manager.removeRoleFromPrincipal('CourrierManager', member.getId())

        logger.info('Done.')

    def _removeUselessMailTopics(self):
        '''Remove useless mail topics added by PloneMeeting migration'''
        logger.info('Removing useless mail topics added by PloneMeeting migration...')

        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id in topicsToRemove:
                cfg.topics.manage_delObjects(topicsToRemove[cfg.id])

        logger.info('Done.')

    def _removeUselessFCKEditorProperties(self):
        '''Remove useless fck_editor properties object'''
        logger.info('Removing useless fck_editor properties objec...')

        properties = self.portal.portal_properties
        if 'fckeditor_properties' in properties:
            properties.manage_delObjects(['fckeditor_properties', ])

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
        logger.info('Migrating to MeetingAndenne 3.3...')
        self._migrateItemDecisionReportTextAttributeOnConfigs()
        self._updateOnMeetingTransitionItemTransitionToTrigger()
        self._addCDLDTopics()
        self._migrateMailRoles()
        self._removeUselessMailTopics()
        self._removeUselessFCKEditorProperties()
        self._createPODTemplates()
        self._updatePloneGroupsTitle()
        # reinstall so skins and so on are correct
#        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1) Remove obsolete attribute 'itemDecisionReportText' from every meetingConfigs
       2) Migrate onMeetingTransitionItemTransitionToTrigger
       3) Add topics for CDLD synthesis
       4) Migrate mail roles
       5) Remove useless mail topics added by PloneMeeting migration
       6) Remove useless fck_editor properties object
       7) Recreate the used POD templates
       8) Make sure Plone groups linked to a MeetingGroup have a consistent title
       9) Reinstall Products.MeetingAndenne so skin and so on are correct
    '''
    Migrate_To_3_3(context).run()
# ------------------------------------------------------------------------------
