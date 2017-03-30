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

from appy.gen import No
from zope.interface import implements
from zope.i18n import translate
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import DisplayList
from Globals import InitializeClass
from Products.CMFCore.permissions import ModifyPortalContent, ReviewPortalContent
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from plone.app.users.browser.personalpreferences import PersonalPreferencesPanelAdapter
from imio.helpers.xhtml import xhtmlContentIsEmpty
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE, \
     TOPIC_SEARCH_SCRIPT, TOPIC_SEARCH_FILTERS, TOPIC_TYPE
from Products.PloneMeeting.Meeting import MeetingWorkflowActions, \
     MeetingWorkflowConditions, Meeting
from Products.PloneMeeting.MeetingItem import MeetingItem, \
     MeetingItemWorkflowConditions, MeetingItemWorkflowActions
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.ToolPloneMeeting import ToolPloneMeeting
from Products.PloneMeeting.interfaces import IMeetingCustom, IMeetingItemCustom, \
                                             IMeetingFileCustom, IMeetingConfigCustom, \
                                             IToolPloneMeetingCustom
from Products.PloneMeeting.MeetingFile import MeetingFile
from Products.MeetingAndenne.interfaces import \
     IMeetingItemCollegeAndenneWorkflowActions, IMeetingItemCollegeAndenneWorkflowConditions, \
     IMeetingCollegeAndenneWorkflowActions, IMeetingCollegeAndenneWorkflowConditions
from Products.MeetingAndenne.config import MAIL_TYPES, SEARCH_TYPES
from Products.MeetingAndenne.SearcherAndenne import SearcherAndenne
from Products.PloneMeeting.utils import checkPermission, sendMail, getLastEvent, spanifyLink
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import WF_DOES_NOT_EXIST_WARNING, WF_APPLIED
from DateTime import DateTime

# Some lines added for the OCR functionalities
import os, os.path, time, unicodedata
import transaction
import logging
logger = logging.getLogger( 'MeetingAndenne' )


