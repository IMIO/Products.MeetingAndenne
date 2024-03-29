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
from Persistence import PersistentMapping
from persistent.list import PersistentList
from Products.MeetingAndenne.config import PROJECTNAME
from Products.MeetingAndenne.config import DEPENDENCIES
from Products.MeetingAndenne.config import CRON_TASKS
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from zope.component import queryUtility
from Products.cron4plone.browser.configlets.cron_configuration import ICronConfiguration
from Products.PloneMeeting.exportimport.content import ToolInitializer
from Products.PloneMeeting.model.adaptations import performWorkflowAdaptations
from Products.PloneMeeting.config import TOOL_FOLDER_POD_TEMPLATES
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.catalog import addOrUpdateColumns

noSearchTypes = ('MeetingCfake', 'MeetingItemCfake', )
# Indexes used by MeetingAndenne
indexInfos = {
                # CourrierFile-related indexes
                'getDestGroups': ( 'KeywordIndex', {} ),
                'getDestOrigin': ( 'ZCTextIndex', {} ),
                'getDestUsers': ( 'KeywordIndex', {} ),
                'getRefcourrier': ( 'FieldIndex', {} ),
                'getTypecourrier': ( 'FieldIndex', {} ),
                'sortable_sender': ( 'FieldIndex', {} ),
                #MeetingItem-related indexes
                'getTreatUser': ( 'FieldIndex', {} )
             }
# Metadata to create in portal_catalog, it has to correspond to an index in indexInfo
columnInfos = ( 'getCategory', 'getDestOrigin', 'getDestUsers', 'getRefcourrier',
                'getTreatUser' )
##/code-section HEAD

def isNotMeetingAndenneProfile(context):
    return context.readDataFile("MeetingAndenne_marker.txt") is None

def isMeetingAndenneConfigureProfile(context):
    return context.readDataFile("MeetingAndenne_configure_marker.txt")


def run_after(context):
    '''Called after the profile-Products.MeetingAndenne:default profile
       is fully imported'''
    profileId = 'profile-Products.MeetingAndenne:default'
    stepContext = context._getImportContext(profileId)

    postInstall(stepContext)
    updateRoleMappings(stepContext)
    reorderCss(stepContext)


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingAndenneProfile(context):
        return

    logStep("postInstall", context)
    site = context.getSite()

    # Create or update indexes
    addOrUpdateIndexes(site, indexInfos)
    addOrUpdateColumns(site, columnInfos)

    # Need to reinstall PloneMeeting after reinstalling MA workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)

    # Make sure the 'home' tab is shown
    showHomeTab(context, site)

    # reorder skins so we are sure that the meetingAndenne_xxx skins are just under custom
    reorderSkinsLayers(context, site)

    # reimport actions provider so that useless portal_tabs are not shown anymore
    reorderPortalTabs(context, site)

    # reimport plone.app.search javascript registry as some scripts are missing
    reorderScriptsRegistry(context, site)

    # Remove some types from the standard Plone search (live and advanced)
    props = site.portal_properties.site_properties
    nsTypes = props.getProperty('types_not_searched')
    if not nsTypes:
        nsTypes = []
    else:
        nsTypes = list(nsTypes)
    for t in noSearchTypes:
        if t not in nsTypes:
            nsTypes.append(t)
    props.manage_changeProperties(types_not_searched = tuple(nsTypes))

    # configure CKEditor
    configureCKEditor(context, site)

    # configure safe_html portal transform
    configureSafeHtml(context, site)

    # adapt gestion-courrier directory
    configureMailDirectory(context, site)

    # configure Products.cron4plone
    # add a call to @@run-docsplit-on-blobs that will run docsplit on a batch of
    # CourrierFile and MeetingFile objects until all migrated content is converted.
    # add a call to @@parse-converted-files that will monthly check that all convertable
    # objects are converted and that all conversion results are still linked to existing
    # objects.
    cron_configlet = queryUtility(ICronConfiguration, 'cron4plone_config')
    if not cron_configlet.cronjobs:
        cron_configlet.cronjobs = CRON_TASKS
    else:
        addCron = True
        cronView = CRON_TASKS[0].split(' ')[-1]
        for cron in cron_configlet.cronjobs:
            cron = cron.split(' ')
            if cron[-1] == cronView:
                addCron = False
                break
        if addCron:
            for task in CRON_TASKS:
                cron_configlet.cronjobs.append(task)

def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotMeetingAndenneProfile(context): return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

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
           'meetingandenne.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']
    for resource in css:
        portal_css.moveResourceToBottom(resource)


