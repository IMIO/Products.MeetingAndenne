# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

import sys
import mimetypes

from OFS.Image import File
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.config import MEETING_GROUP_SUFFIXES, TOPIC_TAL_EXPRESSION, \
                                         TOPIC_TYPE, TOPIC_SEARCH_SCRIPT
from Products.PloneMeeting.migrations import Migrator
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.PloneMeeting.profiles import GroupDescriptor, PodTemplateDescriptor

from Products.MeetingAndenne.config import ANDENNEROLES, MAIL_TOPICS
from Products.MeetingAndenne.profiles.default.import_data import collegeTemplates
from Products.MeetingAndenne.MeetingItemFormation import MeetingItemFormation

meetingFormationFields = (
    ('formation_type', 'training_type', { u"une formation": u"training",
                                          u"un atelier": u"workshop",
                                          u"un séminaire": u"seminar",
                                          u"une réunion de travail": u"workSession",
                                          u"une séance d'information": u"informationSession",
                                          u"un colloque": u"symposium",
                                          u"un salon": u"show"
                                        }, ),
    ('formation_objet', 'training_purpose', {}, ),
    ('formation_date1', 'training_startDate', {}, ),
    ('formation_date2', 'training_endDate', {}, ),
    ('formation_periode', 'training_periodicity', {}, ),
    ('formation_name', 'training_organiser', {}, ),
    ('formation_place', 'training_place', {}, ),
    ('formation_users', 'training_users', {}, ),
    ('formation_user', 'training_additionalUsers', {}, ),
    ('formation_desc', 'training_description', {}, ),
    ('formation_frais_inscription', 'training_registrationFee', {}, ),
    ('formation_frais_syllabi', 'training_syllabusCosts', {}, ),
    ('formation_frais_deplacement', 'training_travelExpenses', {}, ),
    ('formation_frais_stationnement', 'training_parkingFees', {}, ),
    ('formation_frais_sejour', 'training_accomodationExpenses', {}, ),
    ('formation_frais_autre', 'training_otherFees', {}, ),
    ('formation_mod', 'training_paymentTerms', { "1": "after",
                                                 "2": "before",
                                               }, ),
    ('formation_compte', 'training_accountNumber', {}, ),
    ('formation_compte_name', 'training_accountName', {}, ),
    ('formation_compte_com', 'training_acceptanceGiro', {}, ),
)

meetingConfigs = { 'meeting-config-college': {
    'enableAnnexToPrint': True, 'annexToPrintDefault': True, 'annexDecisionToPrintDefault': True,
    'initItemDecisionIfEmptyOnDecide': False, 'toDiscussShownForLateItems': True, 'xhtmlTransformTypes': (u'removeBlanks', ),
    'xhtmlTransformFields': (u'Meeting.observations', u'Meeting.postObservations', u'MeetingItem.description',
                             u'MeetingItem.decision', u'MeetingItem.projetpv', u'MeetingItem.textpv',
                             u'MeetingItem.pv', u'MeetingItem.observations'),
    'usedItemAttributes': (u'budgetInfos', u'observations', u'toDiscuss', u'itemSignatories'),
    'usedMeetingAttributes': (u'startDate', u'endDate', u'signatories', u'attendees',
                              u'absents', u'lateAttendees', u'place', u'observations', u'postObservations'),
    'toDiscussShownForLateItems': True, 'transitionsToConfirm': [ u'Meeting.freeze', u'Meeting.close', u'MeetingItem.delay',
                                                                   u'MeetingItem.backToProposed', u'MeetingItem.backToItemCreated'],
    'itemCopyGroupsStates': [ u'validated', u'presented', u'itemfrozen', u'pre_accepted', u'accepted', u'accepted_and_closed',
                              u'accepted_but_modified', u'accepted_but_modified_and_closed', u'refused', u'refused_and_closed',
                              u'delayed', u'delayed_and_closed'],
    'itemDecidedStates': [ u'pre_accepted', u'accepted', u'accepted_and_closed', u'refused', u'refused_and_closed', u'accepted_but_modified',
                           u'accepted_but_modified_and_closed', u'delayed', u'delayed_and_closed'],
    'workflowAdaptations': ( u'pre_validation_keep_reviewer_permissions', u'only_creator_may_delete'),
    'onMeetingTransitionItemTransitionToTrigger': ( {'meeting_transition': 'freeze', 'item_transition': 'itemfreeze'},
                                                    {'meeting_transition': 'decide', 'item_transition': 'itemfreeze'},
                                                    {'meeting_transition': 'close', 'item_transition': 'accept'},
                                                    {'meeting_transition': 'close', 'item_transition': 'accept_and_close'},
                                                    {'meeting_transition': 'close', 'item_transition': 'accept_but_modify_and_close'},
                                                    {'meeting_transition': 'close', 'item_transition': 'delay_and_close'},
                                                    {'meeting_transition': 'close', 'item_transition': 'refuse_and_close'} ),
    'useUserReplacements': True,
    },
}