# ------------------------------------------------------------------------------
class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """
    def get_function(self):
        return self.context.getProperty('function', '')
    def set_function(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties( {'function': value} )
    function = property(get_function, set_function)

    def get_gender(self):
        return self.context.getProperty('gender', '')
    def set_gender(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties( {'gender': value} )
    gender = property(get_gender, set_gender)


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
class CustomMeetingAndenne(Meeting):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    ##### Functions used for template generation ############################

    security.declarePublic('getDisplayableName')
    def getDisplayableName(self):
        '''Formats the name of a meeting in the way it is printed in templates.'''
        meeting = self.getSelf()
        return meeting.portal_plonemeeting.formatMeetingDate(meeting=meeting, withHour=True)

    Meeting.getDisplayableName=getDisplayableName
    # it'a a monkey patch because it's the only way to add a behaviour to the Meeting class

    security.declarePublic('getSignatoriesForPrinting') 
    def getSignatoriesForPrinting (self, pos=0, level=0, useforpv=False, userepl=True):
        '''To be changed.'''
        # new from plonemeeting 3.3 :print sigantories in template relative to position ans level. pos 0 and level 0 is the first sigantory (bg) and function. 
        # pos 0 and level 1 is the first signatory (bg) with Name
        res = []
        meeting = self.getSelf()
        res = meeting.getSignatories(theObjects = True, includeDeleted = False, includeReplacements = userepl)
        if level == 1:
            return res[pos].Title()
        else:
            # specialement utilisé pour l'affichae avant migration ou apres migration si la personne remplacante a été oubliée 
            # Si c'est un echevin on remplace par bg ff, si c'est un secretaire en general on a deja un dg f.f dans la fonction  principale de celui qui remplace)
            # le getduty revoit la fonction remplacé si includereplacement=true et qu'il y a vraiment un remplaçant inscrit (grace au fakemeetinguser revoyer à la place)
            duty = res[pos].getDuty()
            if duty=="Echevin":
                return "Bourgmestre f.f"
            else:
                return duty

    security.declarePublic('reformAssembly')
    def reformAssembly(self, assembly, strikefirst=True, strikemidle=True, strikelast=False, userepl=True):
        '''To be changed.'''
        # new from plonemeeting 3.3 : used for template only in the header of pv and other. use the return of getstrikeassembly (and item) function to add the replacement user
        # pour une personne absente, soit on la barre (strike=true) , soit on la supprime (strike=false)
        # on peut decider de barrer ou supprimer la premiere ligne (bg) , les lignes du milieu (echevin) ou la derniere ligne (directeur)
        # le comportement par defaut est celui que l'on veur pour la note d'execution
        # on tiendra compte du "remplacé par" si usereplace=true mais on ne tiendra pas compte du "remplacé par" si on barre ou si userplace=false  
        res = []
        meeting = self.getSelf()
        repl = meeting.getUserReplacements()
        repl2 = [repl[user] for user in repl]
        UsedMeetingUsers = meeting.getAllUsedMeetingUsers()
        # liste des gens remplaçant possible a faire correspondre avec la combo "remplacé par" sinon soucis !
        UsedMeetingUsers2 = meeting.getAllUsedMeetingUsers(usages = ('assemblyMember', 'signer', ), includeAllActive = True )
        lines = assembly.split('<br />')
        #print UsedMeetingUsers
        m = 0
        for line in lines:
            my_line = ''
            fct = line.split(' - ')
            fctline = fct[1]
            minline = 0
            members = fct[0].split(', ')
            for member in members:
                #print member
                if userepl == True:
                    ### ce members est-il a remplacer ?
                    if UsedMeetingUsers[m].getId() in repl :
                        # si on decide de barrer le membre, on ne va pas le faire remplacer, donc comportement par defaut, sinon, on essaye ou pas de trouver un remplaçant
                        if( strikefirst == True and m == 0 ) or ( strikemidle == True and m > 0 and m < len(UsedMeetingUsers) - 1) or (strikelast == True and m == len(UsedMeetingUsers) - 1):
                            my_line = "%s%s, " % (my_line,member)
                        else:
                            r = [mUser.Title() for mUser in UsedMeetingUsers2 if mUser.getId() == repl[UsedMeetingUsers[m].getId()]]
                            #f=[mUser.getReplacementDuty() for mUser in UsedMeetingUsers2 if mUser.getId() == repl[UsedMeetingUsers[m].getId()]]
                            f = UsedMeetingUsers[m].getReplacementDuty()               
                            if m == 0:
                                my_line = "%s%s, " % ("<p class='mltAssembly'>",r[0])
                            else:
                                my_line = "%s%s, " % (my_line,r[0])

                            if m == len(UsedMeetingUsers) - 1:
                                fctline= "%s%s" % (f,"</p>")
                            else:
                                fctline= f
                    else:
                        ### ce membre remplace t'il quelqu'un qui n'est pas barré ?
                        if UsedMeetingUsers[m].getId() in repl2 and (strikefirst == False or UsedMeetingUsers[m].getId() <> repl[UsedMeetingUsers[0].getId()]) and (strikemidle == False or UsedMeetingUsers[m].getId() == repl[UsedMeetingUsers[0].getId()] or UsedMeetingUsers[m].getId() == repl[UsedMeetingUsers[len(UsedMeetingUsers) - 1].getId()]) and (strikelast == False or UsedMeetingUsers[m].getId() <> repl[UsedMeetingUsers[len(UsedMeetingUsers) - 1].getId()]):
                            minline -= 1 
                        else:
                            if (strikefirst == True and m == 0) or (strikemidle == True and m > 0 and m < len(UsedMeetingUsers) - 1) or (strikelast == True and m == len(UsedMeetingUsers) - 1):
                                my_line = "%s%s, " % (my_line,member)
                            else:
                                if member.find("<strike>") <> -1:
                                    minline -= 1
                                    if (m == 0):
                                        my_line = "<p class='mltAssembly'>"
                                    if (m == len(UsedMeetingUsers) - 1):
                                        my_line = "%s%s" % (my_line,"</p>")
                                else:
                                    my_line = "%s%s, " % (my_line,member)
                else:
                    if (strikefirst == True and m == 0) or (strikemidle == True and m > 0 and m < len(UsedMeetingUsers) - 1) or (strikelast == True and m == len(UsedMeetingUsers) - 1):
                        ### on  barre  et on ne remplace pas, on va donc simplement suivre le comportement par default 
                        my_line = "%s%s, " % (my_line,member)
                    else:
                       if member.find("<strike>") <> -1:
                           minline -= 1
                           if (m == 0):
                               my_line = "<p class='mltAssembly'>"
                           if (m == len(UsedMeetingUsers) - 1):
                               my_line = "%s%s" % (my_line,"</p>")
                       else:
                           my_line = "%s%s, " % (my_line,member)

                m += 1
                minline += 1

            if minline > 0:
                my_line = "%s%s<br />" % (my_line,fctline)
            print my_line
            res.append(my_line)

        if len(res) > 1:
            res[-1] = res[-1].replace('<br />', '')
        else:
            return ''
        print ''.join(res)
        return ''.join(res)

    security.declarePublic('getAbsentsForPrinting') 
    def getAbsentsForPrinting(self):
        '''Generates a HTML version of absents in a Meeting.'''
        meeting = self.getSelf()
        res = ''
        absents = meeting.getAbsents(theObjects = True) + meeting.getExcused(theObjects = True)
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
        def getPrintableNumCategory(current_cat):
            '''Method used here above.'''
            current_cat_id = current_cat.getId()
            current_cat_name = current_cat.Title()
            current_cat_name = current_cat_name[0:2]
            try:
                catNum = int(current_cat_name)
            except ValueError:
                current_cat_name = current_cat_name[0:1]
                try:
                    catNum = int(current_cat_name)
                except ValueError:
                    catNum = current_cat_id
            return catNum

        itemsGetter = self.context.getItems
        if late:
            itemsGetter = self.context.getLateItems
        items = itemsGetter()
        if allItems:
            items = self.context.getItems() + self.context.getLateItems()
        # res contains all items by category, the key of res is the category
        # number. Pay attention that the category number is obtain by extracting
        # the 2 first caracters of the categoryname, thus the categoryname must
        # be for exemple ' 2.travaux' or '10.Urbanisme. If not, the catnum takes
        # the value of the id + 1000 to be sure to place those categories at the
        # end.
        res = {}
        # First, we create the category and for each category, we create a
        # dictionary that must contain the list of item in in res[catnum][1]
        for item in items:
            if uids:
                if (item.UID() in uids):
                    inuid = "ok"
                else:
                    inuid = "ko"
            else:
                inuid = "ok"
            if (inuid == "ok"):
                current_cat = item.getCategory(theObject=True)
                catNum = getPrintableNumCategory(current_cat)
                if catNum in res:
                    res[catNum][1][item.getItemNumber()] = item
                else:
                    res[catNum] = {}
                    #first value of the list is the category object
                    res[catNum][0] = item.getCategory(True)
                    #second value of the list is a list of items
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
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
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
        # Add our icons for accepted_but_modified and pre_accepted
        itemState = item.queryState()
        if itemState == 'accepted_but_modified':
            res.append(('accepted_but_modified.png', 'icon_help_accepted_but_modified'))
        elif itemState == 'pre_accepted':
            res.append(('pre_accepted.png', 'icon_help_pre_accepted'))
        return res

    ##### End Overrides MeetingCommunes MeetingItemCustom adapter ###########

    ##### Functions used for template generation ############################

    security.declarePublic('getPrintableCopyTo')
    def getPrintableCopyTo(self):
        '''Formats the copyGroups field to print in the templates.'''
        groupsCopyTo = self.context.getCopyGroups()
        groupstr=''
        if groupsCopyTo:
            for group in groupsCopyTo:
                ploneGroup = self.context.portal_groups.getGroupById(group)
                groupstr += ploneGroup.getProperty('title').split('(')[0] + ','
        if groupstr != '':
            return 'Copie(s): ' + groupstr[0:-1]
        else:
            return ''

    security.declarePublic('getPrintableCopyTo')
    def getPrintableNumCategory(self):
        '''Formats the category number to print in the templates.'''
        current_cat = self.context.getCategory(theObject=True)
        current_cat_id = current_cat.getId()
        current_cat_name = current_cat.Title()
        current_cat_name = current_cat_name[0:2]
        try:
            catNum = int(current_cat_name)
        except ValueError:
            current_cat_name = current_cat_name[0:1]
            try:
                catNum = int(current_cat_name)
            except ValueError:
                catNum = current_cat_id
        return catNum

    security.declarePublic('reformAssembly')
    def reformAssembly(self, assembly, strikefirst=True, strikemiddle=True, strikelast=False, userepl=True ):
        '''Formats the attendees to print in the templates.'''
        item = self.getSelf()
        meeting = item.getMeeting().adapted()
        return meeting.reformAssembly(assembly, strikefirst, strikemiddle, strikelast, userepl)

    security.declarePublic('getSignatoriesForPrinting') 
    def getSignatoriesForPrinting (self, pos=0, level=0, useforpv=False, userepl=True):
        # new from plonemeeting 3.3 :print sigantories in template relative to position ans level. pos 0 and level 0 is the first sigantory (bg) and function. 
        # pos 0 and level 1 is the first signatory (bg) with Name
        res = []
        i = 0
        item = self.getSelf()
        res = item.getItemSignatories(theObjects = True, includeDeleted = False, includeReplacements = userepl)
        resworepl = item.getItemSignatories(theObjects = True, includeDeleted = False, includeReplacements = False)
        for attendee in item.getItemPresents():
            i = 0
            for mUser in resworepl:
                if mUser.id == attendee:
                    res[i] = resworepl[i]

        if level == 1:
            return res[pos].Title()
        else:
            # specialement utilisé pour l'affichae avant migration ou apres migration si la personne remplacante a été oubliée 
            # Si c'est un echevin on remplace par bg ff, si c'est un secretaire en general on a deja un dg f.f dans la fonction  principale de celui qui remplace)
            # le getduty revoit la fonction remplacé si includereplacement=true et qu'il y a vraiment un remplaçant inscrit (grace au fakemeetinguser revoyer à la place)
            duty = res[pos].getDuty()
            if duty == "Echevin":
                return "Bourgmestre f.f"
            else:
                return duty

    security.declarePublic('getItemAbsentsForPrinting') 
    def getItemAbsentsForPrinting(self):
        item = self.getSelf()
        res = ''
        absents = item.getItemAbsents(theObjects = True)
        if absents:
            res = "<p class='mltAssembly'>"
            for user in absents:
                res += "%s, %s<br />" % (user.Title(), user.getDuty())
            res += "</p>"
        return res

    security.declarePublic('getCurrentDate')
    def getCurrentDate(self):
        '''Formats the current date to print in the templates.'''
        return DateTime().strftime("%d/%m/%Y")

### New functionalities ###

    ### TO BE CHANGED ###
    security.declarePublic('updateMeetingItem')
    def updateMeetingItem(self):
        """
           Update a MeetingItem object following a copygroups on-the-fly modification.
        """
        self.updateLocalRoles()
#        self.adapted().onEdit(isCreated=False)
        self.reindexObject()

    MeetingItem.updateMeetingItem=updateMeetingItem
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePublic('getExtraFieldsToCopyWhenCloning')
    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc):
        '''Lists the fields to keep when cloning an item'''
        return ['projetpv', 'textpv', 'pv']

#    security.declarePublic('replaceBr')
#    def replaceBr (self,text):
#        description=text
#
#        pos=description.find("<br />")
#        while pos <> -1 :
#            ol=description.count("<ol>",0,pos)
#            ul=description.count ("<ul>",0,pos)
#            li=description.count("<li>",0,pos)
#            sol=description.count ("</ol>",0,pos)
#            sul=description.count("</ul>",0,pos)
#            sli=description.count ("</li>",0,pos)
#            print "ol="+str(ol)+" ul="+str(ul)+" li="+str(li)+" sol="+str(sol)+" sul="+str(sul)+" sli="+str(sli)
#            if ol <= sol and ul <= sul and li <= sli:
#                p=description.count ("<p",0,pos)
#                sp=description.count("</p>",0,pos)
#
#                print "p="+str(p)+" sp="+str(sp)
#
#                if p > sp:
#                    strong=description.rfind ("<strong>",0,pos)
#                    strike=description.rfind("<strike>",0,pos)
#                    u=description.rfind("<u>",0,pos)
#                    em=description.rfind("<em>",0,pos)
#                    sup=description.rfind("<sup>",0,pos)
#                    sub=description.rfind("<sub>",0,pos)
#                    font=description.rfind("<font",0,pos)
#                    span=description.rfind("<span",0,pos)
#                    sstrong=description.rfind("</strong>",0,pos)
#                    sstrike=description.rfind("</strike>",0,pos)
#                    su=description.rfind("</u>",0,pos)
#                    sem=description.rfind("</em>",0,pos)
#                    ssub=description.rfind("</sub>",0,pos)
#                    ssup=description.rfind("</sup>",0,pos)
#                    sfont=description.rfind("</font>",0,pos)
#                    sspan=description.rfind("</span>",0,pos)
#                    htmltuple=[]
#                    if strong > sstrong:
#                        htmltuple.append(("<strong>","</strong>",strong))
#                    if strike > sstrike:
#                        htmltuple.append(("<strike>","</strike>",strike))
#                    if u > su:
#                        htmltuple.append(("<u>","</u>",u))
#                    if em > sem:
#                        htmltuple.append(("<em>","</em>",em))
#                    if sup > ssup:
#                        htmltuple.append(("<sup>","</sup>",sup))
#                    if sub > ssub:
#                        htmltuple.append(("<sub>","</sub>",sub))
#                    if font > sfont:
#                        htmltuple.append(("<font>","</font>",font))
#                    if span > sspan:
#                        htmltuple.append(("<span>","</span>",span))
#
#                    htmltupleclose=sorted(htmltuple, key=lambda student: student[2],reverse=True)
#                    htmltupleopen=sorted(htmltuple, key=lambda student: student[2])
#                    strhtmlclose=""
#                    strhtmlopen=""
#                    for i in htmltupleclose:
#                        strhtmlclose=strhtmlclose+i[1]
#                    for i in htmltupleopen:
#                        strhtmlopen=strhtmlopen+i[0]
#                    description = description.replace("<br />",strhtmlclose+"</p><p>"+strhtmlopen,1)
#                else:
#                    description = description.replace("<br />","<p>&nbsp;</p>",1)
#            else:
#                description = description.replace("<br />","",1)
#            pos=description.find("<br />")
#
#        pos=description.find("<table")
#        while pos <> -1:
#            tdend=description.find("</table",pos)
#            if (description.count("<p",pos,tdend)>0):
#                l=list(description)
#                l[pos:tdend]=list(description[pos:tdend].replace("<p","<span",10).replace("</p>","</span>",10))
#                description="".join(l)
#            pos=description.find("<table",pos+1)
#        return description
#
#
#    security.declarePublic('setOcrFlag')
#    def setOcrFlag(self):
#        """
#            Update a MeetingItem object setting the OCR Flag.
#        """
#        uploadedFiles = self.portal_catalog( portal_type='MeetingFile' )
##        uploadedFiles = self.portal_catalog( portal_type='CourrierFile' )
#
#        logger.info( "Flag OCR sur les annexes" )
#
##        import db
##        pdb.set_trace()
#
#        count = len( uploadedFiles )
#        cpt = 1
#        for uploadedFile in uploadedFiles:
#
#            logline = "Element %d / %d" % ( cpt, count )
#            logger.info( logline )
#
#            if( uploadedFile.id[-4:] == ".pdf" ):
#                fileObject = uploadedFile.getObject()
#                fileObject.needsOcr = True
#                fileObject.ocrLanguage = 'fra'
#                fileObject.flaggedForOcr = False
#                fileObject.isOcrized = False
#
#            cpt = cpt + 1
#
#            if( cpt % 100 == 0 ):
#                transaction.get().commit( True )
#                logger.info( "Commit partiel effectue" )
#
#    MeetingItem.setOcrFlag=setOcrFlag
#
#
#    security.declarePublic('ocrItems')
#    def ocrItems(self):
#        """
#            Update a MeetingItem object setting the extractedText attribute.
#        """
#        logger.info( "Traitement OCR sur les courriers" )
#
##        uploadedFiles = self.portal_catalog( portal_type='CourrierFile' )
#
#        count = len( uploadedFiles )
#        cpt = 1
#        updated = 0
#        for uploadedFile in uploadedFiles:
#
#            logline = "Element %d / %d" % ( cpt, count )
#            logger.info( logline )
#
#            if( uploadedFile.id[-4:] == ".pdf" ):
#                fileObject = uploadedFile.getObject()
#
#                if( fileObject.needsOcr == True and fileObject.isOcrized == False ):
#                    fileObject.flaggedForOcr = True
#
#                    fileObject.reindexObject()
#
#                    fileObject.isOcrized = True
#                    fileObject.flaggedForOcr = False
#
#                    updated = updated + 1
#                    logline = "%d elements traites" % ( updated )
#                    logger.info( logline )
#
#            cpt = cpt + 1
#
#            if( updated % 100 == 0 and updated != 0 ):
#                transaction.savepoint( optimistic = True )
#                logger.info( "Commit partiel effectue" )
#
#            if( updated >= 1000 ):
#                break
#
#        logger.info( "Traitement OCR sur les annexes" )
#
##        uploadedFiles = self.portal_catalog( portal_type='MeetingFile' )
#
##        count = len( uploadedFiles )
##        cpt = 1
##        for uploadedFile in uploadedFiles:
#
##            logline = "Element %d / %d - %s" % ( cpt, count, uploadedFile.getURL() )
##            logger.info( logline )
#
##            fileObject = uploadedFile.getObject()
##            if( fileObject.needsOcr == True and fileObject.isOcrized == False ):
##                if( uploadedFile.id[-4:] == ".pdf" ):
##                    fileObject.flaggedForOcr = True
#
##                    fileObject.reindexObject()
#
##                    fileObject.isOcrized = True
##                    fileObject.flaggedForOcr = False
##                else:
##                    fileObject.reindexObject()
#
##                updated = updated + 1
##                logline = "%d elements traites" % ( updated )
##                logger.info( logline )
#
#            cpt = cpt + 1
#
##            if( updated % 100 == 0 and updated != 0 ):
#                transaction.savepoint( optimistic = True )
##                logger.info( "Commit partiel effectue" )
#
##            if( updated >= 1000 ):
##                break
#
##        logger.info( "Fin de la numerisation, %d elements numerises" % (updated) )
##        transaction.get().commit()
#
#    MeetingItem.ocrItems=ocrItems
#
#
#
#
#    security.declarePublic('onEdit')
#    def onEdit(self,isCreated):
#        # replace de div for p, because xhtmlparlser convert div to page-break and it cause problem in text align justify
#        # replace line break for </p><p> because line break are in <p> and cause justify problems
#        if (self.context.isformation()):
#            if (isCreated):
#                self.context.setRefdoc(self.context.getDocReference())
#                self.context.setVerifUser(self.Creator())
#                self.context.setTreatUser(self.Creator())
#                # Needed because we have to put a default value, otherwise we can't add a new MeetingItem. To remove, with the default values
#                # in the pm_updates when there will be a real TrainingItem type
#                self.context.setFormation_name("")
#                self.context.setFormation_objet("")
#                self.context.setFormation_place("")
#                self.context.setFormation_date1("")
#                self.context.setFormation_date2("")
#                self.context.setBudgetInfos(self.context.translate('MeetingAndenne_default_budgetInfos', domain='PloneMeeting'))
#            else:
#                label1=self.context.translate('MeetingAndenne_label_formation_description1', domain='PloneMeeting').encode('utf-8')
#                label2=self.context.translate('MeetingAndenne_label_formation_description2', domain='PloneMeeting').encode('utf-8')
#                label1d=self.context.translate('MeetingAndenne_label_formation_decision1', domain='PloneMeeting').encode('utf-8')
#                label2d=self.context.translate('MeetingAndenne_label_formation_decision2', domain='PloneMeeting').encode('utf-8')
#                label3d=self.context.translate('MeetingAndenne_label_formation_decision3', domain='PloneMeeting').encode('utf-8')
#                import locale
#                loc=locale.getlocale()
#                locale.setlocale(locale.LC_ALL,'fr_FR.utf8')
#                if self.context.getFormation_periode()!="":
#                    formation_periode=", "+self.context.getFormation_periode()+","
#                else:
#                    formation_periode=""
#                label1F=label1 % {'formation_date1':self.context.getFormation_date1().strftime("%d %B %Y à %H:%M"),'formation_date2':self.context.getFormation_date2().strftime("%d %B %Y à %H:%M"),'formation_periode':formation_periode,'formation_name':self.context.getFormation_name(),'formation_type':self.context.getFormation_type(),'formation_objet':self.context.getFormation_objet()}
#                i=0
#                formation_users=""
#                formation_user=self.context.getFormation_user()
#                for user in self.context.getFormation_users():
#                    i=i+1
#                    ploneUser=self.context.portal_membership.getMemberById(user)
#                    if (ploneUser.getProperty('function')):
#                        function=", " + ploneUser.getProperty('function')
#                    else:
#                        function=""
#                    if (ploneUser.getProperty('gender')):
#                        gender=ploneUser.getProperty('gender')
#                        if gender=='homme':
#                            gender="Monsieur "
#                        elif gender=='femme':
#                            gender="Madame "
#                        else:
#                            gender=""
#                    else:
#                        gender=""
#                    if i > 1:
#                        if ( len(self.context.getFormation_users()) == i and formation_user == ""):
#                            formation_users=formation_users+" et "
#                        else:
#                            formation_users=formation_users+", "
#                    formation_users=formation_users+gender+ploneUser.getProperty('fullname')+function
#                if formation_user != "":
#                    if formation_users != "":
#                        formation_users=formation_users+", "+formation_user
#                    else:
#                        formation_users=formation_user
#                budget_array=self.adapted().extractBudget()
#                formation_price=budget_array[0]
#                formation_budget=budget_array[1]
#                label1dF=label1d % {'formation_users':formation_users,'formation_type':self.context.getFormation_type(),'formation_objet':self.context.getFormation_objet(),'formation_name':self.context.getFormation_name(),'formation_date1':self.context.getFormation_date1().strftime("%d %B %Y à %H:%M"),'formation_date2':self.context.getFormation_date2().strftime("%d %B %Y à %H:%M"),'formation_periode':formation_periode,'formation_place':self.context.getFormation_place()}
#                if (formation_price != ''):
#                    label2dF=label2d % {'formation_price':formation_price,'formation_budget':formation_budget}
#                    payement=''
#                    if (self.context.getFormation_mod()):
#                        res=self.context.listFormationMod(False)
#                        if (self.context.getFormation_mod()== '1'):
#                            payement="<p>"+res[0][1]+"</p>"
#                        else:
#                            payement="<p>"+res[1][1]+self.context.translate('MeetingAndenne_text_formation_compte', domain='PloneMeeting').encode('utf-8')+self.context.getFormation_compte()+" "+self.context.translate('MeetingAndenne_text_formation_compte_name', domain='PloneMeeting').encode('utf-8')+self.context.getFormation_compte_name()+" "+self.context.translate('MeetingAndenne_text_formation_compte_com', domain='PloneMeeting').encode('utf-8')+self.context.getFormation_compte_com()+"</p>"
#                else:
#                    label2dF=self.context.translate('MeetingAndenne_label_formation_decision2free', domain='PloneMeeting').encode('utf-8')
#                    payement=''
#                if i < 2:
#                    usertitle=" - "+formation_users
#                else:
#                    usertitle=""
#
#                #on ne remplace pas le titre si on est en mode template car le titre doit rester le meme pour l'affichage du template
#                if self.context.queryState() != "active":
#                    self.context.setTitle("Demande de formation - "+self.context.getFormation_objet()+usertitle)
#
#                self.context.setDecision(label1dF+label2dF+payement+label3d)
#                self.context.setDescription(label1F+"<p>"+self.context.getFormation_desc()+"</p>"+label2dF+label2)
#                locale.setlocale(locale.LC_ALL,loc)
#
#        self.context.setDescription(self.context.Description().replace("<div","<p"))
#        self.context.setDescription(self.context.Description().replace("</div>","</p>"))
#        self.context.setDescription(self.context.replaceBr(self.context.Description()))
#        #self.context.setDescription(self.context.Description().replace("<br>","</p><p>"))
#
#        self.context.setTextpv(self.context.getTextpv().replace("<div","<p"))
#        self.context.setTextpv(self.context.getTextpv().replace("</div>","</p>"))
#        self.context.setTextpv(self.context.replaceBr(self.context.getTextpv()))
#
#        self.context.setPv(self.context.getPv().replace("<div","<p"))
#        self.context.setPv(self.context.getPv().replace("</div>","</p>"))
#        self.context.setPv(self.context.replaceBr(self.context.getPv()))
#
#        self.context.setProjetpv(self.context.getProjetpv().replace("<div","<p"))
#        self.context.setProjetpv(self.context.getProjetpv().replace("</div>","</p>"))
#        self.context.setProjetpv(self.context.replaceBr(self.context.getProjetpv()))
#
#        self.context.setDecision(self.context.getDecision().replace("<div","<p"))
#        self.context.setDecision(self.context.getDecision().replace("</div>","</p>"))
#        self.context.setDecision(self.context.replaceBr(self.context.getDecision()))
#
#        # Add the local roles corresponding to the proposing group for personnel and when is't confidential
#        tool = self.context.portal_plonemeeting
#
#        if self.context.getIsconfidential()==True:
#            MEETINGROLES = {'reviewers': 'MeetingReviewer'}
#            MEETINGROLESTOREMOVE = {'reviewers': 'MeetingReviewer',
#                'observers': 'MeetingObserverLocal','creators':'MeetingMember'}
#        else:
#            MEETINGROLES = {'reviewers': 'MeetingReviewer',
#                'observers': 'MeetingObserverLocal'}
#            MEETINGROLESTOREMOVE = {'reviewers': 'MeetingReviewer'}
#        #remove the locale roles
#        if self.context.getCategory() == "45-personnel" or self.context.getIsconfidential()==True:
#            meetingGroup = getattr(tool, self.context.getProposingGroup(), None)
#            if meetingGroup:
#                for groupSuffix in MEETINGROLESTOREMOVE.iterkeys():
#                    groupId = meetingGroup.getPloneGroupId(groupSuffix)
#                    self.context.manage_delLocalRoles([groupId])
#                    ploneGroup = self.context.portal_groups.getGroupById(groupId)
#                    # If the corresponding Plone group does not exist anymore,
#                    # recreate it.
#                    if not ploneGroup:
#                        meetingGroup._createPloneGroup(groupSuffix)
#                    meetingRole = ploneGroup.getProperties()['meetingRole']
#                    #self.context.manage_addLocalRoles(groupId, (meetingRole,))
#
#        if self.context.getCategory() == "45-personnel":
#            meetingGroup = getattr(tool, "personnel", None)
#        else:
#            meetingGroup = getattr(tool, self.context.getProposingGroup(), None)
#
#        # add the local role for personnel or confidential point
#        if self.context.getCategory() == "45-personnel" or self.context.getIsconfidential()== True:
#            if meetingGroup:
#                for groupSuffix in MEETINGROLES.iterkeys():
#                    groupId = meetingGroup.getPloneGroupId(groupSuffix)
#                    ploneGroup = self.context.portal_groups.getGroupById(groupId)
#                    # If the corresponding Plone group does not exist anymore,
#                    # recreate it.
#                    if not ploneGroup:
#                        meetingGroup._createPloneGroup(groupSuffix)
#                    meetingRole = ploneGroup.getProperties()['meetingRole']
#                    self.context.manage_addLocalRoles(groupId, (meetingRole,))
#        #add role owner for jm mathieu (CPAS) on created state (to permit JM to edit and propose all created item in CPAS)
#        # NOT USE SINCE 20-03-2014 MAY BE REUSE LATER
#        #if self.context.getProposingGroup() == 'cpas':
#        #    self.context.manage_addLocalRoles('marmat', ('Owner',))
#        #add local role for associated group
#        assGroups = self.context.getAssociatedGroups()
#        if assGroups:
#            for assGroup in assGroups:
#                groupId = assGroup+'_creators'
#                ploneGroup = self.context.portal_groups.getGroupById(groupId)
#            self.context.manage_addLocalRoles(groupId, ('MeetingMember',))
#
#    security.declarePublic('getDefaultBudgetInfo')
#    def getDefaultBudgetInfo(self):
#        '''The default budget info is to be found in the config.'''
#        meetingConfig = self.portal_plonemeeting.getMeetingConfig(self)
#        return meetingConfig.getRawBudgetDefault()
#
#    #it' a monkey patch
#    MeetingItem.getDefaultBudgetInfo=getDefaultBudgetInfo
#
#
#    security.declarePublic('OnPaste')
#    def OnPaste(self):
#        self.context.at_post_create_script()
#
#    security.declarePublic('projetpvFieldIsEmpty')
#    def projetpvFieldIsEmpty(self):
#        '''Is the 'projetpv' field empty ? '''
#        return kupuFieldIsEmpty(self.context.getProjetpv())
#
#    security.declarePublic('pvFieldIsEmpty')
#    def pvFieldIsEmpty(self):
#        '''Is the 'decision' field empty ? '''
#        return kupuFieldIsEmpty(self.context.getPv())
#
#    security.declarePublic('textpvFieldIsEmpty')
#    def textpvFieldIsEmpty(self):
#        '''Is the 'decision' field empty ? '''
#        return kupuFieldIsEmpty(self.context.getTextpv())

    security.declarePublic('getDocReference')
    def getDocReference(self):
        '''Return a too complicated item reference to be defined as a TAL Expression
           (field MeetingConfig.itemReferenceFormat.'''
        userMeetingGroups = self.portal_plonemeeting.getGroupsForUser(suffix="creators")
        if len(userMeetingGroups) >= 1:
            ref = userMeetingGroups[-1].getAcronym()
        else:
            ref = 'XXXX'
        return ref + '/XX.XX/' + DateTime(self.CreationDate()).strftime('%Y.%m') + '/'

    MeetingItem.getDocReference = getDocReference
    # it'a a monkey patch because it's the only way to have a default method in the schema

    security.declarePublic('listUserGroup')
    def listUserGroup(self):
        '''Lists the Users that are associated to the proposing group(s) of the authenticated user.'''
        userCreatorGroups = self.portal_plonemeeting.getGroupsForUser(suffix="creators", userId = self.Creator(), zope=True)

        res = set()
        for group in userCreatorGroups:
            for user in group.getMemberIds():
                res.add( (user, self.portal_membership.getMemberById(user).getProperty('fullname')) )

        return DisplayList( tuple(res) )

    MeetingItem.listUserGroup = listUserGroup
    # it'a a monkey patch because it's the only way to have a default method in the schema

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