##code-section FOOT
def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" %
                (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


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

def reorderSkinsLayers(context, site):
    """
       Re-apply sunburst cssregistry.xml step then plonemeetingskin and MeetingAndenne skins.xml step
       as the reinstallation of MeetingAndenne and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    site.portal_setup.runImportStepFromProfile(u'profile-plonetheme.sunburst:default', 'cssregistry')
    site.portal_setup.runImportStepFromProfile(u'profile-communesplone.layout:default', 'skins')
    site.portal_setup.runImportStepFromProfile(u'profile-plonetheme.imioapps:plonemeetingskin', 'skins')
    site.portal_setup.runImportStepFromProfile(u'profile-Products.PloneMeeting:default', 'skins')
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingAndenne:default', 'skins')

def reorderPortalTabs(context, site):
    """
       Re-apply MeetingAndenne actions.xml step as the reinstallation of
       MeetingAndenne and PloneMeeting changes the portal_tabs order and visibility
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("reorderPortalTabs", context)
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingAndenne:default', 'actions')

def reorderScriptsRegistry(context, site):
    """
       Re-apply plone.app.search jsregistry.xml step as the reinstallation of
       PloneMeeting disables Plone's advanced search by default
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("reorderScriptRegistry", context)
    site.portal_setup.runImportStepFromProfile(u'profile-plone.app.search:default', 'jsregistry')

def configureCKEditor(context, site):
    """
       Configure CKEditor properties correctly
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("configureCKEditor", context)
    properties = site.portal_properties.ckeditor_properties
    properties._updateProperty('toolbar', 'Custom')
    properties._updateProperty('toolbar_Custom', "\n[\n['Source','-','AjaxSave'],\n['Cut','Copy','Paste','PasteText','PasteFromWord','-', 'SpellChecker', 'Scayt'],\n['Undo','Redo','-','Find','Replace','-','SelectAll'],\n['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],\n['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],\n['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],\n['Image','Table','HorizontalRule','Smiley','SpecialChar'],\n['Maximize', 'ShowBlocks','-','About']\n]\n")
    properties._updateProperty('enableScaytOnStartup', True)

def configureSafeHtml(context, site):
    """
       Configure safe_html portal transform to filter tags and attributes correctly
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("configureSafeHtml", context)
    pt = site.portal_transforms

    if not 'safe_html' in pt.objectIds():
        logger.error('safe_html not registered in portal_transforms')
        return

    config = pt.safe_html._config
    config['class_blacklist'] = PersistentList()
    config['nasty_tags'] = PersistentMapping( { 'applet': '1', 'colgroup': '1', 'embed': '1', 'meta': '1', 'object': '1',
                                                'script' :'1', 'style': '1' } )
    config['remove_javascript'] = 1
    config['stripped_attributes'] = PersistentList( [ 'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'alt', 'axis',
                                                      'border', 'cellpadding', 'cellspacing', 'char', 'charoff', 'charset',
                                                      'checked', 'cite', 'class', 'clear', 'color', 'compact', 'coords', 'datetime',
                                                      'disabled', 'enctype', 'for', 'frame', 'headers', 'height', 'hreflang',
                                                      'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method',
                                                      'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly',
                                                      'rel', 'rev', 'rules', 'selected', 'shape', 'size', 'span', 'start',
                                                      'target', 'type', 'usemap', 'valign', 'value', 'vspace', 'width' ] )
    config['stripped_combinations'] = PersistentMapping()
    config['style_whitelist'] = PersistentList( [ 'text-align', 'list-style-type', 'float', 'width', 'height', 'padding-left',
                                                  'padding-right', 'margin', 'margin-left', 'margin-right' ] )
    config['valid_tags'] = PersistentMapping( { 'b': '1', 'blockquote': '1', 'br': '0', 'code': '1', 'dd': '1', 'del': '1',
                                                'dl': '1', 'dt': '1', 'em': '1', 'hgroup': '1', 'hr': '0', 'i': '1',
                                                'img': '0', 'ins': '1', 'li': '1', 'mark': '1', 'meta': '0', 'ol': '1',
                                                'p': '1', 'pre': '1', 's': '1', 'small': '1', 'strike': '1', 'strong': '1',
                                                'sub': '1', 'sup': '1', 'table': '1', 'tbody': '1', 'td': '1', 'tfoot': '1',
                                                'th': '1', 'thead': '1', 'tr': '1', 'tt': '1', 'u': '1', 'ul': '1' } )
    pt.reloadTransforms()

def configureMailDirectory(context, site):
    """
       We adapt the gestion-courrier Folder object at install time. See _adaptFrontPage in PloneMeeting setuphandlers.py file.
    """
    if isNotMeetingAndenneProfile(context):
        return

    logStep("configureMailDirectory", context)
    directory = getattr(site, 'gestion-courrier', None)
    if not directory:
        return

    if directory.modified() - directory.created() < 0.000005:
        if not directory.hasProperty('layout'):
            directory.manage_addProperty('layout', 'mailfolder_redirect_view', 'string')
        if not directory.hasProperty('meeting_config'):
            directory.manage_addProperty('meeting_config', 'courrierfake', 'string')

def installMeetingAndenne(context):
    """ Run the default profile before being able to run the Andenne profile"""
    if not isMeetingAndenneConfigureProfile(context):
        return

    logStep("installMeetingAndenne", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingAndenne:default')

def addToDoListTopics(context, site):
    """
       Add topics linked to MeetingConfigs to populate the ToDoList portlet
    """
    if not isMeetingAndenneConfigureProfile(context):
        return

    logStep("addToDoListTopics", context)
    mcCollege = getattr(site.portal_plonemeeting, 'meeting-config-college')
    mcCollege.setToDoListTopics(
        [ getattr(mcCollege.topics, 'searchallitemsincopy'),
          getattr(mcCollege.topics, 'searchitemstovalidate'),
          getattr(mcCollege.topics, 'searchallitemstoadvice'),
        ] )

def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if not isMeetingAndenneConfigureProfile(context):
        return

    logStep("initializeTool", context)
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()

def finalizeInstance(context):
    """
       Some parameters can not be handled by the PloneMeeting installation,
       so we handle this here
    """
    if not isMeetingAndenneConfigureProfile(context):
        return

    site = context.getSite()
    addToDoListTopics(context, site)
    reorderSkinsLayers(context, site)
    reorderCss(context)
    reorderPortalTabs(context, site)


##/code-section FOOT
