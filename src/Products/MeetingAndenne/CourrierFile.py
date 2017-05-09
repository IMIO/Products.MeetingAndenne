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
import locale
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
from Products.PloneMeeting.utils import getCustomAdapter, _getEmailAddress, \
                                        SENDMAIL_ERROR, ENCODING_ERROR, MAILHOST_ERROR

from DateTime import DateTime
from Products.MeetingAndenne.config import *
from Products.MeetingAndenne.utils import *

### OLD ###
#import time, unicodedata, socket
#from Products.PloneMeeting.utils import _getEmailAddress, getOsTempFolder, \
#     HubSessionsMarshaller, SENDMAIL_ERROR, ENCODING_ERROR, MAILHOST_ERROR

import logging
logger = logging.getLogger( 'MeetingAndenne' )

# Error-related constants ------------------------------------------------------
UNSUPPORTED_FORMAT_FOR_OCR = 'File "%s" could not be OCR-ized because mime ' \
    'type "%s" is not a supported input format. Supported input formats ' \
    'are: %s; %s.'
DUMP_FILE_ERROR = 'Error occurred while dumping or removing file "%s" on ' \
    'disk. %s'
GS_ERROR = 'An error occurred when using Ghostscript to convert "%s". Note ' \
    'that program "gs" must be in path.'
TESSERACT_ERROR = 'An error occurred when using Tesseract to OCR-ize file ' \
    '"%s". Note that program "tesseract" must be in path.'

GS_TIFF_COMMAND = 'gs -q -dNOPAUSE -dBATCH -sDEVICE=tiffg4 ' \
    '-sOutputFile=%s/%%04d.tif %s -c quit'
GS_INFO_COMMAND = 'Launching Ghoscript: %s'
POPPLER_COMMAND = 'pdftoppm -png %s %s'
POPPLER_INFO_COMMAND = 'Launching Poppler: %s'
POPPLER_ERROR = 'An error occurred when using Poppler to convert "%s". Note ' \
    'that program "pdftoppm" must be in path.'
TESSERACT_COMMAND = 'tesseract %s %s -l %s'
TESSERACT_INFO_COMMAND = 'Launching Tesseract: %s'
PDFTOTEXT_COMMAND = 'pdftotext %s %s'
PDFTOTEXT_INFO_COMMAND = 'Launching pdftotext: %s'
PDFTOTEXT_ERROR = 'An error occurred while converting a PDF file with ' \
    'pdftotext.'
##/code-section module-header