#    security.declarePublic('getAttendees')
#    def getAttendees(self, usage=None, includeDeleted=False, includeAbsents=False, includeReplacements=False):
#        '''Returns the attendees for this item. Takes into account
#           self.itemAbsents, excepted if p_includeAbsents is True. If a given
#           p_usage is defined, the method returns only users having this
#           p_usage.'''
#        res = []
#        if self.hasMeeting():
#            # Prevent wrong parameters use
#            if includeDeleted and usage:
#                includeDeleted = False
#            res = []
#            meetingConfig = self.portal_plonemeeting.getMeetingConfig(self)
#            itemAbsents = ()
#            itemPresents = ()
#            itemPresentsinmeeting = ()
#            if not includeAbsents:
#                itemAbsents = self.getItemAbsents()
#                itemPresents=self.getItemPresents()
#                itemPresentsinmeeting=self.getMeeting().getAttendees(False,includeDeleted=includeDeleted)
#                for attendee in meetingConfig.getActiveMeetingUsers():
#                    if (attendee.id in itemPresentsinmeeting or attendee.id in itemPresents ) and attendee.id not in itemAbsents:
#                        if not usage or (usage in attendee.getUsages()):
#                            res.append(attendee)
#        return res
#
#    MeetingItem.getAttendees=getAttendees
#    # it'a a monkey patch
#
    security.declarePublic('onDuplicate')
    def onDuplicate(self):
        '''This method is triggered when the users clicks on
           "duplicate item".'''
        user = self.portal_membership.getAuthenticatedMember()
        newItem = self.clone(newOwnerId=user.id, cloneEventAction='Duplicate')
        newItem.setDecision(self.getTextpv())
        newItem.setProjetpv(self.getPv())
        newItem.reindexObject(idxs=['getDecision', 'getProjetpv'])

        self.plone_utils.addPortalMessage(
            translate('item_duplicated', domain='PloneMeeting', context=self.REQUEST))
        return self.REQUEST.RESPONSE.redirect(newItem.absolute_url())

    MeetingItem.onDuplicate=onDuplicate
    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

