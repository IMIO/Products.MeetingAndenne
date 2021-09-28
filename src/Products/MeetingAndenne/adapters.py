# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2016 by CommunesPlone.org
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# ------------------------------------------------------------------------------

import cgi
import math
from appy.gen import No
from persistent.mapping import PersistentMapping
from zope.i18n import translate
from zope.interface import implements
from collections import OrderedDict
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import DisplayList
from Globals import InitializeClass
from Products.CMFPlone.utils import set_own_login_name, safe_unicode
from Products.CMFCore.permissions import ModifyPortalContent, ReviewPortalContent
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.memoize import ram
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from plone.app.users.browser.personalpreferences import PersonalPreferencesPanelAdapter
from imio.actionspanel.utils import unrestrictedRemoveGivenObject
from imio.helpers.xhtml import xhtmlContentIsEmpty
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE, \
     TOPIC_SEARCH_SCRIPT, TOPIC_SEARCH_FILTERS, TOPIC_TYPE, MEETINGREVIEWERS, NOT_GIVEN_ADVICE_VALUE, \
     DEFAULT_COPIED_FIELDS
from Products.PloneMeeting.Meeting import MeetingWorkflowActions, \
     MeetingWorkflowConditions, Meeting
from Products.PloneMeeting.MeetingItem import MeetingItem, \
     MeetingItemWorkflowConditions, MeetingItemWorkflowActions
from Products.PloneMeeting.MeetingCategory import MeetingCategory
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingFile import MeetingFile
from Products.PloneMeeting.MeetingFileType import MeetingFileType
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.ToolPloneMeeting import ToolPloneMeeting
from Products.PloneMeeting.adapters import AnnexableAdapter
from Products.PloneMeeting.interfaces import IMeetingCustom, IMeetingItemCustom, IMeetingCategoryCustom, \
                                             IMeetingConfigCustom, IMeetingFileCustom, \
                                             IMeetingFileTypeCustom, IMeetingGroupCustom, \
                                             IToolPloneMeetingCustom, IAnnexable
from Products.MeetingAndenne.interfaces import \
     IMeetingItemCollegeAndenneWorkflowActions, IMeetingItemCollegeAndenneWorkflowConditions, \
     IMeetingCollegeAndenneWorkflowActions, IMeetingCollegeAndenneWorkflowConditions, \
     IOCRLanguageCustom
from Products.MeetingAndenne.config import MAIL_TYPES, PERSONNEL_CATEGORIES, SMALLEST_SUBCATEGORY
from Products.MeetingAndenne.utils import *
from Products.MeetingAndenne.SearcherAndenne import SearcherAndenne
from Products.PloneMeeting import PMMessageFactory as _
from Products.PloneMeeting.utils import checkPermission, getCustomAdapter, prepareSearchValue, \
                                        FakeMeetingUser, weekdaysIds
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import WF_DOES_NOT_EXIST_WARNING, WF_APPLIED
from DateTime import DateTime

# Some imports added for the OCR functionalities
import os, os.path, unicodedata
import shutil
import ast
from collective.documentviewer.async import asyncInstalled
from collective.documentviewer.iso639_2_utf8 import ISO_UTF_MAP
from collective.documentviewer.convert import DocSplitSubProcess, DUMP_FILENAME, \
                                              TextCheckerSubProcess, textChecker, \
                                              Page, word_re

# Some imports added for the search functionalities
from plone.app.search.browser import Search, quote_chars, EVER
from Products.CMFPlone.browser.navtree import getNavigationRoot

# Some imports added for the safe_html transform patch
from lxml import etree, html
from lxml.html.clean import Cleaner
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.transforms.safe_html import SafeHTML, hasScript

import logging
logger = logging.getLogger( 'MeetingAndenne' )


# ------------------------------------------------------------------------------
# Names of available workflow adaptations.
customwfAdaptations = list(MeetingConfig.wfAdaptations)
# remove the 'creator_initiated_decisions' as this is always the case in our wfs
if 'creator_initiated_decisions' in customwfAdaptations:
    customwfAdaptations.remove('creator_initiated_decisions')
# remove the 'archiving' as we do not handle archive in our wfs
if 'archiving' in customwfAdaptations:
    customwfAdaptations.remove('archiving')
# remove the 'no_publication' as we do not handle publication in our wfs
if 'no_publication' in customwfAdaptations:
    customwfAdaptations.remove('no_publication')
# remove the 'hide_decision_when_under_writing' as we do not handle publication in our wfs
if 'no_publication' in customwfAdaptations:
    customwfAdaptations.remove('hide_decision_when_under_writing')


MeetingConfig.wfAdaptations = customwfAdaptations
originalPerformWorkflowAdaptations = adaptations.performWorkflowAdaptations

# states taken into account by the 'no_global_observation' wfAdaptation
from Products.PloneMeeting.model import adaptations
noGlobalObsStates = ('itemfrozen', 'accepted', 'accepted_and_closed', 'refused',
                     'refused_and_closed', 'delayed', 'delayed_and_closed',
                     'accepted_but_modified', 'accepted_but_modified_and_closed' 'pre_accepted')
adaptations.noGlobalObsStates = noGlobalObsStates

adaptations.RETURN_TO_PROPOSING_GROUP_FROM_ITEM_STATES = ('presented', 'itemfrozen', )
adaptations.RETURN_TO_PROPOSING_GROUP_MAPPINGS = {'backTo_presented_from_returned_to_proposing_group':
                                                  ['created', ],
                                                  'backTo_itemfrozen_from_returned_to_proposing_group':
                                                  ['frozen', 'decided', ],
                                                  'NO_MORE_RETURNABLE_STATES': ['closed', ]
                                                  }

adaptations.WF_NOT_CREATOR_EDITS_UNLESS_CLOSED = ('delayed_and_closed', 'refused_and_closed',
                                                  'accepted_and_closed', 'accepted_but_modified_and_closed')


def customPerformWorkflowAdaptations(site, meetingConfig, logger, specificAdaptation=None):
    '''This function applies workflow changes as specified by the
       p_meetingConfig.'''

    wfAdaptations = specificAdaptation and [specificAdaptation, ] or meetingConfig.getWorkflowAdaptations()

    #while reinstalling a separate profile, the workflow could not exist
    wfTool = getToolByName(site, 'portal_workflow')
    meetingWorkflow = getattr(wfTool, meetingConfig.getMeetingWorkflow(), None)
    if not meetingWorkflow:
        logger.warning(WF_DOES_NOT_EXIST_WARNING % meetingConfig.getMeetingWorkflow())
        return
    itemWorkflow = getattr(wfTool, meetingConfig.getItemWorkflow(), None)
    if not itemWorkflow:
        logger.warning(WF_DOES_NOT_EXIST_WARNING % meetingConfig.getItemWorkflow())
        return

    error = meetingConfig.validate_workflowAdaptations(wfAdaptations)
    if error:
        raise Exception(error)

    for wfAdaptation in wfAdaptations:
        # Call original perform of PloneMeeting
        originalPerformWorkflowAdaptations(site, meetingConfig, logger, specificAdaptation = wfAdaptation)

        if wfAdaptation in ['pre_validation_keep_reviewer_permissions', ]:
            # We override the PloneMeeting's 'pre_validation_keep_reviewer_permissions' wfAdaptation
            # We update the item workflow
            wf = itemWorkflow
            # Update connections between states and transitions
            wf.states['proposed'].setProperties(
                title='proposed', description='',
                transitions=['backToItemCreated', 'prevalidate', 'validate'])
            wf.states['prevalidated'].setProperties(
                title='prevalidated', description='',
                transitions=['backToProposed', 'validate'])
            wf.states['validated'].setProperties(
                title='validated', description='',
                transitions=['backToPrevalidated', 'present', 'backToProposed'])
            # use a specifig guard_expr 
            transition = wf.transitions['backToPrevalidated']
            transition.setProperties(
                title='backToPrevalidated',
                new_state_id='prevalidated', trigger_type=1, script_name='',
                actbox_name='backToPrevalidated', actbox_url='', actbox_category='workflow',
                props={'guard_expr': 'python:here.wfConditions().mayCorrect(toPrevalidated = True)'})
            logger.info(WF_APPLIED % ("pre_validation_keep_reviewer_permissions patched for MeetingAndenne", meetingConfig.getId()))

import Products.PloneMeeting.ToolPloneMeeting
Products.PloneMeeting.ToolPloneMeeting.performWorkflowAdaptations = customPerformWorkflowAdaptations
adaptations.performWorkflowAdaptations = customPerformWorkflowAdaptations