rolesToRemove = [ 'ComdirMember', 'CourrierManager', 'CourrierViewer', 'MeetingAdviceEditor', 'MeetingAdviser', 'MeetingPresenter',
                  'TaskManager', 'TaskPerformer' ]

topicsToRemove = { 'meeting-config-college': ['searchallitemstovalidate', 'searchallitemsingroup'],
                   'courrierfake': ['searchmyitems', 'searchitemsofmygroups', 'searchmyitemstakenover',
                                    'searchallitems', 'searchallitemsincopy', 'searchitemstovalidate',
                                    'searchitemstoprevalidate', 'searchallitemstoadvice', 'searchitemstoadvicewithoutdelay',
                                    'searchitemstoadvicewithdelay', 'searchitemstoadvicewithdexceededelay',
                                    'searchalladviseditems', 'searchalladviseditemswithdelay', 'searchitemstocorrect',
                                    'searchcorrecteditems', 'searchdecideditems', 'searchallmeetings',
                                    'searchalldecisions']
}

topicsToLink = { 'meeting-config-college': ['searchallitemsincopy', 'searchitemstovalidate'], }

memberPropertiesToRemove = ( 'fck_skin', 'fck_path', 'fck_root', 'fck_force_paste_as_text', 'service' )

groupsToRename = { 'copy_of_zonet': {
    'newName': 'cabinet-du-bourgmestre-yt',
    'groupDescriptor': GroupDescriptor('cabinet-du-bourgmestre-yt', 'Cabinet du Bourgmestre (Yasémin Tuzkan)', 'cab_bg_yastuz')
    },
}

typesToAdaptOCR = [ 'CourrierFile', 'MeetingFile' ]

ocrFlagsToRemove = [ 'isOcrized', 'flaggedForOcr' ]