#    # cette fonction surgarge showduplicateItemAction dans meetingitem
#    # de facon a donner le droit de dupliquer n'importe quel point au meetingmanager
#    security.declarePublic('showDuplicateItemAction')
#    def showDuplicateItemAction (self):
#        member = self.portal_membership.getAuthenticatedMember()
#        if (member.has_role('MeetingManager')):
#            return True
#        else:
#            tool = self.portal_plonemeeting
#            if tool.getPloneDiskAware() or not tool.userIsAmong('creators'):
#                return False
#            return True
#    MeetingItem.showDuplicateItemAction=showDuplicateItemAction
#    #it'a a monkey patch because it's the only way to have a default method in the schema

    security.declareProtected('Modify portal content', 'onWelcomeNowPerson')
    def onWelcomeNowPerson(self):
        '''Some user (in request.userId) has join the meeting 
           We will record this info, excepted if request["action"] tells us to
           remove it instead (delete).'''
        tool = getToolByName(self, 'portal_plonemeeting')
        if not tool.isManager(self) or not checkPermission(ModifyPortalContent, self):
            raise Unauthorized
        rq = self.REQUEST
        userId = rq['userId']
        actionType = rq.get('actionType')
        if actionType == 'delete':
            present = list(self.getItemPresents())
            present.remove(userId)
            self.setItemPresents(present)
        if actionType == 'do':
            present = list(self.getItemPresents())
            present.append(userId)
            self.setItemPresents(present)

    MeetingItem.onWelcomeNowPerson=onWelcomeNowPerson
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    ### RAPCOLAUCON ###
    security.declarePublic('israpcolaucon')
    def israpcolaucon(self):
        """
        """
        meetingconfig = self.context.portal_plonemeeting.getMeetingConfig(self.context)
        if  meetingconfig.id == 'rapport-col-au-con':
            return True
        else :
            return False
