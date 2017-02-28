# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre NUYENS <andre.nuyens@imio.be>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('MeetingAndenne: setuphandlers')
from Products.MeetingAndenne.config import PROJECTNAME
from Products.MeetingAndenne.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from Products.PloneMeeting.exportimport.content import ToolInitializer
##/code-section HEAD

def isNotMeetingAndenneProfile(context):
    return context.readDataFile("MeetingAndenne_marker.txt") is None



def run_after(context):
    '''Called after the profile-Products.MeetingAndenne:default profile
       is fully imported'''
    profileId = 'profile-Products.MeetingAndenne:default'
    stepContext = context._getImportContext(profileId)

    updateRoleMappings(stepContext)
    postInstall(stepContext)



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMeetingAndenneProfile(context): return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingAndenneProfile(context):
        return
    site = context.getSite()
    # Reinstall PloneMeeting
    reinstallPloneMeeting(context, site)
    # Make sure the 'home' tab is shown
    showHomeTab(context, site)
    # Reinstall the skin
    reinstallPloneMeetingSkin(context, site)
    # reorder skins so we are sure that the meetingAndenne_xxx skins are just under custom
    reorderSkinsLayers(context, site)



##code-section FOOT
def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" % (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def installMeetingAndenne(context):
    """ Run the default profile before bing able to run the Andenne profile"""
    if isNotMeetingAndenneProfile(context):
        return

    logStep("installMeetingAndenne", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingAndenne:default')


def reinstallPloneMeeting(context, site):
    '''Reinstall PloneMeeting so after install methods are called and applied,
       like performWorkflowAdaptations for example.'''

    if isNotMeetingAndenneProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)
    # launch skins step for MeetingAndenne so MeetingAndenne skin layers are before PM ones
    site.portal_setup.runImportStepFromProfile('profile-Products.MeetingAndenne:default', 'skins')


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if isNotMeetingAndenneProfile(context):
        return

    logStep("initializeTool", context)
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()


def showHomeTab(context, site):
    """
       Make sure the 'home' tab is shown...
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("showHomeTab", context)

    index_html = getattr(site.portal_actions.portal_tabs, 'index_html', None)
    if index_html:
        index_html.visible = True
    else:
        logger.info("The 'Home' tab does not exist !!!")


def reinstallPloneMeetingSkin(context, site):
    """
       Reinstall Products.plonemeetingskin as the reinstallation of MeetingAndenne
       change the portal_skins layers order
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("reinstallPloneMeetingSkin", context)
    try:
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:default')
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin')
    except KeyError:
        # if the Products.plonemeetingskin profile is not available
        # (not using plonemeetingskin or in testing?) we pass...
        pass


def reorderSkinsLayers(context, site):
    """
       Reinstall Products.plonemeetingskin and re-apply MeetingAndenne skins.xml step
       as the reinstallation of MeetingAndenne and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    try:
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:default')
        site.portal_setup.runAllImportStepsFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin')
        site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingAndenne:default', 'skins')
    except KeyError:
        # if the Products.plonemeetingskin profile is not available
        # (not using plonemeetingskin or in testing?) we pass...
        pass


def finalizeInstance(context):
    """
      Called at the very end of the installation process (after PloneMeeting).
    """
    reorderSkinsLayers(context, context.getSite())
    reorderCss(context)


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things
       work as expected...
    """
    if isNotMeetingAndenneProfile(context):
        return

    site = context.getSite()

    logStep("reorderCss", context)
    portal_css = site.portal_css
    css = ['plonemeeting.css',
           'meeting.css',
           'meetingitem.css',
           'meetingSeraing.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']
    for resource in css:
        portal_css.moveResourceToBottom(resource)

##/code-section FOOT