documentviewerConfig = { 'storage_location': '../var/converted_annexes',
                         'ocr': True,
                         'enable_indexation': True,
                         'detect_text': True
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

    def _addMissingRolesAndGroups(self):
        '''Add missing global roles and Plone groups related to MeetingAndenne.'''
        logger.info('Adding missing global roles and Plone groups related to MeetingAndenne...')

        roleManager = self.portal.acl_users.portal_role_manager
        globalRoles = list(self.portal.__ac_roles__)

        for role in ANDENNEROLES.values():
            if role not in roleManager.listRoleIds():
                roleManager.addRole(role, role, '')
                globalRoles.append(role)

        for mGroup in self.portal.portal_plonemeeting.objectValues('MeetingGroup'):
            for suffix in ANDENNEROLES.keys():
                mGroup._createOrUpdatePloneGroup(suffix)

        self.portal.__ac_roles__ = tuple(globalRoles)

        logger.info('Done.')

    def _addMeetingFormationType(self):
        '''Add the template used to create MeetingItemFormation objects'''
        logger.info('Adding the template used to create MeetingItemFormation objects...')

        collegeConfig = getattr(self.portal.portal_plonemeeting, 'meeting-config-college')
        folder = getattr(collegeConfig, 'itemtemplates')

        if hasattr(folder, 'demande-de-formation'):
            folder.manage_delObjects( ['demande-de-formation', ] )

        data = dict()
        data['id'] = 'demande-de-formation'
        data['title'] = 'Demande de formation'
        data['proposingGroup'] = 'secretariat'
        data['templateUsingGroups'] = []
        data['category'] = '45-personnel'
        folder.invokeFactory('MeetingItemCollege', **data)

        item = getattr(folder, data['id'])
        item.schema = MeetingItemFormation.schema
        item.template = 'MeetingItemFormation'
        item.templateStates = ['itemcreated', 'active', 'inactive']

        # call processForm passing dummy values so existing values are not touched
        item.processForm(values={'dummy': None})

        logger.info('Done.')

    def _migrateMeetingItemFormations(self):
        '''Migrate MeetingItemFormation objects'''
        logger.info('Migrating MeetingItemFormation objects...')

        brains = self.portal.portal_catalog(meta_type='MeetingItem')
        for brain in brains:
            item = brain.getObject()
            if hasattr(item, 'template_flag'):
                if getattr(item, 'template_flag') != 'normal':
                    item.schema = MeetingItemFormation.schema
                    item.template = 'MeetingItemFormation'
                    for oldName, newName, valuesDict in meetingFormationFields:
                        if hasattr(item, oldName):
                            oldValue = getattr(item, oldName)
                            setattr(item, newName, valuesDict.get(oldValue, oldValue))
                delattr(item, 'template_flag')
            for oldName, newName, valuesDict in meetingFormationFields:
                if hasattr(item, oldName):
                    delattr(item, oldName)

            if hasattr(item, 'training_registrationFee'):
                delattr(item, 'training_registrationFee')

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

        for mGroup in self.portal.portal_plonemeeting.objectValues('MeetingGroup'):
            advisersGroup = mGroup.getPloneGroupId('advisers')
            mailViewersGroup = mGroup.getPloneGroupId('mailviewers')
            for member in groupTool.getGroupMembers(advisersGroup):
                groupTool.addPrincipalToGroup(member, mailViewersGroup)
                groupTool.removePrincipalFromGroup(member, advisersGroup)

        logger.info('Done.')

    def _cleanApplicationManager(self):
        '''Remove some objects in Zope Control Panel which were not migrated properly'''
        logger.info('Removing some objects in Zope Control Panel which were not migrated properly...')

        rootOb = self.portal.aq_parent
        appManager = rootOb['Control_Panel']
        if appManager.hasObject('TranslationService'):
            appManager._delObject('TranslationService')
            delattr(appManager, '_objects')

        logger.info('Done.')

    def _removeUnusedGlobalRoles(self):
        '''Remove unused global roles'''
        logger.info('Removing unused global roles...')

        roleManager = self.portal.acl_users.portal_role_manager
        globalRoles = list(self.portal.__ac_roles__)
        for role in rolesToRemove:
            if role in globalRoles:
                globalRoles.remove(role)
                try:
                    roleManager.removeRole(role)
                except KeyError:
                    pass
        self.portal.__ac_roles__ = tuple(globalRoles)

        logger.info('Done.')

    def _removeUnusedPloneUsers(self):
        '''Remove unused users present in portal_membership and acl_users'''
        logger.info('Removing unused users present in portal_membership and acl_users...')

        membershipTool = self.portal.portal_membership
        memberDataTool = self.portal.portal_memberdata
        pas = self.portal.acl_users

        memberDataTool.pruneMemberDataContents()

        memberIds = membershipTool.listMemberIds()
        mutableUsers = pas.mutable_properties.enumerateUsers()
        for user in mutableUsers:
            if user['id'] not in memberIds:
                pas.mutable_properties.deleteUser(user['id'])

        logger.info('Done.')

    def _removeUselessMailTopics(self):
        '''Remove useless mail topics added by PloneMeeting migration'''
        logger.info('Removing useless mail topics added by PloneMeeting migration...')

        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if cfg.id in topicsToRemove:
                topics = cfg.topics.keys()
                topicList = [topic for topic in topicsToRemove[cfg.id] if topic in topics]
                cfg.topics.manage_delObjects(topicList)

        logger.info('Done.')

    def _removeUselessFCKEditorProperties(self):
        '''Remove useless fck_editor properties object'''
        logger.info('Removing useless fck_editor properties objec...')

        properties = self.portal.portal_properties
        if 'fckeditor_properties' in properties:
            properties.manage_delObjects(['fckeditor_properties', ])

        siteProperties = properties['site_properties']
        editors = list(siteProperties.available_editors)
        if 'FCKeditor' in editors:
            editors.remove('FCKeditor')
            siteProperties.available_editors = tuple(editors)

        logger.info('Done.')

    def _renameCategories(self):
        '''Rename some categories if they exist and change related MeetingItems'''
        logger.info('Renaming some categories if they exist and change related MeetingItems...')

        for mc in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if mc.getId() == 'meeting-config-college':
                oldIds = []
                newIds = []

                if '63.-centre-ville-revitalisation' in mc.categories.keys():
                    oldIds.append('63.-centre-ville-revitalisation')
                    newIds.append('63-centre-ville-revitalisation')

                if '64.-cpas' in mc.categories.keys():
                    oldIds.append('64.-cpas')
                    newIds.append('64-cpas')

                if 'nage' in mc.categories.keys():
                    oldIds.append('nage')
                    newIds.append('65-nage')

                if len(oldIds) > 0:
                    brains = self.portal.portal_catalog(meta_type='MeetingItem')
                    for brain in brains:
                        item = brain.getObject()
                        if item.category in oldIds:
                            item.category = newIds[oldIds.index(item.category)]
                    for ids in enumerate(oldIds):
                        mc.categories.manage_renameObject(ids[1], newIds[ids[0]])

        logger.info('Done.')

    def _renameGroups(self):
        '''Rename some groups if they exist and change related MeetingItems'''
        logger.info('Renaming some groups if they exist and change related MeetingItems...')

        tool = self.portal.portal_plonemeeting
        membersTool = self.portal.acl_users
        groupsTool = self.portal.portal_groups
        for groupToRename, infos in groupsToRename.items():
            if groupToRename in tool.keys():
                if infos['newName'] not in tool.keys():
                    tool.addUsersAndGroups( (infos['groupDescriptor'], ) )
                    oldGroup = getattr(tool, groupToRename, None)
                    newGroup = getattr(tool, infos['newName'], None)
                    if oldGroup and newGroup:
                        for groupSuffix in MEETING_GROUP_SUFFIXES:
                            oldGroupId = oldGroup.getPloneGroupId(groupSuffix)
                            newGroupId = newGroup.getPloneGroupId(groupSuffix)
                            groupMembers = membersTool.getGroup(oldGroupId).getMemberIds()
                            for member in groupMembers:
                                groupsTool.addPrincipalToGroup(member, newGroupId)
                                groupsTool.removePrincipalFromGroup(member, oldGroupId)

                for mc in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
                    selectable = mc.getSelectableCopyGroups()
                    if groupToRename + '_reviewers' in selectable:
                        selectable = list(selectable)
                        selectable.remove(groupToRename + '_reviewers')
                        selectable.append(infos['newName'] + '_reviewers')
                        mc.setSelectableCopyGroups(tuple(selectable))

                unicodeGroupToRename = unicode(groupToRename)
                unicodeGroupNewName = unicode(infos['newName'])
                brains = self.portal.portal_catalog(meta_type='MeetingItem')
                cpt = 0
                total = len(brains)
                for brain in brains:
                    item = brain.getObject()
                    cpt += 1
                    if unicodeGroupToRename == item.proposingGroup:
                        item.proposingGroup = unicodeGroupNewName

                    if unicodeGroupToRename in item.associatedGroups:
                        associatedGroups = list(item.associatedGroups)
                        associatedGroups.remove(unicodeGroupToRename)
                        associatedGroups.append(unicodeGroupNewName)
                        item.associatedGroups = tuple(associatedGroups)

                    if unicodeGroupToRename in item.optionalAdvisers:
                        optionalAdvisers = list(item.optionalAdvisers)
                        optionalAdvisers.remove(unicodeGroupToRename)
                        optionalAdvisers.append(unicodeGroupNewName)
                        item.optionalAdvisers = tuple(optionalAdvisers)

                    if unicodeGroupToRename in item.adviceIndex:
                        item.adviceIndex[unicodeGroupNewName] = item.adviceIndex[unicodeGroupToRename]
                        item.adviceIndex.remove(unicodeGroupToRename)

                    if unicodeGroupToRename in item.templateUsingGroups:
                        templateUsingGroups = list(item.templateUsingGroups)
                        templateUsingGroups.remove(unicodeGroupToRename)
                        templateUsingGroups.append(unicodeGroupNewName)
                        item.templateUsingGroups = tuple(templateUsingGroups)

                    if unicodeGroupToRename + unicode('_reviewers') in item.copyGroups:
                        copyGroups = list(item.copyGroups)
                        copyGroups.remove(unicodeGroupToRename + unicode('_reviewers'))
                        copyGroups.append(unicodeGroupNewName + unicode('_reviewers'))
                        item.copyGroups = tuple(copyGroups)

                tool.manage_delObjects( [groupToRename, ])

        logger.info('Done.')

    def _adaptUserProperties(self):
        '''Set CKeditor as default editor for everybody and remove useless properties'''
        logger.info('Setting CKeditor as default editor for everybody and removing useless properties...')

        props = { 'wysiwyg_editor': 'CKeditor' }
        memberDataTool = self.portal.portal_memberdata
        membershipTool = self.portal.portal_membership

        for userId in memberDataTool._members.keys():
            member = membershipTool.getMemberById(userId)
            member.setMemberProperties( props )
            propertiesToRemove = [prop for prop in memberPropertiesToRemove if member.hasProperty(prop)]
            member.manage_delProperties(propertiesToRemove)

        logger.info('Done.')

    def _adaptPloneMeetingConfig(self):
        '''Change PloneMeeting configuration'''
        logger.info('Changing PloneMeeting configuration...')

        self.portal.portal_plonemeeting.unoEnabledPython = sys.executable

        logger.info('Done.')

    def _adaptMeetingConfigs(self):
        '''Change various meetingConfigs properties'''
        logger.info('Changing various meetingConfigs properties...')

        for mc in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if mc.getId() in meetingConfigs:
                for key, value in meetingConfigs[mc.getId()].iteritems():
                    setattr(mc, key, value)

            if mc.getId() in topicsToLink:
                topicsUIDs = list()
                for topic in topicsToLink[mc.getId()]:
                    topicsUIDs.append(mc.topics[topic].UID())
                mc.setToDoListTopics(topicsUIDs)

            performWorkflowAdaptations(self.portal, mc, logger)

        logger.info('Done.')

    def _adaptMailFolder(self):
        '''Modify the default view and redirection method of mail folder'''
        logger.info('Modifying the default view and redirection method of mail folder...')

        folderPath = self.portal.portal_plonemeeting.adapted().getCourrierfakeFolder()
        folder = self.portal.restrictedTraverse(folderPath)

        if folder.hasProperty('MEETING_CONFIG'):
            folder.manage_delProperties(['MEETING_CONFIG'])

        folder.setLayout('mailfolder_redirect_view')

        groupId = 'courrierfake_meetingmanagers'
        folder.__ac_local_roles_block__ = True
        folder.manage_addLocalRoles(groupId, ('MeetingManager',))

        logger.info('Done.')

    def _adaptMailSecurity(self):
        '''Modify the local roles of every mail file'''
        logger.info('Modifying the local roles of every mail file...')

        brains = self.portal.portal_catalog(meta_type='CourrierFile')
        for brain in brains:
            item = brain.getObject()
            users = item.users_with_local_role('CourrierViewer')
            if users:
                item.manage_delLocalRoles(users)
            item.updateLocalRoles()

        logger.info('Done.')

    def _adaptOcrFlags(self):
        '''Modify the ocr flags stored with MeetingFile and CourrierFile objects
           so they will be reindex later by cron4plone'''
        logger.info('Modifying the ocr flags stored with MeetingFile and CourrierFile objects...')

        for type in typesToAdaptOCR:
            brains = self.portal.portal_catalog(meta_type=type)
            for brain in brains:
                item = brain.getObject()
                for flag in ocrFlagsToRemove:
                    if hasattr(item, flag):
                        delattr(item, flag)
                item.needsOcr = True
                if getattr(item, 'ocrLanguage', None) is None:
                    item.ocrLanguage = 'fra'

        logger.info('Done.')

    def _createMailTopics(self):
        '''Create the topics used for mail management'''
        logger.info('Creating the topics used for mail management...')

        mc = self.portal.portal_plonemeeting.adapted().getCourrierfakeConfig()
        ids = mc.topics.objectIds()
        if len(ids) > 0:
            ids = list(ids)
            mc.topics.manage_delObjects(ids)

        for topicId, topicCriteria, sortCriterion, searchScriptId, topic_tal_expr in MAIL_TOPICS:
            mc.topics.invokeFactory('Topic', topicId)
            topic = getattr(mc.topics, topicId)
            topic.setExcludeFromNav(True)
            topic.setTitle(topicId)
            for criterionName, criterionType, criterionValue in topicCriteria:
                criterion = topic.addCriterion(field=criterionName, criterion_type=criterionType)
                if criterionValue is not None:
                    if criterionType == 'ATPortalTypeCriterion':
                        concernedType = criterionValue[0]
                        topic.manage_addProperty(TOPIC_TYPE, concernedType, 'string')
                        # This is necessary to add a script doing the search
                        # when the it is too complicated for a topic.
                        topic.manage_addProperty(TOPIC_SEARCH_SCRIPT, searchScriptId, 'string')
                        # Add a tal expression property
                        topic.manage_addProperty(TOPIC_TAL_EXPRESSION, topic_tal_expr, 'string')
                    criterion.setValue(criterionValue)
            topic.setLimitNumber(True)
            topic.setItemCount(50)
            topic.setSortCriterion(sortCriterion, True)
            topic.setCustomView(True)
            topic.setCustomViewFields(['destUsers', 'destOrigin', 'refcourrier', 'Title'])
            # call processForm passing dummy values so existing values are not touched
            topic.processForm( values = {'dummy': None} )

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

    def _updateDocumentViewerConfiguration(self):
        '''Modify the configuration of the collective.documentviewer product'''
        logger.info('Modifying the configuration of the collective.documentviewer product...')

        site = self.portal
        annotations = IAnnotations(site)
        config = annotations.get('collective.documentviewer', None)
        if config != None:
            for key, value in documentviewerConfig.iteritems():
                config[key] = value

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.3...')
        self._migrateItemDecisionReportTextAttributeOnConfigs()
        self._updateOnMeetingTransitionItemTransitionToTrigger()
        self._addMissingRolesAndGroups()
        self._addMeetingFormationType()
        self._migrateMeetingItemFormations()
        self._migrateMailRoles()
        self._cleanApplicationManager()
        self._removeUnusedGlobalRoles()
        self._removeUnusedPloneUsers()
        self._removeUselessMailTopics()
        self._removeUselessFCKEditorProperties()
        self._renameCategories()
        self._renameGroups()
        self._adaptUserProperties()
        self._adaptPloneMeetingConfig()
        self._adaptMeetingConfigs()
        self._adaptMailFolder()
        self._adaptMailSecurity()
        self._adaptOcrFlags()
        self._createMailTopics()
        self._createPODTemplates()
        self._updatePloneGroupsTitle()
        self._updateDocumentViewerConfiguration()
        # reinstall so skins and so on are correct
        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        # update catalogs after performing all those migration steps
        self.refreshDatabase(catalogs=True,
                             catalogsToRebuild=['portal_catalog',
                                                'uid_catalog',
                                                'reference_catalog', ],
                             workflows=False)
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function:

       1)  Remove obsolete attribute 'itemDecisionReportText' from every meetingConfigs
       2)  Migrate onMeetingTransitionItemTransitionToTrigger
       3)  Add missing global roles and Plone groups related to MeetingAndenne
       4)  Add the template used to create MeetingItemFormation objects
       5)  Migrate MeetingItemFormation objects
       6)  Migrate mail roles
       7)  Remove some objects in Zope Control Panel which were not migrated properl
       8)  Remove unused global roles
       9)  Remove unused users present in portal_membership and acl_users
       10) Remove useless mail topics added by PloneMeeting migration
       11) Remove useless fck_editor properties object
       12) Rename some categories if they exist and change related MeetingItems
       13) Rename some groups if they exist and change related MeetingItems
       14) Set CKeditor as default editor for everybody and remove useless properties
       15) Change ploneMeeting configuration
       16) Change various meetingConfigs properties
       17) Modify the default view and redirection method of mail folder
       18) Modify the local roles of every mail file
       19) Modify the ocr flags stored with MeetingFile and CourrierFile objects
       20) Create the topics used for mail management
       21) Recreate the used POD templates
       22) Make sure Plone groups linked to a MeetingGroup have a consistent title
       23) Modify the configuration of the collective.documentviewer product
       24) Reinstall Products.MeetingAndenne so skin and so on are correct
    '''
    Migrate_To_3_3(context).run()
# ------------------------------------------------------------------------------