#    MeetingItem.israpcolaucon=israpcolaucon

    security.declarePublic('getLabelForDescription')
    def getLabelForDescription(self):
        """
          If we are in the rapcolaucon meetingConfig, we change the label of the 'description' field
        """
        if self.adapted().israpcolaucon():
            return "Corps du texte"
        else:
            return self.utranslate("meeting_item_description", domain="PloneMeeting", context=self)

    MeetingItem.getLabelForDescription=getLabelForDescription
    #it'a a monkey patch because it's the only way to have a default method in the schema
    ### END RAPCOLAUCON ###



    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('isformation')
    def isformation(self):
        if self.context.getTemplate_flag()=='formation' and (self.context.queryState()=='active' or self.context.queryState()=='itemcreated'):
            return True
        else :
            return False

    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('getTrainingDate')
    def getTrainingDate(self):
        '''Sets training date default value to now'''
        return DateTime()

    MeetingItem.getTrainingDate=getTrainingDate
    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('listDestUsers') 
    def listDestUsers(self):
        '''Lists the users that will be selectable to be in destination (view only) for this
            item.'''
        pgp = self.portal_membership
        res = []
        for user in pgp.listMembers():
            res.append((user.getId(),user.getProperty('fullname')))
        res = sorted(res, key=lambda student: student[1])
        return DisplayList(tuple(res))

    MeetingItem.listDestUsers=listDestUsers
    #it'a a monkey patch because it's the only way to have a default method in the schema

    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('listFormationMod') 
    def listFormationMod(self,displaylist=True):
        res = []
        res.append(('1',self.translate('MeetingAndenne_label_formation_mod1', domain='PloneMeeting').encode('utf-8')))
        res.append(('2',self.translate('MeetingAndenne_label_formation_mod2', domain='PloneMeeting').encode('utf-8')))
        if (displaylist):
            return DisplayList(tuple(res))
        else:
            return tuple(res)

    MeetingItem.listFormationMod=listFormationMod
    #it'a a monkey patch because it's the only way to have a default method in the schema

    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('getLabelForIncludebudget')
    def getLabelForIncludebudget(self):
        """
          If we are in the formation template, we change the label of the 'includebudget' field
        """
        if self.adapted().isformation():
            return "La formation est payante - Je remplis les champs suivants (si la formation est gratuite, il y a lieu de décocher et ne rien remplir ci-dessous)"
        else:
            return self.utranslate("MeetingAndenne_label_IncludeBudget", domain="MeetingAndenne", context=self)

    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('extractBudget')
    def extractBudget(self):
        if (not self.context.budgetRelated):
            return ['','']

        returnValue=['XXXX','YYYY']
        budget_array=self.context.budgetInfos().replace(';',' ').replace('>',' ').replace('&',' ').replace('<',' ').split()
        for element in budget_array:
            price=element.replace('.','').replace(',','.')
            if (self.adapted().isFloat(price)):
                returnValue[0]=element
                break
        for element in budget_array:
            article=element.replace('.','').replace('/','').replace('-','')
            if (self.adapted().isFloat(article) and element.count('/')== 1):
                returnValue[1]=element
                break
        return returnValue

    ### FORMATION : TO BE REMOVED LATER ###
    security.declarePublic('isFloat')
    def isFloat(self,string):
        try:
            float(string)
            return True
        except ValueError:
            return False


