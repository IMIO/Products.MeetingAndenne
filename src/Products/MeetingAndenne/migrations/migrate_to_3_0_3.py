# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.config import TOPIC_SEARCH_SCRIPT, POWEROBSERVERS_GROUP_SUFFIX
from Products.PloneMeeting.migrations import Migrator


# The migration class ----------------------------------------------------------
class Migrate_To_3_0_3(Migrator):

    def _correctMailsLanguage(self):
        '''Correct mails language'''

        DEFAULT_CONTENT_LANGUAGE = 'fr-be'
        # first thing, make sure current language is correct
        languageTool = self.portal.portal_languages
        languageTool.use_combined_language_codes = True
        languageTool.supported_langs = [DEFAULT_CONTENT_LANGUAGE, ]
        languageTool.setDefaultLanguage(DEFAULT_CONTENT_LANGUAGE)
        languageTool.use_request_negotiation = False
        brains = self.portal.portal_catalog(meta_type=['CourrierFile', ])
        logger.info('Correcting mails language for %d items...' % len(brains))
        for brain in brains:
            mail = brain.getObject()
            mail.setLanguage(DEFAULT_CONTENT_LANGUAGE)

        logger.info('Done.')

    def _updateCopyGroupsLocalRoles(self):
        '''Update local roles related to copyGroups.
           Set same situation as before removal of 'MeetingObserverLocalCopy'.
        '''
        logger.info('Updating local roles related to copyGroup...')

        copyGroupsStates = ['validated',
                            'presented',
                            'itemfrozen',
                            'pre_accepted',
                            'accepted',
                            'accepted_but_modified',
                            'delayed',
                            'refused',
                            ]
        copyGroupsStatesWithPublication = list(copyGroupsStates)
        copyGroupsStatesWithPublication.append('itempublished')
        # first set correct value for meetingConfigs.itemCopyGroupsStates
        for cfg in self.portal.portal_plonemeeting.objectValues('MeetingConfig'):
            if 'itempublished' in cfg.listItemStates():
                cfg.setItemCopyGroupsStates(copyGroupsStatesWithPublication)
            else:
                cfg.setItemCopyGroupsStates(copyGroupsStates)
        brains = self.portal.portal_catalog(meta_type=('MeetingItem'))
        logger.info('Updating copyGroups local roles for %s MeetingItem objects...' % len(brains))
        for brain in brains:
            obj = brain.getObject()
            obj.updateCopyGroupsLocalRoles()
            # Update security as local_roles are modified by updateCopyGroupsLocalRoles
            obj.reindexObject(idxs=['allowedRolesAndUsers', ])

        logger.info('MeetingItems copyGroups local roles have been updated.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.0.3...')
        self._correctMailsLanguage()
        self._updateCopyGroupsLocalRoles()

        # reinstall so things overwritten by PloneMeeting profile are restored
#        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function does the following things:

       1) Correct mails language
       2) Update local roles related to copyGroups
    '''
    Migrate_To_3_0_3(context).run()
# ------------------------------------------------------------------------------
