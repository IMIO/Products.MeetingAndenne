# -*- coding: utf-8 -*-
#
# File: CourrierFile.py
#
# Copyright (c) 2012 by Andenne
# Generator: ArchGenXML Version 2.6
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Fabio MARCUZZI <fabio.marcuzzi@ac.andenne.be,
Sebastien RONVEAUX <sebastien.ronveaux@ac.andenne.be>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from plone.app.blob.content import ATBlob
from plone.app.blob.content import ATBlobSchema
from Products.PloneMeeting.config import *

##code-section module-header #fill in your manual code here
import os
import os.path
import socket
from Acquisition import aq_base
from AccessControl import Unauthorized
from zope.annotation import IAnnotations
from zope.i18n import translate
from plone.memoize.instance import memoize
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import getObjSize
from Products.MailHost.MailHost import MailHostError
from Products.MimetypesRegistry.common import MimeTypeException
from collective.documentviewer.async import asyncInstalled
from Products.PloneMeeting.MeetingFile import convertToImages
from Products.PloneMeeting.utils import getCustomAdapter, SENDMAIL_ERROR, ENCODING_ERROR, MAILHOST_ERROR

from DateTime import DateTime
from Products.MeetingAndenne.config import *
from Products.MeetingAndenne.utils import *

import logging
logger = logging.getLogger( 'MeetingAndenne' )

# Error-related constants ------------------------------------------------------
CONTENT_TYPE_NOT_FOUND = 'The content_type for CourrierFile at %s was not found in mimetypes_registry!'
FILE_EXTENSION_NOT_FOUND = 'The extension used by CourrierFile at %s does not correspond to ' \
    'an extension available in the mimetype %s found in mimetypes_registry!'
##/code-section module-header