#    security.declarePublic('printUserGroup')
#    def printUserGroup(self):
#        '''Lists the Users that are in all groups for printing and reporting'''
#        from Products.Archetypes.utils import DisplayList
#        #member = self.portal_membership.getAuthenticatedMember()
#        member = self.portal_membership.getMemberById(self.Creator())
#        grp_tool = self.acl_users.source_groups
#        res= ""
#        if member:
#         #groups = grp_tool.getGroupsForPrincipal(member)
#         meetingconfig=self.portal_plonemeeting.getMeetingConfig(self)
#         groups=meetingconfig.getMeetingGroups()
#         for group in groups:
#                res=res+"<p><u><b>"+group.id+"</b></u>"
#                grp_obj = grp_tool.getGroupById(group.id)
#                for user in grp_obj.getMemberIds():
#                    if user:
#                      role=''
#                      role2=''
#                      if (self.portal_membership.getMemberById(user).has_role('MeetingManager')):
#                        role="<b> (est MeetingManager)</b>"
#                      if (self.portal_membership.getMemberById(user).has_role('CourrierManager')):
#                        role2="<b> (est CourrierManager)</b>"
#
#                      res=res+'<br>'+self.portal_membership.getMemberById(user).getProperty('fullname')+role+role2
#                res=res+"</p>"
#        return res
#
#    MeetingItem.printUserGroup=printUserGroup
#    #it'a a monkey patch because it's the only way to have a default method in the schema
#
#    security.declarePublic('listAnnexes')
#    def listAnnexes(self,decision=False,toprint=True):
#        if decision :
#            annexes=self.context.getAnnexesDecision()
#        else:
#            annexes=self.context.getAnnexes()
#        res=''
#        nbann=1
#        for annex in annexes:
#            if annex.getToPrint() or toprint:
#                res = res + ' (' + str(nbann) + ')' + annex.Title() + ';'
#                nbann=nbann+1
#        if res != '' :
#            res= 'Annexe(s): '+res
#        return res
#
#    security.declarePublic('printAnnexes')
#    def printAnnexes(self,decision=False,toprint=True):
#        '''Generate annexe in the text'''
#        import os
#        if decision :
#            annexes=self.context.getAnnexesDecision()
#        else:
#            annexes=self.context.getAnnexes()
#        res=''
#
#        for annex in annexes:
#                if annex.getToPrint() or toprint:
#                    filename=annex.dump()
#                    mimetype=annex.getContentType()
#                    dest = annex.getPhysicalPath()[7]
#                    if dest[len(dest)-4:len(dest)-3] == "." :
#                          dest = dest[0:len(dest)-4]
#                    if mimetype == 'application/pdf' :
#                        os.system ("/srv/importfile.sh " + annex.getPhysicalPath()[3] + " " + annex.getPhysicalPath()[6] + " " +"\"" + annex.getPhysicalPath()[7] + "\"" + " " + dest + " " + "\""+filename+"\"")
#                    else :
#                        os.system ("/srv/importfiletopdf.sh " + annex.getPhysicalPath()[3] + " " + annex.getPhysicalPath()[6] + " " +"\"" + annex.getPhysicalPath()[7] + "\"" + " " + dest+ " " + "\""+filename+"\"")
#                    resume = "/srv/www/htdocs/college/" + annex.getPhysicalPath()[3]+ "/"+annex.getPhysicalPath()[6] +"/FD-"+annex.getPhysicalPath()[7]+"/resume.txt"
#                    ofi = open (resume,'r')
#                    res = res + ofi.read()
#        return res


