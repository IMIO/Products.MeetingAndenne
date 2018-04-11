# -*- coding: utf-8 -*-
#
# File: config.py
#
# Copyright (c) 2012 by CommunesPlone
# Generator: ArchGenXML Version 2.6
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Gauthier Bastien <info@communesplone.be>, Stephan Geulette <unknown>"""
__docformat__ = 'plaintext'


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
from Products.Archetypes.public import DisplayList
##/code-section config-head


PROJECTNAME = "MeetingAndenne"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))

## TO BE CHANGED ##
ADD_CONTENT_PERMISSIONS = {
    'CourrierFile': 'Add portal content',
}

setDefaultRoles('Add portal content', ('Manager', 'CourrierManager'))
## END ##

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
from Products.PloneMeeting import config as PMconfig
ANDENNEROLES = {}
ANDENNEROLES['pvwriters'] = 'MeetingPvWriter'
ANDENNEROLES['mailviewers'] = 'MeetingMailViewer'

PMconfig.MEETINGROLES.update(ANDENNEROLES)
PMconfig.MEETING_GROUP_SUFFIXES = PMconfig.MEETINGROLES.keys()
PMconfig.DEFAULT_COPIED_FIELDS = ['title', 'description', 'detailedDescription', 'motivation','decision', 'budgetInfos', 'budgetRelated', 'privacy','sendToAuthority','refdoc','yourrefdoc','projetpv','textpv','pv']


# Mail types static define
MAIL_TYPES = DisplayList((
    ('Courrier Postal', 'Courrier Postal'),
    ('Courrier numérique', 'Courrier numérique'),
    ('Courrier recommandé', 'Courrier recommandé'),
    ('Note interne', 'Note interne'),
    ('autres', 'autres'),
    ))

LANGUAGES = DisplayList((
    ('fra','Français'),
    ('eng','Anglais'),
    ('deu','Allemand'),
    ('nld','Néerlandais'),
    ))

# Mail topics
# Format is :
# - topicId
# - a list of topic criteria
# - a sort_on attribute
# - a topicScriptId used to manage complex searches
# - a tal expression used to filter who can use the topic
MAIL_TOPICS = (
    # My items.
    ( 'searchmymails',
    (  ('Type', 'ATPortalTypeCriterion', ('CourrierFile',)),
    ), 'CreationDate', 'searchMailsInCopy', '',
    ),
    # Mails in group : need a script to do this search.
    ( 'searchallmailsingroup',
    (  ('Type', 'ATPortalTypeCriterion', ('CourrierFile',)),
    ), 'CreationDate', '', '',
    ),
    # Scanned mails : these were added by a robot.
    ( 'searchmailrobot',
    (  ('Type', 'ATPortalTypeCriterion', ('CourrierFile',)),
       ('Title', 'ATSimpleStringCriterion', 'autotitre*'),
    ), 'CreationDate', '',
       "python: here.portal_plonemeeting.adapted().isMailViewer() or here.portal_plonemeeting.isManager(here)"
    ),
)

# College custom views
CUSTOM_COLLEGE_TOPICS_VIEWS = {
    'searchmyitems': ['Title', 'CreationDate', 'review_state', 'getDisplayableTreatUser', 'getDisplayableProposingGroup'],
    'searchallitems': ['Title', 'CreationDate', 'review_state', 'getDisplayableTreatUser', 'getDisplayableProposingGroup'],
    'searchallitemsincopy': ['Title', 'CreationDate', 'review_state', 'getDisplayableTreatUser'],
    'searchallitemstovalidate': ['Title', 'CreationDate', 'Creator', 'review_state', 'getDisplayableTreatUser'],
    'searchallitemsingroup': ['Title', 'CreationDate', 'review_state', 'getDisplayableTreatUser'],
    }

# Custom Meeting and MeetingItem types by MeetingConfig
CUSTOM_TYPES_BY_CONFIG = {
    'meeting-config-college': {'Meeting': ['MeetingCollege', ], 'MeetingItem': ['MeetingItemCollege', ], },
    'conseil-communal': {'Meeting': ['Meetingcons', ], 'MeetingItem': ['MeetingItemcons', ], },
    'rapport-col-au-con': {'Meeting': ['Meetingrcc', ], 'MeetingItem': ['MeetingItemrcc', ], },
    'comite-de-direction': {'Meeting': ['Meetingcd', ], 'MeetingItem': ['MeetingItemcd', ], },
    }

# Categories defines
PERSONNEL_CATEGORIES = (4300, 45)
SMALLEST_SUBCATEGORY = 100

# cron4plone defines
CRON_TASKS = [ u'55 17 * * portal/@@run-docsplit-on-blobs',
               u'30 0 1 * portal/@@parse-converted-files',
             ]
CRON_BATCH_SIZE = 2500

##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.MeetingAndenne.AppConfig import *
except ImportError:
    pass
