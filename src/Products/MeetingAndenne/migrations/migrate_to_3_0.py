# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('MeetingAndenne')

from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.config import POWEROBSERVERS_GROUP_SUFFIX
from Products.PloneMeeting.migrations import Migrator


# The migration class ----------------------------------------------------------
class Migrate_To_3_0(Migrator):

    def _removeIconExprObjectsOnTypes(self):
        '''Remove icon_expr_object on portal_types relative to MeetingAndenne.'''
        logger.info('Removing icon_expr_objects on portal_types...')

        for ptype in self.portal.portal_types.objectValues():
            typeId = ptype.getId()
            if typeId == 'CourrierFile' and \
               hasattr(ptype, 'icon_expr_object') and \
               ptype.icon_expr_object and \
               ptype.icon_expr_object.text:
                    ptype.icon_expr_object = None
        logger.info('Done.')

    def _migrateCourrierFilesToBlobs(self):
        '''Migrate CourrierFiles to Blobs.'''
        logger.info('Migrating CourrierFiles to Blobs...')

        # Call an helper method of plone.app.blob that does "inplace" migration
        # so existing 'mails' are migrated to blob
        brains = self.portal.portal_catalog(meta_type='CourrierFile')
        # Some CourrierFiles to migrate?
        if not brains:
            logger.info('No CourrierFiles found.')
            return
        # Check if migration has already been launched
        aCourrierFile = brains[0].getObject()
        if aCourrierFile.getField('file').get(aCourrierFile).__module__ == 'plone.app.blob.field':
            logger.info('CourrierFiles already migrated to blobs.')
            return

        logger.info('Migrating %s CourrierFile objects...' % len(brains))
        from plone.app.blob.migrations import migrate
        migrate(self.portal, 'CourrierFile')

        logger.info('Done.')

    def _retrieveCourrierFilesTitles(self):
        '''Restore titles to CourrierFiles which were lost during Blobs migration.'''
        logger.info('Restoring titles to CourrierFiles which were lost during Blobs migration...')

        for brain in self.portal.portal_catalog(meta_type='CourrierFile'):
            item = brain.getObject()
            if not item.Title():
                item.setTitle(item.__dict__['title'])
                item.reindexObject(idxs=['Title', ])
        logger.info('Done.')

    def _adaptCourrierFilesCatalogIndexes(self):
        '''Adapt indexes definitions linked to CourrierFiles.'''
        logger.info('Adapting indexes definitions linked to CourrierFiles...')

        addedIndexes = []
        catalog = self.portal.portal_catalog
        zopeCatalog = catalog._catalog

        if 'getRefcourrierFake' in zopeCatalog.indexes:
            catalog.delIndex('getRefcourrierFake')

        if 'getRefcourrier' in zopeCatalog.indexes:
            if zopeCatalog.indexes['getRefcourrier'].__class__.__name__ != 'FieldIndex':
                catalog.delIndex('getRefcourrier')

        if not 'getRefcourrier' in zopeCatalog.indexes:
            catalog.addIndex('getRefcourrier', 'FieldIndex')
            addedIndexes.append('getRefcourrier')

        if not 'sortable_sender' in zopeCatalog.indexes:
            catalog.addIndex('sortable_sender', 'FieldIndex')
            addedIndexes.append('sortable_sender')

        if len(addedIndexes) > 0:
            catalog.reindexIndex(tuple(addedIndexes), self.portal.REQUEST)

        logger.info('Done.')

    def _removeGlobalPowerObservers(self):
        ''' Before, PowerObservers where global to every meetingConfig. Now
            that PowerObservers are locally defined for each meetingConfig,
            remove the useless 'MeetingPowerObserver' role, remove the useless
            'meetingpowerobservers' group and put users of these groups in relevant
            '_powerobservers' suffixed groups for active meetingConfigs.'''
        logger.info('Migrating from global PowerObservers to local PowerObservers...')

        portal = self.portal
        # remove the 'meetingpowerobservers' group
        # put every users of this group to '_powerobservers' suffixed groups of active meetingConfigs
        # generate a list of groups to transfer users to
        localPowerObserversGroupIds = []
        for cfg in portal.portal_plonemeeting.getActiveConfigs():
            localPowerObserversGroupIds.append("%s_%s" % (cfg.getId(), POWEROBSERVERS_GROUP_SUFFIX))

        powerObserverGroup = portal.portal_groups.getGroupById('meetingpowerobservers')
        existingPowerObserverUserIds = powerObserverGroup and powerObserverGroup.getGroupMemberIds() or ()
        for localPowerObserversGroupId in localPowerObserversGroupIds:
            for existingPowerObserverUserId in existingPowerObserverUserIds:
                portal.portal_groups.addPrincipalToGroup(existingPowerObserverUserId, localPowerObserversGroupId)

        # remove the 'meetingpowerobservers' group
        # first remove every role given to the 'meetingpowerobservers' group
        meetingpowerobservers = portal.portal_groups.getGroupById('meetingpowerobservers')
        if meetingpowerobservers:
            for role in portal.acl_users.portal_role_manager.getRolesForPrincipal(meetingpowerobservers):
                portal.acl_users.portal_role_manager.removeRoleFromPrincipal(role, 'meetingpowerobservers')
            # remove the group
            portal.portal_groups.removeGroup('meetingpowerobservers')
        # remove the 'MeetingPowerObserver' role
        data = list(portal.__ac_roles__)
        if 'MeetingPowerObserver' in data:
            # first on the portal
            data.remove('MeetingPowerObserver')
            portal.__ac_roles__ = tuple(data)
            # then in portal_role_manager
            try:
                portal.acl_users.portal_role_manager.removeRole('MeetingPowerObserver')
            except KeyError:
                pass

        logger.info('Done.')

    def run(self):
        logger.info('Migrating to MeetingAndenne 3.0...')
        self._removeIconExprObjectsOnTypes()
        self._migrateCourrierFilesToBlobs()
        self._retrieveCourrierFilesTitles()
        self._adaptCourrierFilesCatalogIndexes()
        self._removeGlobalPowerObservers()

        # reinstall so things overwritten by PloneMeeting profile are restored
#        self.reinstall(profiles=[u'profile-Products.MeetingAndenne:default', ])
        self.finish()


# The migration function -------------------------------------------------------
def migrate(context):
    '''This migration function does the following things:

       1) Remove icon_expr_object on portal_types relative to MeetingAndenne
       2) Migrate CourrierFiles to Blobs
       3) Restore titles to CourrierFiles which were lost during Blobs migration
       4) Adapt indexes definitions linked to CourrierFiles
       5) Migrate from global PowerObservers to local PowerObservers
    '''
    Migrate_To_3_0(context).run()
# ------------------------------------------------------------------------------