schema = Schema((

    StringField(
        name='refcourrier',
        default_method="getCourrierReference",
        widget=StringWidget(
            sqize= 100,
            label='Refdoc',
            label_msgid='MeetingAndenne_label_refCourrier',
            i18n_domain='MeetingAndenne',
        ),
        searchable=True,
        index="FieldIndex"
    ),

    StringField(
        name='typecourrier',
        index="FieldIndex",
        widget=SelectionWidget(
            label='Typecourrier',
            label_msgid='MeetingAndenne_label_type',
            i18n_domain='MeetingAndenne',
        ),
        vocabulary=MAIL_TYPES
    ),

    StringField(
        name='destOrigin',
        widget=StringWidget(
            size= 100,
            label='Destorigin',
            label_msgid='MeetingAndenne_label_destOrigin',
            i18n_domain='MeetingAndenne',
        ),
        searchable=True,
        index="FieldIndex"
    ),

    LinesField(
        name='destUsers',
        index="FieldIndex:brains",
        widget=MultiSelectionWidget(
            size=10,
            description="destUseritem",
            description_msgid="dest_user_item_descr",
            label='Destusers',
            label_msgid='Courrier_label_destUsers',
            i18n_domain='MeetingAndenne',
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
CourrierFile_schema['description'].widget.label_msgid='Courrier_label_description'
CourrierFile_schema['description'].widget.i18n_domain='PloneMeeting'
CourrierFile_schema['description'].widget.description_msgid='Courrier_label_description_descr'
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
    ocrFormatsOk = ('image/tiff',)
    ocrFormatsOkButConvertNeeded = ('application/pdf',)
    ocrAllFormatsOk = ocrFormatsOk + ocrFormatsOkButConvertNeeded
    ##/code-section class-header

    # Methods

    # Manually created methods

    # we must use a fieldindex index to sort but getCourrierReference is ZCTextIndex (use un search with *) thus we must create an index method an use a fake fieldindex
    security.declarePublic('getCourrierReference')
    def getRefcourrierFake(self):
        return self.getRefcourrier();

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
        os.system( "mv /home/zope/scan/scantmp/" + str(self.getId()) + " /home/zope/scan/scanarchived/" + str(self.getId()))

    security.declarePublic('listdestUsers')
    def listDestUsers(self):
        '''List the users that will be selectable to be in destination (view only) for this
           item.'''
        pgp = self.portal_membership
        res = []
        for user in pgp.listMembers():
            if user.getProperty('listed'):
                res.append( (user.getId(), user.getProperty('fullname')) )
        res = sorted( res, key=collateDisplayListsValues )
        return DisplayList( tuple(res) )

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
        self.needsOcr = rq.get('needs_ocr', None) is not None
        self.ocrLanguage = rq.get('ocr_language', 'fra')
        self.flaggedForOcr = False
        self.isOcrized = False
        # Reindexing the annex may have the effect of extracting text from the
        # binary content, if tool.extractTextFromFiles is True (see method
        # CourrierFile.indexExtractedText).
        self.reindexObject()

    security.declarePrivate('at_post_edit_script')
    def at_post_edit_script(self):
        rq = self.REQUEST
        self.updateLocalRoles()
        self.sendMailIfRelevant()
        self.needsOcr = rq.get('needs_ocr', None) is not None
        self.ocrLanguage = rq.get('ocr_language', 'fra')
        self.flaggedForOcr = False
        self.isOcrized = False
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
        enc = self.portal_properties.site_properties.getProperty( 'default_charset' )

        subjectLabel = 'Courrier_mail_subject'
        subject = self.utranslate( subjectLabel, domain="PloneMeeting" )
        subject = subject.encode( enc )

        bodyLabel = 'Courrier_mail_body'
        body = self.utranslate( bodyLabel, domain="PloneMeeting" ) + "<a href='http://andana.andenne.be:8080/commune/gestion-courrier/courrierall/" + self.getId() + "/view'>http://andana.andenne.be:8080/commune/gestion-courrier/courrierall/" + self.getId() + "/view</a>"
        body = body.encode( enc )

        fromAddress = _getEmailAddress( "ANDANA", portal.getProperty( 'email_from_address' ), enc )
        destUsers = self.getDestUsers()
        if destUsers:
            for destUser in destUsers:
                ploneUser = self.portal_membership.getMemberById( destUser )
                recipient = _getEmailAddress( ploneUser.getProperty( 'fullname' ), ploneUser.getProperty( 'email' ), enc )
                try:
                    self.MailHost.secureSend(
                    body, recipient, fromAddress, subject,
                    charset = 'utf-8', subtype = 'html' )
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
        if not hasattr( self.aq_base, 'needsOcr' ):
            return ''

        tool = self.portal_plonemeeting
        if not tool.getExtractTextFromFiles():
            return ''

        # Extracts the text from the binary content.
        extractedText = ''
        mimeType = self.content_type
        if self.needsOcr:
            # This if is added to prevent ocr-isation on the fly (when item is created or edited)
            # but to allow it when an ocr script is launched during the next night.
            if( hasattr( self, 'flaggedForOcr' ) and self.flaggedForOcr == True ):
                if mimeType in self.ocrAllFormatsOk:
                    try:
                        fileName = self.dump() # Dumps me on disk first
                        pngFolder = None
                        if mimeType in self.ocrFormatsOkButConvertNeeded:
                            # Poppler will be used to convert the file to
                            # "png" format. A folder where Poppler will
                            # generate one png file per PDF page will be created.
                            pngFolder = os.path.splitext( fileName )[0] + '.folder'
                            os.mkdir( pngFolder )
                            cmd = POPPLER_COMMAND % ( fileName, pngFolder + '/' )
                            logger.info( POPPLER_INFO_COMMAND % cmd )
                            os.system( cmd )
                            pngFiles = ['%s/%s' % ( pngFolder, f ) for f in \
                                        os.listdir( pngFolder )]
                            if not pngFiles:
                                logger.warn( POPPLER_ERROR % ( fileName ) )
                        else:
                            pngFiles = [fileName]
                        pngFiles.sort()
                        # Launch the OCR engine
                        for pngFile in pngFiles:
                            resFile = os.path.splitext( pngFile )[0]
                            resFilePlusExt = resFile + '.txt'
                            cmd = TESSERACT_COMMAND % ( pngFile, resFile,
                                                        self.ocrLanguage)
                            logger.info( TESSERACT_INFO_COMMAND % cmd )
                            os.system( cmd )
                            if not os.path.exists( resFilePlusExt ):
                                logger.warn( TESSERACT_ERROR % pngFile )
                            else:
                                f = file( resFilePlusExt )
                                extractedText += f.read()
                                f.close()
                                os.remove( resFilePlusExt )
                            os.remove( pngFile )
                        if pngFolder:
                            os.removedirs( pngFolder )
                        os.remove( fileName )
                    except OSError, oe:
                        logger.warn( DUMP_FILE_ERROR % ( self.getFilename(), str( oe ) ) )
                    except IOError, ie:
                        logger.warn( DUMP_FILE_ERROR % ( self.getFilename(), str( ie ) ) )
                else:
                    logger.warn( UNSUPPORTED_FORMAT_FOR_OCR % ( self.getFilename(),
                        mimeType, self.ocrFormatsOk,
                        self.ocrFormatsOkButConvertNeeded ) )
        else:
            fileName = self.dump() # Dumps me on disk first
            # Import the content of a not-to-ocr PDF file.
            resultFileName = os.path.splitext( fileName )[0] + '.txt'
            decodeNeeded = None
            if mimeType == 'application/pdf':
                cmd = PDFTOTEXT_COMMAND % ( fileName, resultFileName )
                logger.info( PDFTOTEXT_INFO_COMMAND % cmd )
                os.system( cmd )
                if not os.path.exists( resultFileName ):
                    logger.warn( PDFTOTEXT_ERROR )
            else:
                logger.info( 'Unable to index content of "%s"' % self.id )
            # Return temporary files written on disk and return the result.
            os.remove( fileName )
            if os.path.exists( resultFileName ):
                f = file( resultFileName )
                if decodeNeeded:
                    extractedText += f.read().decode( decodeNeeded )
                else:
                    extractedText += f.read()
                f.close()
                os.remove(resultFileName)
        return extractedText


registerType(CourrierFile, PROJECTNAME)
# end of class CourrierFile

##code-section module-footer #fill in your manual code here
#/#code-section module-footer