# ------------------------------------------------------------------------------
#UNSUPPORTED_FORMAT_FOR_OCR = 'File "%s" could not be OCR-ized because mime ' \
#    'type "%s" is not a supported input format. Supported input formats ' \
#    'are: %s; %s.'
#DUMP_FILE_ERROR = 'Error occurred while dumping or removing file "%s" on ' \
#    'disk. %s'
#GS_ERROR = 'An error occurred when using Ghostscript to convert "%s". Note ' \
#    'that program "gs" must be in path.'
#TESSERACT_ERROR = 'An error occurred when using Tesseract to OCR-ize file ' \
#    '"%s". Note that program "tesseract" must be in path.'
#
#GS_TIFF_COMMAND = 'gs -q -dNOPAUSE -dBATCH -sDEVICE=tiffg4 ' \
#    '-sOutputFile=%s/%%04d.tif %s -c quit'
#GS_INFO_COMMAND = 'Launching Ghoscript: %s'
#POPPLER_COMMAND = 'pdftoppm -png %s %s'
#POPPLER_INFO_COMMAND = 'Launching Poppler: %s'
#POPPLER_ERROR = 'An error occurred when using Poppler to convert "%s". Note ' \
#    'that program "pdftoppm" must be in path.'
#TESSERACT_COMMAND = 'tesseract %s %s -l %s'
#TESSERACT_INFO_COMMAND = 'Launching Tesseract: %s'
#PDFTOTEXT_COMMAND = 'pdftotext %s %s'
#PDFTOTEXT_INFO_COMMAND = 'Launching pdftotext: %s'
#PDFTOTEXT_ERROR = 'An error occurred while converting a PDF file with ' \
#    'pdftotext.'
#WVTEXT_COMMAND = 'wvText %s %s'
#WVTEXT_INFO_COMMAND = 'Launching wvText: %s'
#WVTEXT_ERROR = 'An error occurred while converting a Word document with wvText.'