# ------------------------------------------------------------------------------
class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """

    def get_function(self):
        return safe_unicode(self.context.getProperty('function', ''))
    def set_function(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties( {'function': value} )
    function = property(get_function, set_function)

    def get_defaultref(self):
        return safe_unicode(self.context.getProperty('defaultref', ''))
    def set_defaultref(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties( {'defaultref': value} )
    defaultref = property(get_defaultref, set_defaultref)

    def get_gender(self):
        return self.context.getProperty('gender', '')
    def set_gender(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties( {'gender': value} )
    gender = property(get_gender, set_gender)

    def get_defaultgroup(self):
        return safe_unicode(self.context.getProperty('defaultgroup', ''))
    def set_defaultgroup(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties( {'defaultgroup': value} )
    defaultgroup = property(get_defaultgroup, set_defaultgroup)


# ------------------------------------------------------------------------------
class EnhancedPersonalPreferencesPanelAdapter(PersonalPreferencesPanelAdapter):
    """
    """
    def get_listed(self):
        return self.context.getProperty('listed', '')
    def set_listed(self, value):
        return self.context.setMemberProperties( {'listed': value} )
    listed = property(get_listed, set_listed)


# ------------------------------------------------------------------------------
class CustomOCRLanguageAdapter(object):
    '''Adapter that returns the object language.'''
    def __init__(self, context):
        self.context = context

    def getLanguage(self):
        '''Returns OCR language as 3-char language code.'''
        # First try to get the language assigned to the file
        lang = None
        if hasattr(self.context, 'ocrLanguage'):
            lang = getattr(self.context, 'ocrLanguage', None)
        if lang is None:
            if asyncInstalled():
                request = ast.literal_eval(self.context.saved_request)
                lang = request.get('ocr_language', None)
            else:
                lang = self.context.REQUEST.get('ocr_language', None)
        if lang is not None:
            return lang

        # Fallback to $OCR_LANGUAGE environment variable or site language
        lang = os.environ.get('OCR_LANGUAGE')
        if lang is None:
            lang = getToolByName(self.context, 'portal_languages').getPreferredLanguage()
            lang = ISO_UTF_MAP.get(lang[:2], 'fra')
        return lang


# ------------------------------------------------------------------------------
# Adapted to reflect the output of newer versions of pdffonts
TextCheckerSubProcess.font_line_marker = '%s %s %s --- --- --- ---------' % (
        '-' * 36, '-' * 17,'-' * 16)

# Contents function is monkey patched in order to remove accents for SearchableText to be filled properly
@property
def contents(self): 
    if os.path.exists(self.filepath):
        fi = open(self.filepath)
        text = fi.read()
        fi.close()
        # We replace é, à, ù,... by the NFKD unicode form which is the letter code followed by the accent code
        text = unicodedata.normalize('NFKD', unicode(text, encoding = 'utf-8'))
        # We replace special quotes characters (sometimes found in documents such as MS word files) and which are not ASCII
        text = text.replace(u"\u2019", u"\u0027")
        text = text.replace(u"\u2018", u"\u0027")
        text = text.replace(u"\u0060", u"\u0027")
        text = text.replace(u"\u00B4", u"\u0027")
        text = text.replace(u"\u201C", u"\u0022")
        text = text.replace(u"\u201D", u"\u0022")
        # We remove non ASCII characters and replace by spaces non alphanumeric characters  
        text = text.encode('ASCII', 'ignore')
        text = word_re.sub(' ', text).strip()
        return ' '.join( [word for word in text.split() if len(word) > 3] )
    return ''

Page.contents = contents

# Convert function is monkey patched in order to force OCR on PDF files even if some text is already present in the file
def convert(self, output_dir, inputfilepath=None, filedata=None,
            converttopdf=False, sizes=(('large', 1000),), enable_indexation=True,
            ocr=True, detect_text=True, format='gif', filename=None, language='eng'):
        if inputfilepath is None and filedata is None:
            raise Exception("Must provide either filepath or filedata params")

        path = os.path.join(output_dir, DUMP_FILENAME)
        if os.path.exists(path):
            os.remove(path)

        if inputfilepath is not None:
            # copy file to be able to work with.
            shutil.copy(inputfilepath, path)
        else:
            fi = open(path, 'wb')
            fi.write(filedata)
            fi.close()

        if converttopdf:
            self.convert_to_pdf(path, filename, output_dir)

        self.dump_images(path, output_dir, sizes, format, language)
        if enable_indexation and ocr and detect_text and textChecker is not None:
            if textChecker.has(path):
                logger.info('Text already present in pdf.')
                ### patched here to force OCR on PDF files
                file_extension = filename.split('.')[-1].lower()
                if file_extension == 'pdf':
                    logger.info("We'll run Tesseract though as we do not trust in pdf text.")
                else:
                    ocr = False
                    logger.info('Skipping the OCR step.')

        if enable_indexation:
            self.dump_text(path, output_dir, ocr, language)

        num_pages = self.get_num_pages(path)

        os.remove(path)
        return num_pages

DocSplitSubProcess.convert = convert


# ------------------------------------------------------------------------------
# filter_query function is monkey patched in order to add an asterisk after the
# text searched for so the given results are the same as those of the live
# search. Moreover, a functionality to search only in a selected field is added
# and another one to search only in objects linked to a given MeetingConfig.
def filter_query(self, query):
    request = self.request

    tool = getToolByName(self.context, 'portal_plonemeeting')
    catalog = getToolByName(self.context, 'portal_catalog')
    valid_indexes = tuple(catalog.indexes())
    valid_keys = self.valid_keys + valid_indexes

    text = query.get('SearchableText', None)
    if text is None:
        text = request.form.get('SearchableText', '')
    if not text:
        # Without text, must provide a meaningful non-empty search
        valid = set(valid_indexes).intersection(request.form.keys()) or \
            set(valid_indexes).intersection(query.keys())
        if not valid:
            return

    for k, v in request.form.items():
        if v and ((k in valid_keys) or k.startswith('facet.')):
            query[k] = v
    if text:
        # Add an asterisk
        query['SearchableText'] = quote_chars(text) + '*'

    # Add search only on specific fields functionality
    field = request.form.get('field', '')
    if field and field != 'all':
        query[field] = quote_chars(text) + '*'
        del query['SearchableText']

    # don't filter on created at all if we want all results
    created = query.get('created')
    if created:
        try:
            if created.get('query') and created['query'][0] <= EVER:
                del query['created']
        except AttributeError:
            # created not a mapping
            del query['created']

    # respect `types_not_searched` setting
    types = query.get('portal_type', [])
    if 'query' in types:
        types = types['query']
    query['portal_type'] = self.filter_types(types)
    # respect effective/expiration date
    query['show_inactive'] = False
    # respect navigation root
    if 'path' not in query:
        query['path'] = getNavigationRoot(self.context)
    # permit only filtering on types related to the MeetingConfig we are in
    query['path'] = tool.adapted().getSearchPathFromMeetingConfig(self.context, query)
    query['portal_type'] = tool.adapted().getSearchTypesFromMeetingConfig(self.context, query)

    return query

Search.filter_query = filter_query


# ------------------------------------------------------------------------------
# convert and scrub_html functions from PortalTransform3 are backported here
# in order to clean attributes in tags when the safe_html portal transform is
# applied on Rich Text Fields.
html.defs.safe_attrs = list(html.defs.safe_attrs) + ['style']
Cleaner.safe_attrs = html.defs.safe_attrs

# convert function is monkey patched in order to backport from PortalTransform3
def convert(self, orig, data, **kwargs):
    # note if we need an upgrade.
    if 'disable_transform' not in self.config:
        log(logging.ERROR, 'PortalTransforms safe_html transform needs '
            'to be updated. Please re-install the PortalTransforms '
            'product to fix.')

    # if we have a config that we don't want to delete
    # we need a disable option
    if self.config.get('disable_transform'):
        data.setData(orig)
    else:
        safe_html = self.scrub_html(orig)
        data.setData(safe_html)
    return data

SafeHTML.convert = convert

# scrub_html function is monkey patched in order to implement attributes cleaning
def scrub_html(self, orig):
    # append html tag to create a dummy parent for the tree
    html_parser = html.HTMLParser(encoding='utf-8')
    if '<html' in orig.lower():
        # full html
        tree = html.fromstring(orig, parser=html_parser)
        strip_outer = bodyfinder
    else:
        # partial html (i.e. coming from WYSIWYG editor)
        tree = html.fragment_fromstring(orig, create_parent=True, parser=html_parser)

        def strip_outer(s):
            return s[5:-6]

    for elem in tree.iter(etree.Element):
        if elem is not None:
            for attrib, value in elem.attrib.items():
                if hasScript(value):
                    del elem.attrib[attrib]
                else:
                    # strip css styles that are not part of style_whitelist
                    if attrib == "style":
                        newStyle = []
                        for style in value.split(';'):
                            styleDict = style.split(':')
                            if "".join(styleDict[0].split()).lower() in self.config['style_whitelist']:
                                newStyle.append(style)
                        elem.attrib[attrib] = ";".join(newStyle)

    valid_tags = [tag for tag, enabled in self.config['valid_tags'].items() if enabled]
    nasty_tags = [tag for tag, enabled in self.config['nasty_tags'].items() if enabled]
    safe_attrs = list(html.defs.safe_attrs) + ['style']

    for attr in self.config['stripped_attributes']:
        if attr in safe_attrs:
            safe_attrs.remove(attr)

    remove_script = self.config['nasty_tags'].get('script')

    cleaner = Cleaner(kill_tags=nasty_tags,
                      remove_tags=self.config.get('stripped_tags', []),
                      allow_tags=valid_tags,
                      page_structure=False,
                      safe_attrs_only=True,
                      safe_attrs=safe_attrs,
                      embedded=False,
                      remove_unknown_tags=False,
                      meta=False,
                      javascript=remove_script,
                      scripts=remove_script,
                      style=False)
    try:
        cleaner(tree)
    except AssertionError:
        # some VERY invalid HTML
        return ''
    # remove all except body or outer div
    return strip_outer(etree.tostring(tree, encoding='utf-8').strip())

SafeHTML.scrub_html = scrub_html


# ------------------------------------------------------------------------------
class CustomAnnexableAdapter(AnnexableAdapter):
    '''Adapter that adapts an annexable object implementing IItem to the
       interface IAnnexable.'''

    def addAnnex(self, idCandidate, annex_title, annex_file,
                 relatedTo, meetingFileTypeUID, **kwargs):
        '''This function is overridden to take into account the PV annex
           MeetingFileType'''
        # first of all, check if we can actually add the annex
        if relatedTo == 'item_decision':
            if not checkPermission("PloneMeeting: Write decision annex", self.context):
                raise Unauthorized
        elif relatedTo == 'item_pv':
            if not checkPermission("MeetingAndenne: Add pv annex", self.context):
                raise Unauthorized
        else:
            # we use the "PloneMeeting: Add annex" permission for item normal annexes and advice annexes
            if not checkPermission("PloneMeeting: Add annex", self.context):
                raise Unauthorized

        # if we can, proceed
        if not idCandidate:
            idCandidate = annex_file.filename
        # Split leading underscore(s); else, Plone argues that you do not have the
        # rights to create the annex
        idCandidate = idCandidate.lstrip('_')
        # Normalize idCandidate
        idCandidate = self.context.plone_utils.normalizeString(idCandidate)
        i = 0
        idMayBeUsed = False
        while not idMayBeUsed:
            i += 1
            if not self.isValidAnnexId(idCandidate):
                # We need to find another name (prepend a number)
                elems = idCandidate.rsplit('.', 1)
                baseName = elems[0]
                if len(elems) == 1:
                    ext = ''
                else:
                    ext = '.%s' % elems[1]
                idCandidate = '%s%d%s' % (baseName, i, ext)
            else:
                # Ok idCandidate is good!
                idMayBeUsed = True

        newAnnexId = self.context.invokeFactory('MeetingFile', id=idCandidate)
        newAnnex = getattr(self.context, newAnnexId)
        newAnnex.setFile(annex_file, **kwargs)
        newAnnex.setTitle(annex_title)
        newAnnex.setMeetingFileType(meetingFileTypeUID)

        # do some specific stuffs if we are adding an annex on an item, not on an advice
        if self.context.meta_type == 'MeetingItem':
            # Add the annex creation to item history
            self.context.updateHistory('add',
                                       newAnnex,
                                       decisionRelated=(relatedTo == 'item_decision'))
            # Invalidate advices if needed and adding a normal annex
            if relatedTo == 'item' and self.context.willInvalidateAdvices():
                self.context.updateAdvices(invalidate=True)

            # Potentially I must notify MeetingManagers through email.
            if self.context.wfConditions().meetingIsPublished():
                self.context.sendMailIfRelevant('annexAdded', 'MeetingManager', isRole=True)

        # After processForm that itself calls at_post_create_script,
        # current user may loose permission to edit
        # the object because we copy item permissions.
        newAnnex.processForm()
        # display a warning portal message if annex size is large
        if newAnnex.warnSize():
            self.context.plone_utils.addPortalMessage(_("The annex that you just added has a large size and could be "
                                                        "difficult to download by users wanting to view it!"),
                                                      type='warning')
        userId = self.context.portal_membership.getAuthenticatedMember().getId()
        logger.info('Annex at %s uploaded by "%s".' % (newAnnex.absolute_url_path(), userId))


# ------------------------------------------------------------------------------
class CustomMeetingAndenne(Meeting):
    '''Adapter that adapts a meeting object implementing IMeeting to the
       interface IMeetingCustom.'''
    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    ##### Functions used for template generation ############################

    security.declarePrivate('getReplacingUsers')
    def getReplacingUsers(self):
        repl = self.getSelf().getUserReplacements()
        res = []
        for present in repl.itervalues():
            res.append(present)
        return res

    security.declarePrivate('getReplacingUsersDict')
    def getReplacingUsersDict(self):
        repl = self.getSelf().getUserReplacements()
        res = {}
        for absent in repl.iterkeys():
            res[repl[absent]] = absent
        return res

    security.declarePublic('getDisplayableName')
    def getDisplayableName(self, withHour=True, uppercase=False, withDOW=False):
        '''Formats the name of a meeting in the way it is printed in templates.'''
        meeting = self.getSelf()
        date = meeting.getDate()
        res = ''

        if withDOW:
            dow = translate(weekdaysIds[date.dow()], domain='plonelocales',
                            target_language=getToolByName(self.context, 'portal_languages').getPreferredLanguage())
            res = dow.lower() + ' '

        if not withHour:
            res += meeting.portal_plonemeeting.formatMeetingDate(meeting=meeting, withHour=withHour)
        else:
            # Get the format for the rendering of p_aDate
            if date._hour or date._minute :
                fmt = ' (%-Hh%-M)'
                h = date.strftime(fmt)
            else:
                h = ''
            res += meeting.portal_plonemeeting.formatMeetingDate(meeting=meeting, withHour=False) + h

        if uppercase:
            return res.upper()
        return res

    Meeting.getDisplayableName = getDisplayableName
    # it'a a monkey patch because it's the only way to add a behaviour to the Meeting class

    security.declarePublic('getMeetingNumberForPrinting')
    def getMeetingNumberForPrinting(self):
        '''Formats the meeting number in the way it is printed in templates.'''
        meeting = self.getSelf()
        return "N° " + str(meeting.getDate().year()) + "/" + str(meeting.getMeetingNumber())

    security.declarePublic('getMeetingNumberInParliamentaryTermForPrinting')
    def getMeetingNumberInParliamentaryTermExponentForPrinting(self):
        '''Formats the meeting number in parliamentary term in the way it is printed in templates.'''
        meeting = self.getSelf()
        number = meeting.getMeetingNumberInParliamentaryTerm()
        if number == 1:
            return "ère"
        return "ème"

    security.declarePublic('getSignatoriesForPrinting')
    def getSignatoriesForPrinting (self, pos=0, level=0, useforpv=False, userepl=True):
        '''Gets the signatories to be printed in templates. Position is linked to the different signatories.
           For each signatory, level 0 is his duty and level 1 is his name.
           useforpv is used to manage the case where the mandatary's duty should be replaced by "Président".
           userepl is used to take replacements into account when selecting signatories and duties.'''
        meeting = self.getSelf()
        res = meeting.getSignatories(theObjects=True, includeDeleted=False, includeReplacements=userepl)

        if level == 1:
            return res[pos].Title()

        if pos == 0 and useforpv == True:
            repl = self.getReplacingUsers()
            if res[pos].id in repl:
                return "Président f.f."
            return "Président"

        return res[pos].getDuty()

    security.declarePublic('getCertifiedSignatures')
    def getCertifiedSignatures(self):
        '''Gets the certified signatures for this meeting. Always force computation with signatures
           defined in the related MeetingConfig object.'''
        meeting = self.getSelf()
        tool = getToolByName(meeting, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(meeting)
        return cfg.getCertifiedSignatures(computed=True)

    security.declarePublic('getStrikedAssembly')
    def getStrikedAssembly(self, groupByDuty=True):
        '''
          Generates a HTML version of the assembly :
          - strikes absents (represented using [[Member assembly name]]) except the general director
          - add a 'mltAssembly' class to generated <p> so it can be used in the Pod Template
          If p_groupByDuty is True, the result will be generated with members having the same
          duty grouped, and the duty only displayed once at the end of the list of members
          having this duty...  This is only relevant if MeetingUsers are enabled.
        '''
        meeting = self.getSelf()
        userReplacements = meeting.getUserReplacements()
        substitutes = {}
        for user in userReplacements:
            substitutes[userReplacements[user]] = user
        # either we use free textarea to define assembly...
        if meeting.getAssembly():
            tool = getToolByName(meeting, 'portal_plonemeeting')
            return tool.toHTMLStrikedContent(meeting.getAssembly())
        # ... or we use MeetingUsers
        elif meeting.getAttendees():
            res = []
            attendeesIds = meeting.getAttendees()
            groupedByDuty = OrderedDict()
            usedMeetingUsers = [mUser for mUser in meeting.getAllUsedMeetingUsers(usages=['assemblyMember','signer', ])]
            usedMeetingUsersMinusSubstitutesIds = [mUser.getId() for mUser in usedMeetingUsers if mUser.getId() not in substitutes]
            for mUser in usedMeetingUsers:
                userId = mUser.getId()
                userTitle = mUser.Title()
                userDuty = mUser.getDuty()
                if userId not in attendeesIds and userId == usedMeetingUsersMinusSubstitutesIds[-1]:
                    continue
                if userId in substitutes:
                    substitutedId = substitutes[userId]
                    userDuty = [mUser.getReplacementDuty() for mUser in usedMeetingUsers if mUser.getId() == substitutedId][0]

                if groupByDuty:
                    if not userDuty in groupedByDuty:
                        groupedByDuty[userDuty] = []
                    if userId in attendeesIds:
                        groupedByDuty[userDuty].append(userTitle)
                    else:
                        groupedByDuty[userDuty].append("<strike>%s</strike>" % userTitle)
                else:
                    if userId in attendeesIds:
                        res.append("%s, %s" % (userTitle, userDuty))
                    else:
                        res.append("<strike>%s, %s</strike>" % (userTitle, userDuty))
            if groupByDuty:
                for duty in groupedByDuty:
                    # check if every member of given duty are striked, we strike the duty also
                    everyStriked = True
                    for elt in groupedByDuty[duty]:
                        if not elt.startswith('<strike>'):
                            everyStriked = False
                            break
                    res.append(', '.join(groupedByDuty[duty]) + ', ' + duty)
                    if len(groupedByDuty[duty]) > 1:
                        # add a trailing 's' to the duty if several members have the same duty...
                        res[-1] = res[-1] + 's'
                    if everyStriked:
                        lastAdded = res[-1]
                        # strike the entire line and remove existing <strike> tags
                        lastAdded = "<strike>" + lastAdded.replace('<strike>', '').replace('</strike>', '') + \
                                    "</strike>"
                        res[-1] = lastAdded
            return "<p class='mltAssembly'>" + '<br />'.join(res) + "</p>"

    security.declarePublic('getAttendeesForPrinting')
    def getAttendeesForPrinting(self, groupByDuty=True):
        '''
          Generates a HTML version of the attendees in a Meeting.
        '''
        meeting = self.getSelf()
        # either we use free textarea to define assembly...
        if meeting.getAssembly():
            tool = getToolByName(meeting, 'portal_plonemeeting')
            return tool.toHTMLStrikedContent(meeting.getAssembly())
        # ... or we use MeetingUsers
        elif meeting.getAttendees():
            res = []
            attendees = meeting.getAttendees(theObjects = True, includeReplacements = True)
            groupedByDuty = OrderedDict()

            for mUser in attendees:
                userId = mUser.getId()
                userTitle = mUser.Title()
                userDuty = mUser.getDuty()
                if groupByDuty:
                    if not userDuty in groupedByDuty:
                        groupedByDuty[userDuty] = []
                    groupedByDuty[userDuty].append(mUser.Title())
                else:
                    res.append("%s, %s" % (mUser.Title(), userDuty))

            if groupByDuty:
                for duty in groupedByDuty:
                    res.append(', '.join(groupedByDuty[duty]) + ', ' + duty)
                    if len(groupedByDuty[duty]) > 1:
                        # add a trailing 's' to the duty if several members have the same duty...
                        res[-1] = res[-1] + 's'
            return "<p class='mltAssembly'>" + '<br />'.join(res) + "</p>"

    security.declarePublic('getAbsentsForPrinting')
    def getAbsentsForPrinting(self, absenceType='*'):
        '''Generates a HTML version of absents in a Meeting.'''
        meeting = self.getSelf()
        res = ''
        if absenceType not in ('*', 'absents', 'excused'):
            return res

        if absenceType == '*':
            absents = meeting.getAbsents(theObjects = True) + meeting.getExcused(theObjects = True)
        elif absenceType == 'absents':
            absents = meeting.getAbsents(theObjects = True)
        else:
            absents = meeting.getExcused(theObjects = True)

        if absents:
            res = "<p class='mltAssembly'>"
            for user in absents:
                res += "%s, %s<br />" % (user.Title(), user.getDuty())
            res += "</p>"
        return res


    ##### Taken from MeetingCommunes CustomMeeting adapter ##################

    security.declarePublic('getPrintableItemsByNumCategory')
    def getPrintableItemsByNumCategory(self, late=False, uids=[],
                                       catstoexclude=[], exclude=True, allItems=False):
        '''Returns a list of items ordered by category number. If there are many
           items by category, there is always only one category, even if the
           user have chosen a different order. If exclude=True , catstoexclude
           represents the category number that we don't want to print and if
           exclude=False, catsexclude represents the category number that we
           only want to print. This is useful when we want for exemple to
           exclude a personnal category from the meeting an realize a separate
           meeeting for this personal category. If allItems=True, we return
           late items AND items in order.'''

        itemsGetter = self.context.getItems
        if late:
            itemsGetter = self.context.getLateItems
        items = itemsGetter()
        if allItems:
            items = self.context.getItems() + self.context.getLateItems()
        user = self.context.portal_membership.getAuthenticatedMember()

        # res contains all items by category, the key of res being the category
        # number. Pay attention that the category number is obtained by extracting
        # the first 2 caracters of the category name, thus the categoryname must
        # be for example ' 2.travaux' or '10.Urbanisme. If not, the catnum takes
        # the value of the id + 1000 to be sure to place those categories at the
        # end.
        res = {}
        # First, we create the categories and for each category, we create a
        # dictionary that must contain the list of items in res[catnum][1]
        for item in items:
            if user.has_permission("View", item):

                if uids:
                    if (item.UID() in uids):
                        inuid = "ok"
                    else:
                        inuid = "ko"
                else:
                    inuid = "ok"
                if (inuid == "ok"):
                    current_cat = item.getCategory(theObject=True)
                    catNum = current_cat.adapted().getRootCatNum()
                    if catNum in res:
                        res[catNum][1][item.getItemNumber()] = item
                    else:
                        res[catNum] = {}
                        # first value of the list is the category object
                        res[catNum][0] = item.getCategory(True)
                        # second value of the list is a list of items
                        res[catNum][1] = {}
                        res[catNum][1][item.getItemNumber()] = item

        # Now we must sort the res dictionary with the key (containing catnum)
        # and copy it in the returned array.
        reskey = res.keys()
        reskey.sort()
        ressort = []
        for i in reskey:
            if catstoexclude:
                if (i in catstoexclude):
                    if exclude is False:
                        guard = True
                    else:
                        guard = False
                else:
                    if exclude is False:
                        guard = False
                    else:
                        guard = True
            else:
                guard = True

            if guard is True:
                k = 0
                ressorti = []
                ressorti.append(res[i][0])
                resitemkey = res[i][1].keys()
                resitemkey.sort()
                ressorti1 = []
                for j in resitemkey:
                    k = k+1
                    ressorti1.append([res[i][1][j], k])
                ressorti.append(ressorti1)
                ressort.append(ressorti)
        return ressort

    ##### End Taken from MeetingCommunes CustomMeeting adapter ###############


# ------------------------------------------------------------------------------
class CustomMeetingItemAndenne(MeetingItem):
    '''Adapter that adapts a meeting item object implementing IMeetingItem to
       the interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    ##### Begin Overrides MeetingCommunes MeetingItemCustom adapter #########

    def getIcons(self, inMeeting, meeting):
        '''Check docstring in PloneMeeting interfaces.py.'''
        item = self.getSelf()
        # Default PM item icons
        res = MeetingItem.getIcons(item, inMeeting, meeting)
        # display an icon if completeness yes/no
        itemCompleteness = item.getCompleteness()
        if itemCompleteness == 'completeness_complete':
            res.append(('completeness_complete.png', 'completeness_complete'))
        elif itemCompleteness == 'completeness_incomplete':
            res.append(('completeness_incomplete.png', 'completeness_incomplete'))
        # Add our icons for accepted_but_modified and pre_accepted
        itemState = item.queryState()
        if itemState == 'accepted_but_modified':
            res.append(('accepted_but_modified.png', 'icon_help_accepted_but_modified'))
        elif itemState == 'accepted_but_modified_and_closed':
            res.append(('accepted_but_modified.png', 'icon_help_accepted_but_modified'))
        elif itemState == 'delayed_and_closed':
            res.append(('delayed.png', 'icon_help_delayed'))
        elif itemState == 'pre_accepted':
            res.append(('pre_accepted.png', 'icon_help_pre_accepted'))
        elif itemState == 'refused_and_closed':
            res.append(('refused.png', 'icon_help_refused'))
        return res

    ##### End Overrides MeetingCommunes MeetingItemCustom adapter ###########

    ##### Functions used for template generation ############################

    security.declarePublic('getPrintableCopyTo')
    def getPrintableCopyTo(self):
        '''Formats the copyGroups field to print in the templates.'''
        groupsCopyTo = self.context.getCopyGroups()
        groupstr = ''
        if groupsCopyTo:
            for group in groupsCopyTo:
                ploneGroup = self.context.portal_groups.getGroupById(group)
                groupstr += ploneGroup.getProperty('title').split('(')[0][0:-1] + ', '
        if groupstr != '':
            return 'Copie(s): ' + groupstr[0:-2]
        else:
            return ''

    security.declarePublic('getPrintableNumCategory')
    def getPrintableNumCategory(self):
        '''Formats the category number to print only the root category number in the templates.'''
        current_cat = self.context.getCategory(theObject=True)
        return str(current_cat.adapted().getRootCatNum())

    security.declarePublic('getSignatoriesForPrinting')
    def getSignatoriesForPrinting (self, pos=0, level=0, useforpv=False, userepl=True):
        '''Gets the signatories to be printed in templates. Position is linked to the different signatories.
           For each signatory, level 0 is his duty and level 1 is his name.
           useforpv is used to manage the case where the mandatary's duty should be replaced by "Président".
           userepl is used to take replacements into account when selecting signatories and duties.'''
        item = self.getSelf()
        meeting = item.getMeeting()

        itemAttendees = item.getAttendees(includeReplacements=True)
        itemAttendeesIds = item.getAttendeesIds(attendees=itemAttendees)

        meetingAttendees = meeting.getAttendees(theObjects=True, includeDeleted=False, includeReplacements=True)
        replDict = meeting.adapted().getReplacingUsersDict()

        # The following part is used for rare cases where a signatory of the Meeting is absent for this
        # particular MeetingItem. So he must be replaced by the attendee following him in the attendees
        # list of the item who has to keep the replacementDuty given to the absent for the MeetingItem.
        res = item.getItemSignatories(theObjects=True, includeDeleted=False, includeReplacements=userepl)
        users = []
        for user in res:
            if user.id not in itemAttendeesIds:
                nextUser = False
                found = False
                for attendee in meetingAttendees:
                    if nextUser and attendee in itemAttendees:
                        if user.id in replDict:
                            user = getMeetingUser(item, replDict[user.id])
                        users.append(FakeMeetingUser(attendee.id, attendee, user))
                        replDict[attendee.id] = user.id
                        found = True
                        break
                    if attendee.id == user.id:
                        nextUser = True
                if not found:
                    users.append(user)
            else:
                users.append(user)
        res = users

        if level == 1:
            return res[pos].Title()

        if pos == 0 and useforpv == True:
            if res[pos].id in replDict:
                return "Président f.f."
            return "Président"

        return res[pos].getDuty()

    security.declarePublic('getStrikedItemAssembly')
    def getStrikedItemAssembly(self, groupByDuty=True):
        '''
          Generates a HTML version of the assembly :
          - strikes absents (represented using [[Member assembly name]]) except the general director
          - add a 'mltAssembly' class to generated <p> so it can be used in the Pod Template
          If p_groupByDuty is True, the result will be generated with members having the same
          duty grouped, and the duty only displayed once at the end of the list of members
          having this duty...  This is only relevant if MeetingUsers are enabled.
        '''
        item = self.getSelf()
        # either we use free textarea to define assembly...
        if item.getAssembly():
            tool = getToolByName(item, 'portal_plonemeeting')
            return tool.toHTMLStrikedContent(item.getItemAssembly())
        # ... or we use MeetingUsers
        elif item.getAttendees():
            res = []
            meeting = item.getMeeting()
            userReplacements = meeting.getUserReplacements()
            substitutes = {}
            for user in userReplacements:
                substitutes[userReplacements[user]] = user

            # Still something bad here as attendee.isPresent doesn't take itemPresents into account...
            attendees = meeting.getAttendees(True)
            attendeesIds = []
            for attendee in attendees:
                if attendee.isPresent(self.context, meeting) or attendee.getId() in self.context.getItemPresents():
                    attendeesIds.append(attendee.getId())

            groupedByDuty = OrderedDict()
            usedMeetingUsers = [mUser for mUser in meeting.getAllUsedMeetingUsers(usages=['assemblyMember','signer', ])]
            usedMeetingUsersMinusSubstitutesIds = [mUser.getId() for mUser in usedMeetingUsers if mUser.getId() not in substitutes]
            for mUser in usedMeetingUsers:
                userId = mUser.getId()
                userTitle = mUser.Title()
                userDuty = mUser.getDuty()
                if userId not in attendeesIds and userId == usedMeetingUsersMinusSubstitutesIds[-1]:
                    continue
                if userId in substitutes:
                    substitutedId = substitutes[userId]
                    userDuty = [mUser.getReplacementDuty() for mUser in usedMeetingUsers if mUser.getId() == substitutedId][0]

                if groupByDuty:
                    if not userDuty in groupedByDuty:
                        groupedByDuty[userDuty] = []
                    if userId in attendeesIds:
                        groupedByDuty[userDuty].append(userTitle)
                    else:
                        groupedByDuty[userDuty].append("<strike>%s</strike>" % userTitle)
                else:
                    if userId in attendeesIds:
                        res.append("%s, %s" % (userTitle, userDuty))
                    else:
                        res.append("<strike>%s, %s</strike>" % (userTitle, userDuty))
            if groupByDuty:
                for duty in groupedByDuty:
                    # check if every member of given duty are striked, we strike the duty also
                    everyStriked = True
                    for elt in groupedByDuty[duty]:
                        if not elt.startswith('<strike>'):
                            everyStriked = False
                            break
                    res.append(', '.join(groupedByDuty[duty]) + ', ' + duty)
                    if len(groupedByDuty[duty]) > 1:
                        # add a trailing 's' to the duty if several members have the same duty...
                        res[-1] = res[-1] + 's'
                    if everyStriked:
                        lastAdded = res[-1]
                        # strike the entire line and remove existing <strike> tags
                        lastAdded = "<strike>" + lastAdded.replace('<strike>', '').replace('</strike>', '') + \
                                    "</strike>"
                        res[-1] = lastAdded
            return "<p class='mltAssembly'>" + '<br />'.join(res) + "</p>"

        '''
          Generates a HTML version of the assembly :
          - strikes absents (represented using [[Member assembly name]])
          - add a 'mltAssembly' class to generated <p> so it can be used in the Pod Template
          If p_groupByDuty is True, the result will be generated with members having the same
          duty grouped, and the duty only displayed once at the end of the list of members
          having this duty...  This is only relevant if MeetingUsers are enabled.
        '''
        item = self.getSelf()
        meeting = item.getMeeting()
        repl = meeting.getUserReplacements()
        repl2 = []
        repl3 = {}
        for user in repl:
            repl2.append(repl[user])
            repl3[repl[user]] = user
        # either we use free textarea to define assembly...
        if item.getAssembly():
            tool = getToolByName(item, 'portal_plonemeeting')
            return tool.toHTMLStrikedContent(item.getItemAssembly())
        # ... or we use MeetingUsers
        elif item.getAttendees():
            res = []
            attendees = meeting.getAttendees(True)
            attendeeIds = []
            for user in attendees:
                if not ((not user.isPresent(self.context, meeting) and user.getId() not in self.context.getItemPresents()) or user.getId() in self.context.getItemAbsents()):
                    attendeeIds.append(user.getId())
            meeting.getAttendees()
            groupedByDuty = OrderedDict()
            m = 0
            UsedMeetingUsers = [mUser for mUser in meeting.getAllUsedMeetingUsers(usages=['assemblyMember', 'signer', ])] # ADDED BY FABMAR : just added signer for rongos from original
            UsedMeetingUsersMinusreplacedIds = [mUser.getId() for mUser in meeting.getAllUsedMeetingUsers(usages=['assemblyMember', 'signer', ]) if mUser.getId() not in repl2] # ADDED BY FABMAR
            for mUser in UsedMeetingUsers:
                ### ADDED BY FABMAR FROM ORIGINAL
                userId = mUser.getId()
                userTitle = mUser.Title()
                userDuty = mUser.getDuty()
                strikeme = True
                deleteme = False
                if userepl == True:
                    # ce members est-il a remplacer?
                    if userId in repl:
                        # Oui, il est a remplacer
                        # si on decide de barrer le membre, on ne va pas le faire remplacer, donc comportement par defaut, sinon, on essaye ou pas de trouver un remplaçant
                        if not ( (strikefirst == True and UsedMeetingUsersMinusreplacedIds.index(userId) == 0) \
                                 or (strikemidle == True and UsedMeetingUsersMinusreplacedIds.index(userId) > 0 and UsedMeetingUsersMinusreplacedIds.index(userId) < len(UsedMeetingUsersMinusreplacedIds) - 1) \
                                 or (strikelast == True and UsedMeetingUsersMinusreplacedIds.index(userId) == len(UsedMeetingUsersMinusreplacedIds) - 1)):
                            # on remplace le membre car on a pas décidé de le barrer, sinon comportement par defaut
                            userDuty = mUser.getReplacementDuty()
                            mUser = [mU for mU in UsedMeetingUsers if mU.getId() == repl[userId]][0]
                            strikeme = False
                            userId = mUser.getId()
                            userTitle = mUser.Title()
                    else:
                        # ce membre n'est pas à remplacer mais peut-être qu'il remplace quelqu'un qu'on n'a pas décidé de ne pas barrer (dans quel cas , il ne faut plus le faire apparaitre)
                        if userId in repl2 and not ((strikefirst == True and UsedMeetingUsersMinusreplacedIds.index(repl3[userId]) == 0) \
                                                    or (strikemidle == True and UsedMeetingUsersMinusreplacedIds.index(repl3[userId]) > 0 and UsedMeetingUsersMinusreplacedIds.index(repl3[userId]) < len(UsedMeetingUsersMinusreplacedIds)-1) \
                                                    or (strikelast == True and UsedMeetingUsersMinusreplacedIds.index(repl3[userId]) == len(UsedMeetingUsersMinusreplacedIds)-1)):
                            deleteme = True
                        else:
                            # ce membre n'est pas à remplacer et il ne remplace personne, on va juste verifier si il doit être barré ou pas
                            if not ((strikefirst == True and m == 0) or (strikemidle == True and m > 0 and m < len(UsedMeetingUsers)-1) or (strikelast == True and m == len(UsedMeetingUsers) - 1)):
                                # on n'a pas décidé de barrer donc il faut uniquement supprimer la personne sinon on a décidé de barrer le membre, c'est le comportement par défaut, on ne fait rien
                                if not userId in attendeeIds: # il faut juste verifier qu'il est bien absent avant de l'enlever
                                    deleteme = True
                else:
                    # il n'y a pas de remplacement, on regarde juste si on barre ou pas
                    if not ((strikefirst == True and m == 0) or (strikemidle == True and m > 0 and m < len(UsedMeetingUsers)-1) \
                            or (strikelast == True and m == len(UsedMeetingUsers) - 1)):
                        # on n'a pas décidé de barrer donc il faut uniquement supprimer la personne sinon on a décidé de barrer le membre, c'est le comportement par défaut, on ne fait rien
                        if not userId in attendeeIds: # il faut juste verifier qu'il est bien absent avant de l'enlever
                            deleteme = True
                #### END ADDED BY FABMAR

                # if we group by duty, create an OrderedDict where the key is the duty
                # and the value is a list of meetingUsers having this duty
                if not deleteme: ### ADDED BY FABMAR
                    if groupByDuty:
                        if not userDuty in groupedByDuty:
                            groupedByDuty[userDuty] = []
                        if userId in attendeeIds:
                            groupedByDuty[userDuty].append(mUser.Title())
                        else:
                            if strikeme:  #### ADDED BY FABMAR
                                groupedByDuty[userDuty].append("<strike>%s</strike>" % userTitle)
                            else:
                                groupedByDuty[userDuty].append(mUser.Title())
                    else:
                        if userId in attendeeIds:
                            res.append("%s, %s" % (mUser.Title(), userDuty))
                        else:
                            if strikeme:  #### ADDED BY FABMAR
                                res.append("<strike>%s, %s</strike>" % (mUser.Title(), userDuty))
                            else:
                                res.append("%s, %s" % (mUser.Title(), userDuty))
                m = m + 1
            if groupByDuty:
                for duty in groupedByDuty:
                    # check if every member of given duty are striked, we strike the duty also
                    everyStriked = True
                    for elt in groupedByDuty[duty]:
                        if not elt.startswith('<strike>'):
                            everyStriked = False
                            break
                    res.append(', '.join(groupedByDuty[duty]) + ', ' + duty)
                    if len(groupedByDuty[duty]) > 1:
                        # add a trailing 's' to the duty if several members have the same duty...
                        res[-1] = res[-1] + 's'
                    if everyStriked:
                        lastAdded = res[-1]
                        # strike the entire line and remove existing <strike> tags
                        lastAdded = "<strike>" + lastAdded.replace('<strike>', '').replace('</strike>', '') + \
                                    "</strike>"
                        res[-1] = lastAdded
            return "<p class='mltAssembly'>" + '<br />'.join(res) + "</p>"

    security.declarePublic('getItemAbsentsForPrinting') 
    def getItemAbsentsForPrinting(self):
        item = self.context.getSelf()
        res = ''
        meeting = item.getMeeting()
        attendees = meeting.getAttendees(True)
        for user in attendees:
            if (not user.isPresent(self.context, meeting) and user.getId() not in self.context.getItemPresents()) or user.getId() in self.context.getItemAbsents():
                res = "%s%s, %s%s" % (res, user.Title(), user.getDuty(), "<br />")
        if res != '':
            res= "%s%s%s" % ("<p class='mltAssembly'>", res, "</p>")
        return res

    security.declarePublic('getCurrentDate')
    def getCurrentDate(self):
        '''Formats the current date to print in the templates.'''
        return DateTime().strftime("%d/%m/%Y")

    security.declarePublic('printAdvicesInfos')
    def printAdvicesInfos(self,
                          withAdvicesTitle=True,
                          withDelay=False,
                          withDelayLabel=True,
                          withAuthor=True):
        '''Helper method to have a printable version of advices.'''
        # bbb compatible fix, as printAdvicesInfos was defined in a profile before...
        self = self.context.getSelf()
        membershipTool = getToolByName(self, 'portal_membership')
        itemAdvicesByType = self.getAdvicesByType()
        res = "<p class='pmAdvices'>"
        
        for adviceType in itemAdvicesByType:
            for advice in itemAdvicesByType[adviceType]:
                # if we have a delay and delay_label, we display it
                delayAwareMsg = u''
                if withDelay and advice['delay']:
                        delayAwareMsg = u"%s" % (translate('delay_of_x_days',
                                                 domain='PloneMeeting',
                                                 mapping={'delay': advice['delay']},
                                                 context=self.REQUEST))
                if withDelayLabel and advice['delay'] and advice['delay_label']:
                        if delayAwareMsg:
                            delayAwareMsg = "%s - %s" % (delayAwareMsg,
                                                         unicode(advice['delay_label'], 'utf-8'))
                        else:
                            delayAwareMsg = "%s" % unicode(advice['delay_label'], 'utf-8')
                if delayAwareMsg:
                    delayAwareMsg = u"(%s)" % cgi.escape(delayAwareMsg)
                    msg = u"%s" % delayAwareMsg
                else:
                    msg = u""

                # display the author if advice was given
                if withAuthor and not adviceType == NOT_GIVEN_ADVICE_VALUE:
                    adviceObj = getattr(self, advice['advice_id'])
                    author = membershipTool.getMemberInfo(adviceObj.Creator())
                    res = res + u"<b><u>%s %s, %s le %s %s</u></b><br/>" % (translate('Advice given by',
                                                                  domain='PloneMeeting',
                                                                  context=self.REQUEST),
                                                                  cgi.escape(unicode(author['fullname'], 'utf-8')),cgi.escape(advice['name']),cgi.escape(advice['advice_given_on_localized']),msg)
                else:
                    if withAdvicesTitle:
                        res += "<u><b>%s</b></u><br/>" % translate('PloneMeeting_label_advices',
                                                          domain='PloneMeeting',
                                                          context=self.REQUEST)
                # add advice type
                res = res + u"<br/><i>--%s--</i><br/>" % (translate([advice['type']][0],
                                                                        domain='PloneMeeting',
                                                                        context=self.REQUEST), )
                adviceComment = 'comment' in advice and advice['comment'] or '-'
                res = res + (u"<br/><u>%s :</u>%s" % (translate('Advice comment',
                                                                         domain='PloneMeeting',
                                                                         context=self.REQUEST),
                                                               unicode(adviceComment, 'utf-8')))
        if not itemAdvicesByType:
            res += '-'
        res += u"</p>"

        return res.encode('utf-8')

    ### New functionalities ###

    security.declarePublic('updateMeetingItem')
    def updateMeetingItem(self):
        """
           Update a MeetingItem object following a copygroups on-the-fly modification.
        """
        self.updateLocalRoles()
        self.adapted().onEdit(isCreated=False)
        self.reindexObject()

    MeetingItem.updateMeetingItem = updateMeetingItem
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePublic('getDocReference')
    def getDocReference(self):
        '''Return a too complicated item reference to be defined as a TAL Expression
           (field MeetingConfig.itemReferenceFormat.'''
        membershipTool = getToolByName(self, 'portal_membership')
        User=membershipTool.getAuthenticatedMember()
        Docref=User.getProperty('defaultref')
        if Docref:
            return Docref+ '/' + DateTime(self.CreationDate()).strftime('%Y.%m') + '.'
        else:
            userMeetingGroups = self.portal_plonemeeting.getGroupsForUser(suffix="creators")
            if len(userMeetingGroups) >= 1:
                ref = userMeetingGroups[-1].getAcronym()
            else:
                ref = 'XXXX'
            return ref + '/XX.XX/' + DateTime(self.CreationDate()).strftime('%Y.%m') + '.'

    MeetingItem.getDocReference = getDocReference
    # it'a a monkey patch because it's the only way to have a default method in the schema

    security.declarePublic('getDefaultProposingGroup')
    def getDefaultProposingGroup(self):
        '''Return a default proposing group to fill the proposing group field on item creation 
           (usefull when there is more than 1 proposing group) '''
        tool = getToolByName(self, 'portal_plonemeeting')
        membershipTool = getToolByName(self, 'portal_membership')
        User=membershipTool.getAuthenticatedMember()
        ProposingGroup=User.getProperty('defaultgroup')
        isDefinedInTool = self.isDefinedInTool()
        # bypass for Managers, pass idDefinedInTool to True so Managers
        # can select any available MeetingGroup
        isManager = tool.isManager(self, realManagers=True)
        res = tool.getSelectableGroups(isDefinedInTool=(isDefinedInTool or isManager))
        if ProposingGroup and ProposingGroup in [g[0] for g in res] :
        #and ProposingGroup in self.listProposingGroups(): 
           return ProposingGroup
        else:
           return None

    MeetingItem.getDefaultProposingGroup = getDefaultProposingGroup
    # it'a a monkey patch because it's the only way to have a default method in the schema

    security.declarePublic('listTreatUsers')
    def listTreatUsers(self):
        '''Lists the Users that are associated to the proposing group(s) of the authenticated user.'''
        userCreatorGroups = self.portal_plonemeeting.getGroupsForUser(suffix="creators", userId = self.Creator(), zope=True)

        res = set()
        for group in userCreatorGroups:
            for user in group.getMemberIds():
                res.add( (user, self.portal_membership.getMemberById(user).getProperty('fullname')) )
        res = sorted(res, key=collateDisplayListsValues)

        return DisplayList( tuple(res) )

    MeetingItem.listTreatUsers = listTreatUsers
    # it'a a monkey patch because it's the only way to have a default method in the schema

    security.declarePublic('listItemSignatories')
    def listItemSignatories(self):
        '''Returns a list of available signatories for the item.'''
        res = []
        if self.hasMeeting():
            # Get IDs of attendees
            for m in self.getMeeting().getAllUsedMeetingUsers(usages=['signer', ],includeAllActive=True): ### MODIFIED To display all signer and not only the present (use in meetingitemcollege_edit to display the signer list)
                if 'signer' in m.getUsages():
                    res.append((m.id, m.Title()))
        return DisplayList(tuple(res))

    MeetingItem.listItemSignatories = listItemSignatories
    # it'a a monkey patch because it's the only way to have a default method in the schema

    security.declarePublic('listProposingGroups')
    def listProposingGroups(self):
        '''Return the sorted MeetingGroup(s) that may propose this item. If no group is
           set yet, this method returns the MeetingGroup(s) the user belongs
           to. If a group is already set, it is returned.
           If this item is being created or edited in portal_plonemeeting (as a
           recurring item), the list of active groups is returned.'''
        tool = getToolByName(self, 'portal_plonemeeting')
        groupId = self.getField('proposingGroup').get(self)
        isDefinedInTool = self.isDefinedInTool()
        # bypass for Managers, pass idDefinedInTool to True so Managers
        # can select any available MeetingGroup
        isManager = tool.isManager(self, realManagers=True)
        res = tool.getSelectableGroups(isDefinedInTool=(isDefinedInTool or isManager),
                                       existingGroupId=groupId)
        res = sorted(res, key=collateDisplayListsValues)
        # add a 'make_a_choice' value when the item is in the tool
        if isDefinedInTool:
            res.insert(0, ('', translate('make_a_choice',
                           domain='PloneMeeting',
                           context=self.REQUEST)))
        return DisplayList(tuple(res))

    MeetingItem.listProposingGroups = listProposingGroups
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declarePublic('listCopyGroups')
    def listCopyGroups(self):
        '''Lists the groups that will be selectable to be in copy for this
           item.'''
        cfg = self.portal_plonemeeting.getMeetingConfig(self)
        res = []
        for groupId in cfg.getSelectableCopyGroups():
            group = self.portal_groups.getGroupById(groupId)
            res.append((groupId, group.getProperty('title')))

        # make sure groups already selected for the current item
        # and maybe not in the vocabulary are added to it so
        # the field is correctly displayed while editing/viewing it
        copyGroups = self.getCopyGroups()
        if copyGroups:
            copyGroupsInVocab = [copyGroup[0] for copyGroup in res]
            for groupId in copyGroups:
                if not groupId in copyGroupsInVocab:
                    group = self.portal_groups.getGroupById(groupId)
                    if group:
                        res.append((groupId, group.getProperty('title')))
                    else:
                        res.append((groupId, groupId))
        res = sorted(res, key=collateDisplayListsValues)

        return DisplayList(tuple(res))

    MeetingItem.listCopyGroups = listCopyGroups
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declarePublic('listAssociatedGroups')
    def listAssociatedGroups(self):
        '''Lists the groups that are associated to the proposing group(s) to
           propose this item. Return groups that have at least one creator,
           excepted if we are on an archive site.'''
        cfg = self.portal_plonemeeting.getMeetingConfig(self)
        res = []
        for groupId in cfg.getSelectableAssociatedGroups():
            group = self.portal_groups.getGroupById(groupId)
            res.append((groupId, group.getProperty('title')))

        # make sure associatedGroups actually stored have their corresponding
        # term in the vocabulary, if not, add it
        associatedGroups = self.getAssociatedGroups()
        if associatedGroups:
            associatedGroupsInVocab = [associatedGroup[0] for associatedGroup in res]
            for groupId in associatedGroups:
                if not groupId in associatedGroupsInVocab:
                    group = self.portal_groups.getGroupById(groupId)
                    if group:
                        res.append((groupId, group.getProperty('title')))
                    else:
                        res.append((groupId, groupId))
        res = sorted(res, key=collateDisplayListsValues)

        return DisplayList(tuple(res)).sortedByValue()

    MeetingItem.listAssociatedGroups = listAssociatedGroups
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    MeetingItem.originalClone = MeetingItem.clone

    security.declarePublic('customClone')
    def customClone(self, copyAnnexes=True, newOwnerId=None, cloneEventAction=None,
                    destFolder=None, copyFields=DEFAULT_COPIED_FIELDS, newPortalType=None,
                    keepProposingGroup=False):
        '''Clones the item in the PloneMeetingFolder of the current user, or p_newOwnerId if given.
           This custom version removes the PV annexes if any as duplicating them is not coherent.'''
        newItem = self.originalClone(copyAnnexes, newOwnerId, cloneEventAction, destFolder, copyFields,
                           newPortalType, keepProposingGroup)
        for annex in newItem.objectValues('MeetingFile'):
            if annex.findRelatedTo() == 'item_pv':
                unrestrictedRemoveGivenObject(annex)

        return newItem

    MeetingItem.clone = customClone
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declarePublic('getAttendees')
    def getAttendees(self, usage=None, includeDeleted=False,
                     includeAbsents=False, includeReplacements=False):
        '''Returns the attendees for this item. Takes into account
           self.itemAbsents, excepted if p_includeAbsents is True. It also
           takes into account self.itemPresents. If a given
           p_usage is defined, the method returns only users having this
           p_usage.'''
        res = []
        if usage == 'signer':
            raise 'Please use MeetingItem.getItemSignatories instead.'
        if not self.hasMeeting():
            return res
        # Prevent wrong parameters use
        if includeDeleted and usage:
            includeDeleted = False
        itemAbsents = ()
        itemPresents = self.getItemPresents()
        meeting = self.getMeeting()
        if not includeAbsents:
            # item absents are absents for the item, absents from an item before this one
            # and lateAttendees that still not arrived
            itemAbsents = list(self.getItemAbsents()) + meeting.getDepartures(self, when='before', alsoEarlier=True)
        # remove lateAttendees that arrived before this item
        lateAttendees = meeting.getLateAttendees()
        arrivedLateAttendees = meeting.getEntrances(self, when='during') + meeting.getEntrances(self, when='before')
        stillNotArrivedLateAttendees = set(lateAttendees).difference(set(arrivedLateAttendees))
        itemAbsents = itemAbsents + list(stillNotArrivedLateAttendees)
        for attendee in meeting.getAttendees(True,
                                             includeDeleted=includeDeleted,
                                             includeReplacements=includeReplacements):
            if attendee.id in itemAbsents and attendee.id not in itemPresents:
                continue
            if not usage or (usage in attendee.getUsages()):
                res.append(attendee)
        return res

    MeetingItem.getAttendees = getAttendees
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declarePublic('getAttendeesIds')
    def getAttendeesIds(self, usage=None, includeDeleted=False,
                     includeAbsents=False, includeReplacements=False,
                     attendees=None):
        '''Returns the attendees ids for this item. Takes into account
           self.itemAbsents, excepted if p_includeAbsents is True. It also
           takes into account self.itemPresents. If a given
           p_usage is defined, the method returns only users having this
           p_usage. If an array of attendees in passed in argument, the
           ids are simply extracted from this array.'''
        res = []
        if attendees is None:
            attendees = self.getAttendees(usage, includeDeleted, includeAbsents, includeReplacements)
        for attendee in attendees:
            res.append(attendee.id)
        return res

    MeetingItem.getAttendeesIds = getAttendeesIds
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declareProtected('Modify portal content', 'onWelcomePerson')
    def onWelcomePerson(self):
        '''Some user (in request.userId) has joined the meeting:
           1) either a late attendee just before discussion on this item
             (request.welcomeType == 'from_now'),
           2) or just during the discussion on this particular item
             (request.welcomeType == 'just_now').
           We will record this info, except if request["action"] tells us to
           remove it instead.'''
        tool = getToolByName(self, 'portal_plonemeeting')
        if not tool.isManager(self) or not checkPermission(ModifyPortalContent, self):
            raise Unauthorized
        rq = self.REQUEST
        userId = rq['userId']
        mustDelete = rq.get('actionType') == 'delete'
        if rq['welcomeType'] == 'from_now':
            # Case 1)
            meeting = self.getMeeting()
            if mustDelete:
                del meeting.entrances[userId]
            else:
                if not hasattr(meeting.aq_base, 'entrances'):
                    meeting.entrances = PersistentMapping()
                meeting.entrances[userId] = self.getItemNumber(relativeTo='meeting')
        else:
            # Case 2)
            presents = list(self.getItemPresents())
            if mustDelete:
                presents.remove(userId)
            else:
                presents.append(userId)
            self.setItemPresents(presents)

    MeetingItem.onWelcomePerson = onWelcomePerson
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declarePublic('mayAskEmergency')
    def mayAskEmergency(self):
        '''Returns True if current user may ask emergency for an item.'''
        # in our case, only MeetingManagers may ask emergency
        item = self.getSelf()
        if item.isDefinedInTool():
            return False

        tool = getToolByName(item, 'portal_plonemeeting')
        membershipTool = getToolByName(item, 'portal_membership')
        member = membershipTool.getAuthenticatedMember()
        if tool.isManager(item) and member.has_permission(ModifyPortalContent, item):
            return True
        return False

    security.declarePublic('mayAcceptOrRefuseEmergency')
    def mayAcceptOrRefuseEmergency(self):
        '''Returns True if current user may accept or refuse emergency if asked for an item.'''
        # in our case, only MeetingManagers can accept or refuse emergency
        item = self.getSelf()
        tool = getToolByName(item, 'portal_plonemeeting')
        membershipTool = getToolByName(item, 'portal_membership')
        member = membershipTool.getAuthenticatedMember()
        if tool.isManager(item) and member.has_permission(ModifyPortalContent, item):
            return True
        return False

    security.declarePublic('getExtraFieldsToCopyWhenCloning')
    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc):
        '''Lists the fields to keep when cloning an item'''
        return ['projetpv', 'textpv', 'pv']

    security.declarePrivate('replaceBr')
    def replaceBr (self,text):
        description = text
        if description == "":
            description = "<html></html>"
        pos = description.find("<br />")
        while pos <> -1 :
            ol = description.count("<ol>", 0, pos)
            ul = description.count("<ul>", 0, pos)
            li = description.count("<li>", 0, pos)
            sol = description.count("</ol>", 0, pos)
            sul = description.count("</ul>", 0, pos)
            sli = description.count("</li>", 0, pos)
            if ol <= sol and ul <= sul and li <= sli:
                p = description.count("<p", 0, pos)
                sp = description.count("</p>", 0, pos)

                if p > sp:
                    strong = description.rfind ("<strong>", 0, pos)
                    strike = description.rfind("<strike>", 0, pos)
                    u = description.rfind("<u>", 0, pos)
                    em = description.rfind("<em>", 0, pos)
                    sup = description.rfind("<sup>", 0, pos)
                    sub = description.rfind("<sub>", 0, pos)
                    font = description.rfind("<font", 0, pos)
                    span = description.rfind("<span", 0, pos)
                    sstrong = description.rfind("</strong>", 0, pos)
                    sstrike = description.rfind("</strike>", 0, pos)
                    su = description.rfind("</u>", 0, pos)
                    sem = description.rfind("</em>", 0, pos)
                    ssub = description.rfind("</sub>", 0, pos)
                    ssup = description.rfind("</sup>", 0, pos)
                    sfont = description.rfind("</font>", 0, pos)
                    sspan = description.rfind("</span>", 0, pos)
                    htmltuple = []
                    if strong > sstrong:
                        htmltuple.append( ("<strong>", "</strong>", strong) )
                    if strike > sstrike:
                        htmltuple.append( ("<strike>", "</strike>", strike) )
                    if u > su:
                        htmltuple.append( ("<u>", "</u>", u) )
                    if em > sem:
                        htmltuple.append( ("<em>", "</em>", em) )
                    if sup > ssup:
                        htmltuple.append( ("<sup>", "</sup>", sup) )
                    if sub > ssub:
                        htmltuple.append( ("<sub>", "</sub>", sub) )
                    if font > sfont:
                        htmltuple.append( ("<font>", "</font>", font) )
                    if span > sspan:
                        htmltuple.append( ("<span>", "</span>", span) )

                    htmltupleclose = sorted(htmltuple, key=lambda tag: tag[2], reverse = True)
                    htmltupleopen = sorted(htmltuple, key=lambda tag: tag[2])
                    strhtmlclose = ""
                    strhtmlopen = ""
                    for i in htmltupleclose:
                        strhtmlclose += i[1]
                    for i in htmltupleopen:
                        strhtmlopen += i[0]
                    description = description.replace("<br />", strhtmlclose + "</p><p>" + strhtmlopen, 1)
                else:
                    description = description.replace("<br />", "<p>&nbsp;</p>", 1)
            else:
                description = description.replace("<br />", "", 1)
            pos = description.find("<br />")

        pos = description.find("<table")
        while pos <> -1:
            tdend = description.find("</table", pos)
            if description.count("<p", pos, tdend) > 0:
                l = list(description)
                l[pos:tdend] = list(description[pos:tdend].replace("<p", "<span", 10).replace("</p>", "</span>", 10))
                description = "".join(l)
            pos = description.find("<table", pos+1 )

        return description

    security.declarePublic('onEdit')
    def onEdit(self, isCreated):
        tool = self.context.portal_plonemeeting

        # replace div by p, because xhtmlparlser convert div to page-break and it causes problems in text align justify
        # replace line breaks by </p><p> because line breaks are in <p> and causes justify problems
        #description = self.context.Description()
        #self.context.setDescription(self.context.replaceBr(description))

        #decision = self.context.getDecision()
        #self.context.setDecision(self.context.replaceBr(decision))

        #projetpv = self.context.getProjetpv()
        #self.context.setProjetpv(self.context.replaceBr(projetpv))

        #textpv = self.context.getTextpv()
        #self.context.setTextpv(self.context.replaceBr(textpv))

        #pv = self.context.getPv()
        #self.context.setPv(self.context.replaceBr(pv))

        # Add local roles corresponding to the proposing group if item category is personnel or if item is confidential
        category = self.context.getCategory(theObject=True)
        if category == '':
            itemCatNum = 0
        else:
            itemCatNum = category.adapted().getRootCatNum()

        personnel = itemCatNum in PERSONNEL_CATEGORIES
        if personnel or self.context.getIsconfidential() == True:
            meetingGroup = getattr(tool, self.context.getProposingGroup(), None)
            personnelGroup = getattr(tool, "personnel", None)
            cfg = tool.getMeetingConfig(self.context)
            adaptations = cfg.getWorkflowAdaptations()

            if self.context.getIsconfidential() == True:
                MEETINGROLESTOREMOVE = ('prereviewers', 'reviewers', 'observers', 'creators')
                MEETINGROLESTOADD = dict()
            else:
                MEETINGROLESTOREMOVE = ('prereviewers', 'reviewers')
                MEETINGROLESTOADD = { 'MeetingObserverLocal': ( personnelGroup, 'observers' ), }

            if 'pre_validation_keep_reviewer_permissions' in adaptations and meetingGroup.getUsePrevalidation():
                MEETINGROLESTOADD['MeetingReviewer'] = ( meetingGroup, 'reviewers' )
                if personnel:
                    MEETINGROLESTOADD['MeetingPreReviewer'] = ( personnelGroup, 'prereviewers' )
                    if self.context.getIsconfidential() == True:
                        MEETINGROLESTOADD['MeetingObserverLocal'] = ( meetingGroup, 'prereviewers' )
                else:
                    MEETINGROLESTOADD['MeetingPreReviewer'] = ( meetingGroup, 'prereviewers' )
            else:
                MEETINGROLESTOADD['MeetingPreReviewer'] = ( meetingGroup, 'prereviewers' )
                if personnel:
                    MEETINGROLESTOADD['MeetingReviewer'] = ( personnelGroup, 'reviewers' )
                    if self.context.getIsconfidential() == True:
                        MEETINGROLESTOADD['MeetingObserverLocal'] = ( meetingGroup, 'reviewers' )
                else:
                    MEETINGROLESTOADD['MeetingReviewer'] = ( meetingGroup, 'reviewers' )

            # Remove the locale roles
            for groupSuffix in MEETINGROLESTOREMOVE:
                groupId = meetingGroup.getPloneGroupId(groupSuffix)
                # If the corresponding Plone group does not exist anymore,
                # recreate it.
                ploneGroup = self.context.portal_groups.getGroupById(groupId)
                if not ploneGroup:
                    meetingGroup._createPloneGroup(groupSuffix)
                self.context.manage_delLocalRoles((groupId, ))

            # Add the local roles
            for role, groupData in MEETINGROLESTOADD.items():
                groupId = groupData[0].getPloneGroupId(groupData[1])
                # If the corresponding Plone group does not exist anymore,
                # recreate it.
                ploneGroup = self.context.portal_groups.getGroupById(groupId)
                if not ploneGroup:
                    groupData[0]._createPloneGroup(groupData[1])
                self.context.manage_addLocalRoles(groupId, (role, ))
        #add local role for associated group
        assGroups = self.context.getAssociatedGroups()
        if assGroups:
            for assGroup in assGroups:
                self.context.manage_addLocalRoles(assGroup, ('MeetingMember','Owner'))

    security.declarePublic('getLatestReviewer')
    def getLatestReviewer(self):
        '''Returns the user of the latest validate action that was performed on this item or
           the creator if the history is incomplete.'''
        item = self.getSelf()
        wfName = item.portal_workflow.getWorkflowsFor(item)[0].getId()
        if wfName in item.workflow_history:
            objectHistory = item.workflow_history[wfName]
            i = len(objectHistory) - 1
            while i >= 0:
                if objectHistory[i]['action'] == 'validate':
                    return objectHistory[i]['actor']
                i -= 1
        return item.Creator()

    security.declarePublic('onDuplicate')
    def onDuplicate(self):
        '''This method is triggered when the users clicks on
           "duplicate item".'''
        user = self.portal_membership.getAuthenticatedMember()
        newItem = self.clone(newOwnerId=user.id, cloneEventAction='Duplicate')
        if (user.has_permission('MeetingAndenne: Read pv', self)):
            if not newItem.fieldIsEmpty('textpv'):
                newItem.setDecision(self.getTextpv())
            if not newItem.fieldIsEmpty('pv'):
                newItem.setProjetpv(self.getPv())

        newItem.setTreatUser(user.id)
        newItem.itemPresents = ()
        newItem.itemSignatories = ()
        newItem.itemAbsents = ()

        tool = self.portal_plonemeeting
        cfg = tool.getMeetingConfig(self)
        if cfg.getUseSubCategories():
            cat = newItem.getCategory(theObject=True)
            if cat and cat.adapted().getRootCatNum() < SMALLEST_SUBCATEGORY:
                newItem.category = ''

        newItem.reindexObject(idxs=['getTreatUser', 'Description', 'getDecision', 'getProjetpv', 'getTextpv', 'getPv'])
        self.plone_utils.addPortalMessage(
            translate('item_duplicated', domain='PloneMeeting', context=self.REQUEST))
        return self.REQUEST.RESPONSE.redirect(newItem.absolute_url())

    MeetingItem.onDuplicate = onDuplicate
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    def showAnnexesTab_cachekey(method, self, decisionRelated=False, pvRelated=False):
        '''cachekey method for self.showAnnexesTab.'''
        return (str(self.REQUEST.debug), decisionRelated, pvRelated)

    MeetingItem.showAnnexesTab_cachekey = showAnnexesTab_cachekey
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    security.declarePublic('showAnnexesTab')
    @ram.cache(showAnnexesTab_cachekey)
    def showAnnexesTab(self, decisionRelated=False, pvRelated=False):
        '''Must we show the "Annexes" (or "Decision-related annexes" or "PV-related annnexes") tab ?'''
        if self.isTemporary() or self.isDefinedInTool():
            return False
        tool = getToolByName(self, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(self)
        if cfg.getFileTypes(relatedTo=((pvRelated and 'item_pv') or (decisionRelated and 'item_decision') or 'item')):
            return True
        return False

    MeetingItem.showAnnexesTab = showAnnexesTab
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    ### functionalities linked to rap-col-au-con ###

    security.declarePublic('israpcolaucon')
    def israpcolaucon(self):
        '''This method is used know in which config we are so the meetingitem_view
           template is rendered properly.'''
        meetingconfig = self.context.portal_plonemeeting.getMeetingConfig(self.context)
        if  meetingconfig.id == 'rapport-col-au-con':
            return True
        else :
            return False

    security.declarePublic('getLabelForDescription')
    def getLabelForDescription(self):
        '''This fuinction is used to change the label of the "description" field depending on the
           meetingConfig we are currently in.'''
        if self.adapted().israpcolaucon():
            return self.utranslate("meeting_item_rcc_description", domain="PloneMeeting", context=self)
        else:
            return self.utranslate("meeting_item_description", domain="PloneMeeting", context=self)

    MeetingItem.getLabelForDescription = getLabelForDescription
    # it'a a monkey patch because it's the only way to have a default method in the schema


# ------------------------------------------------------------------------------
class CustomMeetingCategoryAndenne(MeetingCategory):
    '''Adapter that adapts a meeting category object implementing IMeetingCategory
       to the interface IMeetingCategoryCustom.'''
    implements(IMeetingCategoryCustom)
    security = ClassSecurityInfo()

    def __init__(self, category):
        self.context = category

    security.declarePrivate('getRootCatNum')
    def getRootCatNum(self):
        try:
            catRootNum = int(self.context.getId().split('-')[0])
            if catRootNum > SMALLEST_SUBCATEGORY:
                catRootNum = int(math.floor(catRootNum / 100)) * 100
        except ValueError:
            catRootNum = 0 
        return catRootNum

    ##### Functions used for template generation ############################

    security.declarePublic('getRootTitle')
    def getRootTitle(self):
        return str(self.getRootCatNum()) + "." + self.context.getName().split('>')[0].split('.')[1]

    security.declarePublic('getRootPVTitle')
    def getRootPVTitle(self):
        return self.context.getName().split('>')[0].split('.')[1][1:]


# ------------------------------------------------------------------------------
class CustomMeetingConfigAndenne(MeetingConfig):
    '''Adapter that adapts a meeting config object implementing IMeetingConfig to the
       interface IMeetingConfigCustom.'''
    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def __init__(self, config):
        self.context = config

    security.declarePublic('getTopicResults')
    def getTopicResults(self, topic, isFake):
        '''This method computes results of p_topic. If p_topic is a fake one
           (p_isFake is True), it means that some information in the request
           will allow to perform a direct query in portal_catalog (the user
           triggered an advanced search).'''
        rq = self.REQUEST
        # How must we sort the result?
        sortKey = rq.get('sortKey', None)
        sortOrder = 'reverse'
        if sortKey and (rq.get('sortOrder', 'asc') == 'asc'):
            sortOrder = None
        # Is there a filter defined?
        filterKey = rq.get('filterKey', '')
        filterValue = rq.get('filterValue', '').decode('utf-8')

        if not isFake:
            tool = getToolByName(self, 'portal_plonemeeting')
            # Execute the query corresponding to the topic.
            if not sortKey:
                sortCriterion = topic.getSortCriterion()
                if sortCriterion:
                    sortKey = sortCriterion.Field()
                    sortOrder = sortCriterion.reversed and 'reverse' or None
                else:
                    sortKey = 'created'
            methodId = topic.getProperty(TOPIC_SEARCH_SCRIPT, None)
            batchSize = self.REQUEST.get('MaxShownFound') or tool.getMaxShownFound()
            if methodId:
                # Topic params are not sufficient, use a specific method.
                # keep topics defined paramaters
                kwargs = {}
                kwargs['isDefinedInTool'] = False
                for criterion in topic.listSearchCriteria():
                    # Only take criterion with a defined value into account
                    criterionValue = criterion.value
                    if criterionValue:
                        kwargs[str(criterion.field)] = criterionValue
                # if the topic has a TOPIC_SEARCH_FILTERS, we add it to kwargs
                # also because it is the called search script that will use it
                searchFilters = topic.getProperty(TOPIC_SEARCH_FILTERS, None)
                if searchFilters:
                    # the search filters are stored in a text property but are
                    # in reality dicts, so use eval() so it is considered correctly
                    kwargs[TOPIC_SEARCH_FILTERS] = eval(searchFilters)
                brains = getattr(self, methodId)(sortKey, sortOrder,
                                                 filterKey, filterValue, **kwargs)
            else:
                # Execute the topic, but decide ourselves for sorting and filtering.
                params = topic.buildQuery()
                params['sort_on'] = sortKey
                params['sort_order'] = sortOrder
                params['isDefinedInTool'] = False
                if filterKey:
                    params[filterKey] = prepareSearchValue(filterValue)
                brains = self.portal_catalog(**params)
            res = tool.batchAdvancedSearch(
                brains, topic, rq, batch_size=batchSize)
        else:
            # This is an advanced search. Use the Searcher.
            searchedType = topic.getProperty('meeting_topic_type', 'MeetingFile')
            return SearcherAndenne(self, searchedType, sortKey, sortOrder,
                                   filterKey, filterValue).run()
        return res

    MeetingConfig.getTopicResults = getTopicResults
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePublic('searchItemsToValidateOfHighestHierarchicLevel')
    def searchItemsToValidateOfHighestHierarchicLevel(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
        '''Return a list of items that the user can validate regarding his highest hierarchic level.
           So if a user is 'prereviewer' and 'reviewier', the search will only return items
           in state corresponding to his 'reviewer' role.'''
        tool = getToolByName(self, 'portal_plonemeeting')
        member = self.portal_membership.getAuthenticatedMember()
        groupIds = self.portal_groups.getGroupsForPrincipal(member)
        reviewProcessInfos = []
        for groupId in groupIds:
            for reviewer_suffix, review_state in MEETINGREVIEWERS.items():
                if groupId.endswith('_%s' % reviewer_suffix):
                    groupName = groupId[:-len(reviewer_suffix) - 1]
                    # specific management for workflows using the 'pre_validation' wfAdaptation
                    if reviewer_suffix == 'reviewers' and \
                       ('pre_validation' in self.getWorkflowAdaptations() or
                       'pre_validation_keep_reviewer_permissions' in self.getWorkflowAdaptations()):
                        groupObj = getattr(tool, groupName)
                        if groupObj.getUsePrevalidation():
                            review_state = 'prevalidated'
                    reviewProcessInfos.append('%s__reviewprocess__%s' % (groupName, review_state))

        params = {'portal_type': self.getItemTypeName(),
                  'reviewProcessInfo': reviewProcessInfos,
                  'sort_on': sortKey,
                  'sort_order': sortOrder
                  }
        # Manage filter
        if filterKey:
            params[filterKey] = prepareSearchValue(filterValue)
        # update params with kwargs
        params.update(kwargs)
        # Perform the query in portal_catalog
        return self.portal_catalog(**params)

    MeetingConfig.searchItemsToValidateOfHighestHierarchicLevel = searchItemsToValidateOfHighestHierarchicLevel
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePublic('getQueryColumns')
    def getQueryColumns(self, metaType):
        '''What columns must we show when displaying results of a query for
           objects of p_metaType ?'''
        res = ('title',)
        if metaType == 'MeetingItem':
            res += tuple(self.getUserParam('itemColumns', self.REQUEST))
        elif metaType == 'Meeting':
            res += tuple(self.getUserParam('meetingColumns', self.REQUEST))
        elif metaType == 'CourrierFile':
            res += tuple(self.listMailColumns())
        else:
            res += ('creator', 'creationDate')
        return res

    MeetingConfig.getQueryColumns = getQueryColumns
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePrivate('listMailColumns')
    def listMailColumns(self):
        '''Lists all the attributes that can be used as columns for displaying
           information about a mail.'''
        d = 'PloneMeeting'
        res = [ ("creationDate", translate('pm_creation_date', domain=d, context=self.REQUEST)),
                ("refCourrier", translate('MeetingAndenne_label_refCourrier', domain=d, context=self.REQUEST)),
                ("destOrigin", translate('MeetingAndenne_label_destOrigin', domain=d, context=self.REQUEST)),
                ("destUsers", translate('MeetingAndenne_label_destUsers', domain=d, context=self.REQUEST)),
                ("actions", translate("heading_actions", domain='plone', context=self.REQUEST)),
        ]
        return DisplayList(tuple(res))

    MeetingConfig.listMailColumns = listMailColumns
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePublic('searchMyMails')
    def searchMyMails(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
        '''Returns the list of mails for which the user is a recipient.'''
        member = self.portal_membership.getAuthenticatedMember()

        params = {'portal_type': 'CourrierFile',
                  'getDestUsers': member.id,
                  'sort_on': sortKey,
                  'sort_order': sortOrder,
                  }

        # Manage filter
        if filterKey:
            params[filterKey] = prepareSearchValue(filterValue)
        # update params with kwargs
        params.update(kwargs)
        # Perform the query in portal_catalog
        return self.portal_catalog(**params)

    MeetingConfig.searchMyMails = searchMyMails
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePublic('searchAllMailsInCopy')
    def searchAllMailsInCopy(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
        '''Returns the list of mails for which the user is in copy.'''
        tool = getToolByName(self, 'portal_plonemeeting')
        mailGroups = tool.getGroupsForUser(suffix='mailviewers')
        if len(mailGroups) > 0:
            mailGroups = [group.id for group in mailGroups]

        params = {'portal_type': 'CourrierFile',
                  'getDestGroups': mailGroups,
                  'sort_on': sortKey,
                  'sort_order': sortOrder,
                  }

        if tool.isManager(self):
            del params['getDestGroups']

        # Manage filter
        if filterKey:
            params[filterKey] = prepareSearchValue(filterValue)
        # update params with kwargs
        params.update(kwargs)
        # Perform the query in portal_catalog
        return self.portal_catalog(**params)

    MeetingConfig.searchAllMailsInCopy = searchAllMailsInCopy
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    MeetingConfig.listAdviceTypesOrg=MeetingConfig.listAdviceTypes
    security.declarePublic('listAdviceTypes')
    def listAdviceTypes(self):
        res = self.listAdviceTypesOrg()
        d = "PloneMeeting"
        res.add("reservation", translate('reservation', domain=d, context=self.REQUEST))
        return res

    MeetingConfig.listAdviceTypes = listAdviceTypes
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePublic('listItemEvents')
    def listItemEvents(self):
        '''Lists the events related to items that will trigger a mail being
           sent.'''
        d = 'PloneMeeting'
        res = [
            ("lateItem", translate('event_late_item',
                                   domain=d,
                                   context=self.REQUEST)),
            ("itemPresented", translate('event_item_presented',
                                        domain=d,
                                        context=self.REQUEST)),
            ("itemUnpresented", translate('event_item_unpresented',
                                          domain=d,
                                          context=self.REQUEST)),
            ("itemDelayed", translate('event_item_delayed',
                                      domain=d,
                                      context=self.REQUEST)),
            ("annexAdded", translate('event_add_annex',
                                     domain=d,
                                     context=self.REQUEST)),
            # relevant if advices are enabled
            ("adviceToGive", translate('event_advice_to_give',
                                       domain=d,
                                       context=self.REQUEST)),
            ("adviceEdited", translate('event_add_advice',
                                       domain=d,
                                       context=self.REQUEST)),
            ("adviceInvalidated", translate('event_invalidate_advice',
                                            domain=d,
                                            context=self.REQUEST)),
            # relevant if askToDiscuss is enabled
            ("askDiscussItem", translate('event_ask_discuss_item',
                                         domain=d,
                                         context=self.REQUEST)),
            # relevant if clone to another MC is enabled
            ("itemClonedToThisMC", translate('event_item_clone_to_this_mc',
                                             domain=d,
                                             context=self.REQUEST)),
            # relevant if annex conversion is enabled
            ("annexConversionError", translate('event_item_annex_conversion_error',
                                               domain=d,
                                               context=self.REQUEST)),
            # relevant if wfAdaptation 'return to proposing group' is enabled
            ("returnedToProposingGroup", translate('event_item_returned_to_proposing_group',
                                                   domain=d,
                                                   context=self.REQUEST)),
            ("returnedToMeetingManagers", translate('event_item_returned_to_meeting_managers',
                                                    domain=d,
                                                    context=self.REQUEST)), ]

        # add custom mail notifications added by subproducs
        for extra_item_event in self.adapted().extraItemEvents():
            res.append((extra_item_event,
                        translate(extra_item_event,
                                  domain=d,
                                  context=self.REQUEST)))

        # a notification can also be sent on every item transition
        # create a separated result (res_transitions) so we can easily sort it
        item_transitions = self.listTransitions('Item')
        res_transitions = []
        for item_transition_id, item_transition_name in item_transitions:
            res_transitions.append(("item_state_changed_%s" % item_transition_id, item_transition_name))

        return DisplayList(tuple(res)) + DisplayList(res_transitions).sortedByValue()

    MeetingConfig.listItemEvents = listItemEvents
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePublic('listSelectableAssociatedGroups')
    def listSelectableAssociatedGroups(self):
        '''Returns a list of groups that can be selected on an item as associated for
           the item.'''
        res = []
        tool = getToolByName(self, 'portal_plonemeeting')
        meetingGroups = tool.getMeetingGroups()
        for mg in meetingGroups:
            meetingPloneGroups = mg.getPloneGroups()
            for ploneGroup in meetingPloneGroups:
                res.append((ploneGroup.id, ploneGroup.getProperty('title')))
        return DisplayList(tuple(res))

    MeetingConfig.listSelectableAssociatedGroups = listSelectableAssociatedGroups
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class

    security.declarePublic('extraItemEvents')
    def extraItemEvents(self):
        return ("event_add_pv_annex", )


# ------------------------------------------------------------------------------
class CustomMeetingFileAndenne(MeetingFile):
    '''Adapter that adapts a meeting file object implementing IMeetingFile to
       the interface IMeetingFileCustom.'''
    implements(IMeetingFileCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        # We define here a PloneMeeting-specific modification date for this
        # annex. Indeed, we can't use the standard Plone modification_date for
        # the PloneMeeting color system because some events like parent state
        # changes update security settings on annexes and modification_date is
        # updated.
        tool = getToolByName(self, 'portal_plonemeeting')
        self.pm_modification_date = self.modification_date
        tool.rememberAccess(self.UID(), commitNeeded=False)
        parent = self.getParent()
        if parent:
            # update parent.annexIndex if it was not already set
            # by the conversion process for example
            annexIndexUids = [annex['UID'] for annex in parent.annexIndex]
            if not self.UID() in annexIndexUids:
                IAnnexable(parent).updateAnnexIndex()
            parent.alreadyUsedAnnexNames.append(self.id)
        # at the end of creation, we know now self.relatedTo
        # and we can manage the self.toPrint default value
        cfg = tool.getMeetingConfig(self)
        if self.findRelatedTo() == 'item_pv':
            self.setToPrint(False)
        elif self.findRelatedTo() == 'item_decision':
            self.setToPrint(cfg.getAnnexDecisionToPrintDefault())
        elif self.findRelatedTo() == 'item':
            self.setToPrint(cfg.getAnnexToPrintDefault())
        else:
            # relatedTo == 'advice'
            self.setToPrint(cfg.getAnnexAdviceToPrintDefault())
        # at the end of creation, we know now self.meetingFileType
        # and we can manage the self.isConfidential default value
        mft = self.getMeetingFileType(theData=True)
        self.setIsConfidential(mft['isConfidentialDefault'])
        # Call sub-product code if any
        self.adapted().onEdit(isCreated=True)
        # Add text-extraction-related attributes
        rq = self.REQUEST
        self.needsOcr = rq.get('needs_ocr', None) is not None
        self.ocrLanguage = rq.get('ocr_language', None)
        # Reindexing the annex may have the effect of extracting text from the
        # binary content, if tool.extractTextFromFiles is True (see method
        # MeetingFile.indexExtractedText).
        self.reindexObject()

    MeetingFile.at_post_create_script = at_post_create_script
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        self.adapted().onEdit(isCreated=False)

        if self.findRelatedTo() == 'item_pv':
            catalog = getToolByName(self, 'portal_catalog')
            catalog.uncatalog_object('/'.join(self.getPhysicalPath()))

    MeetingFile.at_post_edit_script = at_post_edit_script
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class

    security.declarePublic('indexExtractedText')
    def indexExtractedText(self):
        ''' This method should extract text from the binary content of this object
            and put it in the indexExtractedText index if tool.extractTextFromFiles is True.

            However, as we use collective.documentviewer and SearchableText,
            we have to monkey patch this function and always return an empty string.'''
        return ''

    MeetingFile.indexExtractedText = indexExtractedText
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class

    security.declarePublic('SearchableText')
    def SearchableText(self):
        ''' This method should extract text from the binary content of this object
            and put it in the indexExtractedText index if tool.extractTextFromFiles is True.

            However, as we use collective.documentviewer and SearchableText,
            we have to monkey patch this function and always return an empty string.'''
        if self.findRelatedTo() == 'item_pv':
            return ''
        super(MeetingFile, self).SearchableText()

    MeetingFile.SearchableText = SearchableText
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class


# ------------------------------------------------------------------------------
class CustomMeetingFileTypeAndenne(MeetingFileType):
    '''Adapter that adapts a meeting file type object implementing
       IMeetingFileType to the interface IMeetingFileTypeCustom.'''
    implements(IMeetingFileTypeCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    security.declarePrivate('listOtherMCCorrespondences')
    def listOtherMCCorrespondences(self):
        '''Vocabulary for the otherMCCorrespondence field, also
           used for the subTypes.otherMCCorrespondence column.
           This will only appear for the 'item', 'item_decision' and
           'item_pv' relatedTo MeetingFileType as advices are not
           transfered to another MC.'''
        # display also inactive MeetingConfigs because during configuration
        # we can define thses values before activating the new meetingConfig
        # and we do not have to manage inactive meetingConfigs consistency
        tool = getToolByName(self, 'portal_plonemeeting')
        currentCfgId = self.getParentNode().getParentNode().getId()
        relatedToVocab = self.listRelatedTo()
        res = []
        for cfg in tool.objectValues('MeetingConfig'):
            cfgId = cfg.getId()
            if cfgId == currentCfgId:
                continue
            fileTypes = cfg.getFileTypes(relatedTo='item')
            fileTypes = fileTypes + cfg.getFileTypes(relatedTo='item_decision')
            fileTypes = fileTypes + cfg.getFileTypes(relatedTo='item_pv')
            for fileType in fileTypes:
                res.append(('%s__filetype__%s' % (cfg.getId(), fileType['id']),
                            u'%s -> %s -> %s' % (unicode(cfg.Title(), 'utf-8'),
                                                 self.displayValue(relatedToVocab, fileType['relatedTo']),
                                                 unicode(fileType['name'], 'utf-8'))))
        return DisplayList(tuple(res))

    MeetingFileType.listOtherMCCorrespondences = listOtherMCCorrespondences
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingFileType class

    security.declarePrivate('listRelatedTo')
    def listRelatedTo(self):
        ''' This method lists to what an annex can be related to. It is monkey
            patched to add the possibility to add annexes to closed points.'''
        res = []
        res.append(('item',
                    translate('meetingfiletype_related_to_item',
                              domain='PloneMeeting',
                              context=self.REQUEST)))
        res.append(('item_decision',
                    translate('meetingfiletype_related_to_item_decision',
                              domain='PloneMeeting',
                              context=self.REQUEST)))
        res.append(('item_pv',
                    translate('meetingfiletype_related_to_item_pv',
                              domain='PloneMeeting',
                              context=self.REQUEST)))
        res.append(('advice',
                    translate('meetingfiletype_related_to_advice',
                              domain='PloneMeeting',
                              context=self.REQUEST)))
        return DisplayList(tuple(res))

    MeetingFileType.listRelatedTo = listRelatedTo
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingFileType class


# ------------------------------------------------------------------------------
class CustomMeetingGroupAndenne(MeetingGroup):
    '''Adapter that adapts a meeting group object implementing IMeetingGroup to
       the interface IMeetingGroupCustom.'''
    implements(IMeetingGroupCustom)
    security = ClassSecurityInfo()

    def __init__(self, group):
        self.context = group


# ------------------------------------------------------------------------------
class CustomToolMeetingAndenne(ToolPloneMeeting):
    '''Adapter that adapts the PloneMeeting tool object implementing
       IToolPloneMeeting to the interface IToolPloneMeetingCustom.'''
    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, tool):
        self.context = tool

    security.declarePublic('getSearchPathFromMeetingConfig')
    def getSearchPathFromMeetingConfig(self,context,query):
        '''Used in monkey patched filter_query function for search, in livesearch_reply.py (skin) for livesearch
           and in search.pt for filter type advanced search query'''
        cfg = self.context.getMeetingConfig(self.context)
        if cfg is not None:
            if cfg.id == "courrierfake":
                path = { 'query': 'gestion-courrier', 'level': 1 }
            else:
                path = { 'query': 'mymeetings/' + cfg.id, 'level': 3 }
        else:
            # if there's no current MeetingConfig (if we are on home for example)
            path = { 'query': '/', 'level': 1 }
        return path

    security.declarePublic('getSearchTypesFromMeetingConfig')
    def getSearchTypesFromMeetingConfig(self,context,query):
        '''Used in monkey patched filter_query function for search, in livesearch_reply.py (skin) for livesearch
           and in search.pt for filter type advanced search query'''
        type_list = []
        cfg = self.context.getMeetingConfig(self.context)
        if cfg is not None:
            if cfg.id == "courrierfake":
                type_list = ['CourrierFile', ]
            else:
                type_list = [cfg.getItemTypeName(), cfg.getMeetingTypeName(), 'MeetingFile']
        else:
            # if there's no current MeetingConfig (if we are on home for example)
            type_list = ['CourrierFile', 'MeetingFile']
            for config in self.context.objectValues('MeetingConfig'):
                type_list.append(config.getItemTypeName())
                type_list.append(config.getMeetingTypeName())

        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        if types:
            all_allowed_types = type_list
            type_list = []
            for portal_type in types:
                if portal_type in all_allowed_types:
                    type_list.append(portal_type)

        return type_list

    security.declarePublic('getCategoriesFromMeetingConfig')
    def getCategoriesFromMeetingConfig(self,context):
        '''Used in advanced searches to filter results by category'''
        cfg = self.context.getMeetingConfig(self.context)
        if cfg is not None and cfg.id != "courrierfake":
            return cfg.categories.objectValues()
        return None  

    security.declarePrivate('listProposingGroup')
    def listProposingGroups(self):
        '''Used in advanced searches to filter results by proposing group.'''
        res = []
        tool = getToolByName(self.context, 'portal_plonemeeting')
        for group in tool.getMeetingGroups():
            res.append((group.id, group.getName()))
        res = sorted(res, key = collateDisplayListsValues)
        return res

    security.declarePrivate('listDestUsers')
    def listDestUsers(self):
        '''List the users that will be selectable in the destination user ComboBox.'''
        pgp = self.context.portal_membership
        res = []
        for user in pgp.listMembers():
            if user.getProperty('listed'):
                res.append( (user.getId(), user.getProperty('fullname')) )
        res = sorted(res, key = collateDisplayListsValues)
        return res

    security.declarePublic('getCourrierfakeConfig')
    def getCourrierfakeConfig(self):
        '''
            Returns the courrierfake MeetingConfig object.
        '''
        return getattr(self.context, 'courrierfake')

    security.declarePublic('getCourrierfakeFolder')
    def getCourrierfakeFolder(self):
        '''
            Returns the courrierfake folder.
        '''
        return self.getPhysicalPath()[0] + '/commune/gestion-courrier'

    security.declarePublic('getMailTypesForSearch')
    def getMailTypesForSearch(self):
        '''
            Returns the ids and titles of all the available mail types for
            search purposes.
        '''
        return MAIL_TYPES.items()

    security.declarePublic('isMailViewer')
    def isMailViewer(self):
        '''
            Returns True if the current user is member of a _mailviewers
            group.
        '''
        return len(self.context.getGroupsForUser(suffix='mailviewers')) > 0


# ------------------------------------------------------------------------------
class MeetingCollegeAndenneWorkflowActions(MeetingWorkflowActions):
    '''Adapter that adapts a meeting object implementing IMeeting to the
       interface IMeetingCollegeWorkflowActions'''

    implements(IMeetingCollegeAndenneWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('initSequenceNumbers')
    def initSequenceNumbers(self):
        '''When a meeting is published (or frozen, depending on workflow
           adaptations), we attribute him two sequence numbers.'''
        cfg = self.context.portal_plonemeeting.getMeetingConfig(self.context)

        if self.context.getMeetingNumberInParliamentaryTerm() == -1:
            meetingNumberInParliamentaryTerm = cfg.getLastMeetingNumberInParliamentaryTerm() + 1
            self.context.setMeetingNumberInParliamentaryTerm(meetingNumberInParliamentaryTerm)
            cfg.setLastMeetingNumberInParliamentaryTerm(meetingNumberInParliamentaryTerm)

        if self.context.getMeetingNumber() != -1:
            return  # Already done.
        if cfg.getYearlyInitMeetingNumber():
            # I must reinit the meeting number to 0 if it is the first
            # meeting of this year or the first meeting ever.
            prev = self.context.getPreviousMeeting()
            if prev == None or \
               (prev.getDate().year() != self.context.getDate().year()):
                self.context.setMeetingNumber(1)
                cfg.setLastMeetingNumber(1)
                return
        # If we are here, we must simply increment the meeting number.
        meetingNumber = cfg.getLastMeetingNumber()+1
        self.context.setMeetingNumber(meetingNumber)
        cfg.setLastMeetingNumber(meetingNumber)

    security.declarePrivate('doPublish')
    def doPublish(self, stateChange):
        '''When publishing the meeting, initialize the sequence numbers.'''
        self.initSequenceNumbers()

    security.declarePrivate('doFreeze')
    def doFreeze(self, stateChange):
        '''When freezing the meeting, we initialize sequence numbers.'''
        self.initSequenceNumbers()


# ------------------------------------------------------------------------------
class MeetingCollegeAndenneWorkflowConditions(MeetingWorkflowConditions):
    '''Adapter that adapts a meeting object implementing IMeeting to the
       interface IMeetingCollegeWorkflowConditions'''

    implements(IMeetingCollegeAndenneWorkflowConditions)
    security = ClassSecurityInfo()

    security.declarePublic('mayFreeze')
    def mayFreeze(self):
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True # At least at present
            if not self.context.getRawItems():
                res = No(translate('item_required_to_publish', domain='PloneMeeting', context=self.context.REQUEST))
        return res

    security.declarePublic('mayDecide')
    def mayDecide(self):
        if checkPermission(ReviewPortalContent, self.context):
            return True
        return False

    security.declarePublic('mayClose')
    def mayClose(self):
        # The user just needs the "Review portal content" permission on the
        # object to close it.
        if checkPermission(ReviewPortalContent, self.context):
            return True
        return False


# ------------------------------------------------------------------------------
class MeetingItemCollegeAndenneWorkflowActions(MeetingItemWorkflowActions):
    '''Adapter that adapts a meeting item object implementing IMeetingItem to
       the interface IMeetingItemAndenneWorkflowActions'''

    implements(IMeetingItemCollegeAndenneWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doValidate')
    def doValidate(self, stateChange):
        MeetingItemWorkflowActions.doValidate(self, stateChange)
        self.context.setVerifUser(self.context.adapted().getLatestReviewer())

    security.declarePrivate('doItemFreeze')
    def doItemFreeze (self, stateChange):
        member = self.context.portal_membership.getAuthenticatedMember()
        if (member.has_permission('MeetingAndenne: Write pv', self.context)):
            if not self.context.fieldIsEmpty('projetpv'):
                self.context.setPv(self.context.getProjetpv())
            if not self.context.fieldIsEmpty('decision'):
                self.context.setTextpv(self.context.getDecision())

    security.declarePrivate('doPre_accept')
    def doPre_accept(self, stateChange):
        pass

    security.declarePrivate('doAccept_but_modify')
    def doAccept_but_modify(self, stateChange):
        pass

    security.declarePublic('doAccept_but_modify_and_close')
    def doAccept_but_modify_and_close(self, stateChange):
        pass

    security.declarePublic('doAccept_and_close')
    def doAccept_and_close(self, stateChange):
        pass

    security.declarePublic('doDelay_and_close')
    def doDelay_and_close(self, stateChange):
        pass

    security.declarePublic('doRefuse_and_close')
    def doRefuse_and_close(self, stateChange):
        pass

    security.declarePrivate('doDelay')
    def doDelay(self, stateChange):
        '''When an item is delayed, we will duplicate it: the copy is back to
           the initial state and will be linked to this one.'''
        creator = self.context.Creator()
        # We create a copy in the initial item state, in the folder of creator.
        clonedItem = self.context.clone(copyAnnexes=True,
                                        newOwnerId=creator,
                                        cloneEventAction='create_from_predecessor',
                                        keepProposingGroup=True)
        clonedItem.setPredecessor(self.context)
        # Send, if configured, a mail to the person who created the item
        clonedItem.sendMailIfRelevant('itemDelayed', 'Owner', isRole=True)
        clonedItem.setTreatUser(self.context.getTreatUser())
        wTool = api.portal.get_tool('portal_workflow')
        try:
            wTool.doActionFor(clonedItem, 'propose')
        except:
            pass  # Maybe does transaction 'propose' not exist.

# ------------------------------------------------------------------------------
class MeetingItemCollegeAndenneWorkflowConditions(MeetingItemWorkflowConditions):
    '''Adapter that adapts a meeting item object implementing IMeetingItem to
       the interface IMeetingItemAndenneWorkflowConditions'''

    implements(IMeetingItemCollegeAndenneWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item # Implements IMeetingItem

    security.declarePublic('mayDecide')
    def mayDecide(self):
        '''We may decide an item if the linked meeting is in relevant state.'''
        meeting = self.context.getMeeting()
        if checkPermission(ReviewPortalContent, self.context) and \
           meeting and meeting.adapted().isDecided():
            return True
        return False

    security.declarePublic('mayPrevalidate')
    def mayPrevalidate(self):
        '''We may prevalidate an item if the user has the 'Review portal content'
           permission, prevalidation workflow adaptation is active and the
           proposing group uses prevalidation.'''
        if not MeetingItemWorkflowConditions.mayPrevalidate(self):
            return False

        item = self.context
        tool = getToolByName(item, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        adaptations = cfg.getWorkflowAdaptations()
        group = tool[item.getProposingGroup()]
        if not 'pre_validation_keep_reviewer_permissions' in adaptations or not group.getUsePrevalidation():
            return False

        toolMembership = getToolByName(item, 'portal_membership')
        user = toolMembership.getAuthenticatedMember()
        if user.has_role('Manager', item):
            return True

        userMeetingGroups = tool.getGroupsForUser(suffix="prereviewers")
        if item.getCategory(theObject=True).adapted().getRootCatNum() in PERSONNEL_CATEGORIES:
            return getattr(tool, "personnel") in userMeetingGroups
        else:
            return group in userMeetingGroups

    security.declarePublic('mayValidate')
    def mayValidate(self):
        '''We may validate an item if the user has the 'Review portal content' permission
           and either the prevalidation workflow adaptation is not active or the proposing
           group doesn't use prevalidation or the user is member of the reviewer group.'''
        if not MeetingItemWorkflowConditions.mayValidate(self):
            return False

        item = self.context
        tool = getToolByName(item, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        adaptations = cfg.getWorkflowAdaptations()
        group = tool[item.getProposingGroup()]
        if not 'pre_validation_keep_reviewer_permissions' in adaptations or not group.getUsePrevalidation() \
           or item.queryState() == 'prevalidated':
            return True

        toolMembership = getToolByName(item, 'portal_membership')
        user = toolMembership.getAuthenticatedMember()
        if user.has_role('Manager', item):
            return True

        if item.getCategory(theObject=True).adapted().getRootCatNum() in PERSONNEL_CATEGORIES:
            return group == getattr(tool, "personnel")
        else:
            return group in tool.getGroupsForUser(suffix="prereviewers")

    security.declarePublic('mayCorrect')
    def mayCorrect(self, toPrevalidated = False):
        '''We use the PloneMeeting default implementation except when toPrevalidate is
           True. We then have to verify that the proposing group also uses prevalidation.
           This is necessary to avoid that a Manager sets an item in Prevalidated state
           when it is not in use.'''
        if not MeetingItemWorkflowConditions.mayCorrect(self):
            return False

        item = self.context
        if item.queryState() != 'validated':
            return True

        tool = getToolByName(item, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        adaptations = cfg.getWorkflowAdaptations()
        group = tool[item.getProposingGroup()]
        prevalidation = 'pre_validation_keep_reviewer_permissions' in adaptations and group.getUsePrevalidation()
        return prevalidation == toPrevalidated

# ------------------------------------------------------------------------------
InitializeClass(CustomMeetingAndenne)
InitializeClass(CustomMeetingItemAndenne)
InitializeClass(CustomMeetingCategoryAndenne)
InitializeClass(CustomMeetingConfigAndenne)
InitializeClass(CustomMeetingFileAndenne)
InitializeClass(CustomMeetingFileTypeAndenne)
InitializeClass(CustomMeetingGroupAndenne)
InitializeClass(CustomToolMeetingAndenne)
InitializeClass(MeetingCollegeAndenneWorkflowActions)
InitializeClass(MeetingCollegeAndenneWorkflowConditions)
InitializeClass(MeetingItemCollegeAndenneWorkflowActions)
InitializeClass(MeetingItemCollegeAndenneWorkflowConditions)
# ------------------------------------------------------------------------------