schema = Schema((

    StringField(
        name='refcourrier',
        default_method="getCourrierReference",
        widget=StringWidget(
            sqize= 100,
            label='Refdoc',
            label_msgid='MeetingAndenne_label_refCourrier',
            i18n_domain='PloneMeeting',
        ),
        searchable=True,
    ),

    StringField(
        name='typecourrier',
        widget=SelectionWidget(
            label='Typecourrier',
            label_msgid='MeetingAndenne_label_typeCourrier',
            i18n_domain='PloneMeeting',
        ),
        vocabulary=MAIL_TYPES
    ),

    StringField(
        name='destOrigin',
        widget=StringWidget(
            size= 100,
            label='Destorigin',
            label_msgid='MeetingAndenne_label_destOrigin',
            i18n_domain='PloneMeeting',
        ),
        searchable=True,
    ),

    LinesField(
        name='destUsers',
        widget=MultiSelectionWidget(
            size=10,
            description="destUseritem",
            description_msgid="dest_user_item_descr",
            label='Destusers',
            label_msgid='MeetingAndenne_label_destUsers',
            i18n_domain='PloneMeeting',
        ),
        enforceVocabulary=True,
        multiValued=1,
        vocabulary='listDestUsers'
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

CourrierFile_schema = ATBlobSchema.copy() + schema.copy()
CourrierFile_schema['relatedItems'].widget.visible=False
CourrierFile_schema['description'].widget.description='Descriptionitem'
CourrierFile_schema['description'].widget.description_msgid='CourrierFile_label_description_descr'
CourrierFile_schema['description'].widget.label='Description'
CourrierFile_schema['description'].widget.label_msgid='CourrierFile_label_description'
CourrierFile_schema['description'].widget.i18n_domain='PloneMeeting'
CourrierFile_schema.moveField('refcourrier',pos='top')
CourrierFile_schema.moveField('typecourrier',pos=4)
CourrierFile_schema.moveField('destOrigin',pos=3)

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class CourrierFile(ATBlob, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.ICourrierFile)

    meta_type = 'CourrierFile'
    _at_rename_after_creation = True

    schema = CourrierFile_schema

    ##code-section class-header #fill in your manual code here
    aliases = {
        '(Default)'  : '(dynamic view)',
        'view'       : 'file_view',
        'index.html' : '(dynamic view)',
        'edit'       : 'atct_edit',
        'properties' : 'base_metadata',
        'sharing'    : 'folder_localrole_form',
        'gethtml'    : '',
        'mkdir'      : '',
    }
    ##/code-section class-header

    # Methods

    # Manually created methods
    security.declarePublic('getCourrierReference')
    def getCourrierReference(self):
        '''Return a too complicated item reference to be defined as a TAL Expression
            (field MeetingConfig.itemReferenceFormat.'''
        actualyear = int( DateTime(self.CreationDate()).strftime('%y') )
        start = DateTime(actualyear, 1, 1)
        end = DateTime(actualyear, 12, 31)
        results = self.portal_catalog.searchResults(Type = "CourrierFile", created = { "query": [ start , end ] ,"range" : "minmax" } )
        result = len(results)
        ref = str( DateTime(self.CreationDate()).strftime('%y.%m.%d') ) + '/' + '%05d' % result
        return ref

    security.declarePublic('getNumRefCourrier')
    def getNumRefCourrier(self):
        '''Extracts the mail number from the complete reference.'''
        return long(self.getRefcourrier().split('/')[1])

    security.declarePrivate('deletefile')
    def deletefile(self):
        os.system( "mv /home/zope/scan/scantmp/" + str(self.getFilename()) + " /home/zope/scan/scanarchived/" + str(self.getFilename()))

    security.declarePrivate('listDestUsers')
    def listDestUsers(self):
        '''List the users that will be selectable in the destination user ComboBox.'''
        return DisplayList( tuple(self.portal_plonemeeting.adapted().listDestUsers()) )

    security.declarePublic('getDisplayableDestUsers')
    def getDisplayableDestUsers(self):
        '''Lists the Users with full name.'''
        destUsers = self.getDestUsers()
        res = ""
        for destUser in destUsers:
            if self.portal_membership.getMemberById( destUser ):
                res += self.portal_membership.getMemberById(destUser).getProperty('fullname') + ";"
            else:
                res += destUser + ";"
        if len(res) > 0:
            return res[:-1]
        return res

    security.declarePrivate('affectPermissions')
    def affectPermissions(self, destuser):
        '''Add the MeetingMailViewer permission to the user and all the groups he belongs to.'''
        grp_tool = self.acl_users.source_groups
        ploneUser = self.portal_membership.getMemberById(destuser)
        if ploneUser:
            groups = grp_tool.getGroupsForPrincipal(ploneUser)
            groupsToAdd = set()
            for group in groups:
                explodedGroup = group.split('_')
                if explodedGroup[1] in MEETING_GROUP_SUFFIXES and explodedGroup[1] != "pvwriters":
                    groupsToAdd.add( explodedGroup[0] + '_mailviewers' )
            for group in groupsToAdd:
                self.manage_addLocalRoles( group, ('MeetingMailViewer', ) )
            self.manage_addLocalRoles( destuser, ('MeetingMailViewer', ) )
            self.reindexObject()

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        user = self.portal_membership.getAuthenticatedMember()
        self.manage_delLocalRoles( [user.getId()] )
        self.manage_addLocalRoles( user.getId(), ('Owner', ) )
        self.updateLocalRoles()
        self.sendMailIfRelevant()
        self.deletefile()
        # Add text-extraction-related attributes
        rq = self.REQUEST
        self.ocrLanguage = rq.get('ocr_language', 'fra')
        self.reindexObject()

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        rq = self.REQUEST
        self.updateLocalRoles()
        self.sendMailIfRelevant()
        self.ocrLanguage = rq.get('ocr_language', 'fra')
        convertToImages(self, None, force=True)
        self.reindexObject()

    security.declarePublic('wfConditions')
    def wfConditions(self):
        '''Returns self. This is some kind of patch needed for mail types to work without changing plonemeeting_actions.pt file'''
        return self

    security.declarePublic('mayDelete')
    def mayDelete(self):
        '''Returns True. This is some kind of patch needed for mail types to work without changing plonemeeting_actions.pt file'''
        return True

    security.declareProtected('Modify portal content', 'updateLocalRoles')
    def updateLocalRoles(self):
        # Add the local roles corresponding to the selected DestUser.
        # We give the CourrierFile role to the selected User
        # this will give them a read-only access to the item
        portal = self.portal_url.getPortalObject()
        destUsers = self.getDestUsers()
        if destUsers:
            for destUser in destUsers:
                self.affectPermissions( destUser )

    security.declarePrivate('sendMailIfRelevant')
    def sendMailIfRelevant(self):
        # Send a mail to selected DestUsers.
        portal = self.portal_url.getPortalObject()

        subject = translate('CourrierFile_mail_subject', domain='PloneMeeting', context=self.REQUEST)

        host = self.unrestrictedTraverse('@@plone_portal_state').navigation_root_url()
        link = "%s/gestion-courrier/courrierall/%s" % (host, self.getId())
        body = translate('CourrierFile_mail_body', domain='PloneMeeting', context=self.REQUEST) + link

        fromAddress = ("ANDANA <%s>" % portal.getProperty('email_from_address'))
        destUsers = self.getDestUsers()
        if destUsers:
            for destUser in destUsers:
                ploneUser = self.portal_membership.getMemberById(destUser)
                recipient = (ploneUser.getProperty('fullname') + ' <%s>' % ploneUser.getProperty('email'))
                try:
                    self.MailHost.send(body, recipient, fromAddress, subject, msg_type = 'text/plain', charset='utf-8')
                except socket.error, sg:
                    logger.warn( SENDMAIL_ERROR % str( sg ) )
                    break
                except UnicodeDecodeError, ue:
                    logger.warn( ENCODING_ERROR % str( ue ) )
                    break
                except MailHostError, mhe:
                    logger.warn( MAILHOST_ERROR % str( mhe ) )
                    break
                except Exception, e:
                    logger.warn( SENDMAIL_ERROR % str( e ) )
                    break

    security.declarePublic('indexExtractedText')
    def indexExtractedText(self):
        ''' This method extracts text from the binary content of this object
            and puts it in the index that corresponds to this method. It does so
            only if tool.extractTextFromFiles is True.

            If self.needsOcr is True, it does OCR recognition
            by calling command-line programs Poppler (pdftoppm) and Tesseract
            (tesseract). Poppler is used for converting a file into
            images and Tesseract is the OCR engine that converts those images
            into text. Tesseract needs to know in what p_ocrLanguage the file
            is written in'''
        return ''

    security.declarePublic('isConvertable')
    def isConvertable(self):
        '''Check if the mail is convertable (hopefully).  If the mail mimetype is one taken into
           account by collective.documentviewer CONVERTABLE_TYPES, then it should be convertable...
        '''
        mr = self.mimetypes_registry
        try:
            content_type = mr.lookup(self.content_type)
        except MimeTypeException:
            content_type = None
        if not content_type:
            logger.warning(CONTENT_TYPE_NOT_FOUND % self.absolute_url_path())
            return False
        # get printable extensions from collective.documentviewer
        printableExtensions = self._documentViewerPrintableExtensions()

        # mr.lookup returns a list
        extensions = content_type[0].extensions
        # now that we have the extensions, find the one we are using
        currentExtension = ''
        # in case we have myimage.JPG, make sure extension is lowercase as
        # extentions on mimetypes_registry are lowercase...
        try:
            filename = self.getFilename()
        except AttributeError:
            filename = self.getFile().filename
        file_extension = filename.split('.')[-1].lower()
        for extension in extensions:
            if file_extension == extension:
                currentExtension = extension
                break

        # if we found the exact extension we are using, we can see if it is in the list
        # of printable extensions provided by collective.documentviewer
        # most of times, this is True...
        if currentExtension in printableExtensions:
            return True
        if not currentExtension:
            logger.warning(FILE_EXTENSION_NOT_FOUND % (self.absolute_url_path(),
                                                       content_type[0]))

        # if we did not find the currentExtension in the mimetype's extensions,
        # for example an uploaded element without extension, check nevertheless
        # if the mimetype seems to be managed by collective.documentviewer
        if set(extensions).intersection(set(printableExtensions)):
            return True

        return False

    @memoize
    def _documentViewerPrintableExtensions(self):
        """
          Compute file extensions that will be considered as printable.
        """
        from collective.documentviewer.config import CONVERTABLE_TYPES
        printableExtensions = []
        for convertable_type in CONVERTABLE_TYPES.iteritems():
            printableExtensions.extend(convertable_type[1].extensions)
        return printableExtensions


registerType(CourrierFile, PROJECTNAME)
# end of class CourrierFile

##code-section module-footer #fill in your manual code here
#/#code-section module-footer