# ------------------------------------------------------------------------------
class CustomMeetingFileAndenne(MeetingFile):
    '''Adapter that adapts a meeting File implementing IMeetingFile to the
       interface IMeetingFileCustom.'''
    implements(IMeetingFileCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

#    security.declarePublic('onEdit')
#    def onEdit(self,isCreated):
#        print "passage dans le ON EDIT"
#        self.flaggedForOcr = False
#        self.isOcrized = False
#
#    MeetingFile.onEdit=onEdit
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class
#
#    security.declarePublic('indexExtractedText')
#    def indexExtractedText(self):
#        ''' This method extracts text from the binary content of this object
#            and puts it in the index that corresponds to this method. It does so
#            only if tool.extractTextFromFiles is True.
#
#            If self.needsOcr is True, it does OCR recognition
#            by calling command-line programs Poppler (pdftoppm) and Tesseract
#            (tesseract). Poppler is used for converting a file into
#            images and Tesseract is the OCR engine that converts those images
#            into text. Tesseract needs to know in what p_ocrLanguage the file
#            is written in'''
#
#        if not hasattr( self.aq_base, 'needsOcr' ):
#            return ''
#
#        tool = self.portal_plonemeeting
#        if not tool.getExtractTextFromFiles():
#            return ''
#
#        # Extracts the text from the binary content.
#        extractedText = ''
#        mimeType = self.content_type
#        if self.needsOcr:
#            # This if is added to prevent ocr-isation on the fly (when item is created or edited)
#            # but to allow it when an ocr script is launched during the next night.
#            if( hasattr( self, 'flaggedForOcr' ) and self.flaggedForOcr == True ):
#                if mimeType in self.ocrAllFormatsOk:
#                    try:
#                        fileName = self.dump() # Dumps me on disk first
#                        pngFolder = None
#                        if mimeType in self.ocrFormatsOkButConvertNeeded:
#                            # Poppler will be used to convert the file to
#                            # "png" format. A folder where Poppler will
#                            # generate one png file per PDF page will be created.
#                            pngFolder = os.path.splitext( fileName )[0] + '.folder'
#                            os.mkdir( pngFolder )
#                            cmd = POPPLER_COMMAND % ( fileName, pngFolder + '/file' )
#                            logger.info( POPPLER_INFO_COMMAND % cmd )
#                            os.system( cmd )
#                            pngFiles = ['%s/%s' % ( pngFolder, f ) for f in \
#                                        os.listdir( pngFolder )]
#                            if not pngFiles:
#                                logger.warn( POPPLER_ERROR % ( fileName ) )
#                        else:
#                            pngFiles = [fileName]
#                        pngFiles.sort()
#                        # Launch the OCR engine
#                        for pngFile in pngFiles:
#                            resFile = os.path.splitext( pngFile )[0]
#                            resFilePlusExt = resFile + '.txt'
#                            cmd = TESSERACT_COMMAND % ( pngFile, resFile,
#                                                        self.ocrLanguage)
#                            logger.info( TESSERACT_INFO_COMMAND % cmd )
#                            os.system( cmd )
#                            if not os.path.exists( resFilePlusExt ):
#                                logger.warn( TESSERACT_ERROR % pngFile )
#                            else:
#                                f = file( resFilePlusExt )
#                                extractedText += f.read()
#                                f.close()
#                                os.remove( resFilePlusExt )
#                            os.remove( pngFile )
#                        if pngFolder:
#                            os.removedirs( pngFolder )
#                        os.remove( fileName )
#                    except OSError, oe:
#                        logger.warn( DUMP_FILE_ERROR % ( self.getFilename(), str( oe ) ) )
#                    except IOError, ie:
#                        logger.warn( DUMP_FILE_ERROR % ( self.getFilename(), str( ie ) ) )
#                else:
#                    logger.warn( UNSUPPORTED_FORMAT_FOR_OCR % ( self.getFilename(),
#                        mimeType, self.ocrFormatsOk,
#                        self.ocrFormatsOkButConvertNeeded ) )
#        else:
#            fileName = self.dump() # Dumps me on disk first
#            # Import the content of a not-to-ocr PDF file.
#            resultFileName = os.path.splitext( fileName )[0] + '.txt'
#            decodeNeeded = None
#            if mimeType == 'application/pdf':
#                cmd = PDFTOTEXT_COMMAND % ( fileName, resultFileName )
#                logger.info( PDFTOTEXT_INFO_COMMAND % cmd )
#                os.system( cmd )
#                if not os.path.exists( resultFileName ):
#                    logger.warn( PDFTOTEXT_ERROR )
#            elif mimeType == 'application/msword':
#                cmd = WVTEXT_COMMAND % ( fileName, resultFileName )
#                logger.info( WVTEXT_INFO_COMMAND % cmd )
#                os.system( cmd )
#                decodeNeeded = 'latin-1'
#                if not os.path.exists( resultFileName ):
#                    logger.warn( WVTEXT_ERROR )
#            else:
#                logger.info( 'Unable to index content of "%s"' % self.id )
#            # Return temporary files written on disk and return the result.
#            os.remove( fileName )
#            if os.path.exists( resultFileName ):
#                f = file( resultFileName )
#                if decodeNeeded:
#                    extractedText += f.read().decode( decodeNeeded )
#                else:
#                    extractedText += f.read()
#                f.close()
#                os.remove( resultFileName )
#        return extractedText
#
#    MeetingFile.indexExtractedText=indexExtractedText
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class
#
#    security.declarePublic('annex_print')
#    def annex_print(self):
#        '''Toggles the toPrint switch'''
#        self.setToPrint(not self.getToPrint())
#        return self.REQUEST.RESPONSE.redirect(self.getParentNode().absolute_url() + '/annexes_form')
#
#    MeetingFile.annex_print=annex_print
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class


# ------------------------------------------------------------------------------
class CustomMeetingConfigAndenne(MeetingConfig):
    '''Adapter that adapts a meeting config item implementing IMeetingConfig to the
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

    MeetingConfig.getTopicResults=getTopicResults
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

    MeetingConfig.getQueryColumns=getQueryColumns
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

    MeetingConfig.listMailColumns=listMailColumns
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePublic('searchMailsInCopy')
    def searchMailsInCopy(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
        '''Returns the list of mails for which the user is in copy.'''
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

    MeetingConfig.searchMailsInCopy = searchMailsInCopy
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class


# ------------------------------------------------------------------------------
class CustomToolMeetingAndenne(ToolPloneMeeting):
    '''Adapter that adapts the PloneMeeting tool implementing IToolPloneMeeting
       to the interface IToolPloneMeetingCustom.'''
    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, tool):
        self.context = tool

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


    security.declarePublic('hasSearchTypeFor')
    def hasSearchTypeFor(self, meetingType):
        '''
            Returns True if there is a portal_type to be used in a search local to the given meeting type.
        '''
        return meetingType in SEARCH_TYPES.keys()

#    security.declarePublic('getSearchTypeFor')
#    def getSearchTypeFor(self, meetingType):
#        '''
#            Returns the portal_type to be used in a search local to the given meeting type.
#        '''
#        return SEARCH_TYPES[meetingType]
#
#    security.declarePublic('getMailTypesForSearch')
#    def getMailTypesForSearch(self):
#        '''
#            Returns the ids and titles of alll the available mail types for
#            search purposes.
#        '''
#        return MAIL_TYPES.items()
#
#    security.declarePublic('listDestUsers')
#    def listDestUsers(self):
#        '''
#            Lists the users that will be selectable to be in destination (view only) for this item.
#        '''
#        pgp = getToolByName(self.context, 'portal_membership')
#        res = []
#        for user in pgp.listMembers():
#            if user.getProperty('listed'):
#                res.append( (user.getId(), user.getProperty('fullname')) )
#        res = sorted( res, key=lambda student: student[1] )
#        return res


# ------------------------------------------------------------------------------
class MeetingCollegeAndenneWorkflowActions(MeetingWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingCollegeWorkflowActions'''

    implements(IMeetingCollegeAndenneWorkflowActions)
    security = ClassSecurityInfo()

    def doDecide(self, stateChange):
        '''We pass every item that is 'presented' in the 'itemfrozen'
           state.  It is the case for late items. Moreover, if
           MeetingConfig.initItemDecisionIfEmptyOnDecide is True, we
           initialize the decision field with content of Title+Description
           if decision field is empty.'''
        tool = getToolByName(self.context, 'portal_plonemeeting')
        cfg = tool.getMeetingConfig(self.context)
        initializeDecision = cfg.getInitItemDecisionIfEmptyOnDecide()
        for item in self.context.getAllItems(ordered=True):
            if initializeDecision:
                # If deliberation (motivation+decision) is empty,
                # initialize it the decision field
                item._initDecisionFieldIfEmpty()


# ------------------------------------------------------------------------------
class MeetingCollegeAndenneWorkflowConditions(MeetingWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
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
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayClose')
    def mayClose(self):
        res = False
        # The user just needs the "Review portal content" permission on the
        # object to close it.
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res


# ------------------------------------------------------------------------------
class MeetingItemCollegeAndenneWorkflowActions(MeetingItemWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemAndenneWorkflowActions'''

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
            self.context.setPv(self.context.getProjetpv())
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

    security.declarePublic('doRefuse_and_close')
    def doRefuse_and_close(self, stateChange):
        pass


# ------------------------------------------------------------------------------
class MeetingItemCollegeAndenneWorkflowConditions(MeetingItemWorkflowConditions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemAndenneWorkflowConditions'''

    implements(IMeetingItemCollegeAndenneWorkflowConditions)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item # Implements IMeetingItem

    security.declarePublic('mayDecide')
    def mayDecide(self):
        '''We may decide an item if the linked meeting is in relevant state'''
        res = False
        meeting = self.context.getMeeting()
        if checkPermission(ReviewPortalContent, self.context) and \
           meeting and meeting.adapted().isDecided():
            res = True
        return res

    security.declarePublic('mayPrevalidate')
    def mayPrevalidate(self):
        '''We'll see who can prevalidate later'''
        pass

#    security.declarePublic('mayValidate')
#    def mayValidate(self):
#        '''We'll see what to do with Personnel category'''
#        from Products.PloneMeeting.MeetingItem import MeetingItemWorkflowConditions
#        res=MeetingItemWorkflowConditions.mayValidate(self)
#        #if res:
#        #  user = self.context.Communesportal_membership.getAuthenticatedMember()
#        #  if self.context.getCategory() == "66-personnel" and (not user.has_role('MeetingManager')):
#        #          res = False
#        return res


# ------------------------------------------------------------------------------
InitializeClass(CustomMeetingAndenne)
InitializeClass(CustomMeetingItemAndenne)
InitializeClass(CustomMeetingFileAndenne)
InitializeClass(CustomMeetingConfigAndenne)
InitializeClass(CustomToolMeetingAndenne)
InitializeClass(MeetingCollegeAndenneWorkflowActions)
InitializeClass(MeetingCollegeAndenneWorkflowConditions)
InitializeClass(MeetingItemCollegeAndenneWorkflowActions)
InitializeClass(MeetingItemCollegeAndenneWorkflowConditions)
# ------------------------------------------------------------------------------
