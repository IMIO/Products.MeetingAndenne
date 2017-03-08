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
from Products.CMFCore.permissions import ReviewPortalContent
from Products.CMFCore.utils import getToolByName
from plone import api
from imio.helpers.xhtml import xhtmlContentIsEmpty
from Products.PloneMeeting.config import ITEM_NO_PREFERRED_MEETING_VALUE, \
     TOPIC_SEARCH_SCRIPT, TOPIC_TYPE
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
#from Products.MeetingAndenne.SearcherAndenne import SearcherAndenne
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
class CustomMeetingAndenne(Meeting):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

#    security.declarePublic('getAttendeesForPrinting')
#    def getAttendeesForPrinting(self, meeting=False):
#        '''Check doc in interfaces.py.'''
#        attendees = self.getAttendees(theObjects=True)
#        absents = self.getAbsents(theObjects=True)
#        excused = self.getExcused(theObjects=True)
#        attendeesIds = list(self.getAttendees())
#        absentsIds = list(self.getAbsents())
#        absentsItemIds = []
#        presentsItemIds = list(self.getAttendees())
#        excusedIds = list(self.getExcused())
#
#        lastduty = ""
#        morethanone = 0
#        toprint = ""
#        toprint2 = ""
#        todelete = False
#        toStrike = False
#        morethan = False
#
#        assemblyMembers = self.listAllAssemblyMembers()
#        potentialAssemblyMembers = assemblyMembers
#        everyone = attendeesIds + absentsIds + excusedIds
#        meetingDate = self.getDate()
#
#        for attendeeId in potentialAssemblyMembers:
#            attendee = getattr(self.portal_plonemeeting.getMeetingConfig(self).meetingusers, attendeeId)
#            currentDuty = attendee.getDuty()
#            currentTitle = attendee.Title()
#            currentId = attendee.getId()
#            currentStartdate=attendee.getStart_date_function()
#            currentEnddate=attendee.getEnd_date_function()
#            enfonction='ok'
#            enfonction2='ok'
#            if not currentStartdate:
#                enfonction='ok'
#            else:
#                if currentStartdate > meetingDate:
#                    enfonction='ko'
#            if not currentEnddate:
#                enfonction2='ok'
#            else:
#                if currentEnddate < meetingDate:
#                    enfonction2='ko'
#            if enfonction=='ok' and enfonction2=='ok':
#                if lastduty == "":
#                    lastduty=currentDuty
#                    toprint2 = "<p>"
#
#            if lastduty != currentDuty:
#                if morethan:
#                    toprint2 = toprint2 + "MM. "+toprint + "%ss</p><p>" % lastduty
#                else:
#                    if todelete == False:
#                        if tostrike == True:
#                            toprint2 = toprint2 + "<strike>M. "+toprint + "%s</strike></p><p>" % lastduty
#                        else:
#                            toprint2 = toprint2 + "M. "+toprint + "%s</p><p>" % lastduty
#                toprint=""
#                morethanone = 0
#                morethan = False
#                lastduty = currentDuty
#
#            if lastduty == currentDuty:
#                morethanone = morethanone + 1
#                if morethanone > 1:
#                    morethan = True
#                if (currentId not in attendeesIds and currentId not in presentsItemIds) or currentId in absentsItemIds:
#                    if currentDuty == "Echevin" or currentDuty.count("sociale") == 1 or currentDuty.count("Bourgmestre") == 1 or currentDuty == "Membre":
#                        toprint = toprint + "<strike>%s</strike>, " % currentTitle
#                        tostrike = True
#                        todelete = False
#                    else:
#                        todelete = True
#                else:
#                    toprint = toprint + "%s, " % currentTitle
#                    tostrike = False
#                    todelete = False
#                    lastduty = currentDuty
#
#        if toprint != "":
#            return toprint2+"M. "+toprint+ "%s</p>" % lastduty
#        else:
#            return toprint2+"</p>"
#
#    Meeting.getAttendeesForPrinting=getAttendeesForPrinting
#    #it'a a monkey patch because it's the only way to change the behaviour of the Meeting class
#
#    security.declarePublic('getItemAbsentForPrinting')
#    def getItemAbsentForPrinting(self):
#        absentsItemIds=list(self.getItemAbsents())
#        lastduty = ""
#        morethanone = 0
#        toprint = ""
#        toprint2 = ""
#        morethan = False
#        count = 0
#
#        for attendeeId in absentsItemIds:
#            count = count +1
#            attendee = getattr(self.portal_plonemeeting.getMeetingConfig(self).meetingusers, attendeeId)
#            currentDuty = attendee.getDuty()
#            currentTitle = attendee.Title()
#            currrentId = attendee.getId()
#
#            if lastduty == "":
#                lastduty=currentDuty
#                toprint2 = "["
#
#            if lastduty != currentDuty:
#                #print duty
#                if morethan:
#                    toprint2 = toprint2 + "MM. "+toprint + "%ss " % lastduty
#                else:
#                    toprint2 = toprint2 + "M. "+toprint + "%s " % lastduty
#                toprint=""
#                morethanone = 0
#                morethan = False
#                lastduty = currentDuty
#
#            if lastduty == currentDuty:
#                morethanone = morethanone + 1
#                if morethanone > 1:
#                    morethan = True
#                toprint = toprint + "%s, " % currentTitle
#                lastduty = currentDuty
#
#        if morethan:
#            toprint2 = toprint2 + "MM. "+ toprint + "%ss" % lastduty
#        else:
#            toprint2 = toprint2 + "M. "+ toprint + "%s" % lastduty
#        if count > 1:
#            toprint2 = toprint2 +" sont absents pour l'examen de ce point]"
#        else:
#            toprint2 = toprint2 + "est absent pour l'examen de ce point]"
#        return toprint2
#
#    security.declarePublic('getSignatoriesForPrinting')
#    def getSignatoriesForPrinting(self, pos=0, level=0, pv=False, meeting=False):
#        '''Returns the attendees in html mode for printing'''
#        attendees = self.getAttendees(theObjects=True)
#        absents = self.getAbsents(theObjects=True)
#        excused = self.getExcused(theObjects=True)
#        attendeesIds = list(self.getAttendees())
#        absentsIds = list(self.getAbsents())
#        absentsItemIds = []
#        excusedIds = list(self.getExcused())
#
#        lastduty = ""
#        morethanone = 0
#        toprint = ""
#        toprint2 = ""
#        todelete = False
#        toStrike = False
#        morethan = False
#
#        if pv==True:
#            assemblyMembers = self.listAssemblyMembers()
#            potentialAssemblyMembers = assemblyMembers
#            i=0
#            for attendeeId in potentialAssemblyMembers:
#                attendee = getattr(self.portal_plonemeeting.getMeetingConfig(self).meetingusers, attendeeId)
#                currentDuty = attendee.getDuty()
#                currentTitle = attendee.Title()
#                currentId = attendee.getId()
#                if currentId in attendeesIds and currentId not in absentsItemIds:
#                    if i==0:
#                        firstDuty = "Président" 
#                        firstTitle= currentTitle
#                    else:
#                        lastDuty=currentDuty
#                        lastTitle = currentTitle
#                    i=i+1
#
#        duty=self.getSignatories(theObjects=True)[pos].getDuty()
#        title=self.getSignatories(theObjects=True)[pos].Title()
#
#        if pos==0:
#            if pv==False:
#                if duty=="Bourgmestre-Président": 
#                    duty="Bourgmestre"
#                else:
#                    duty="Bourgmestre f.f."
#            else:
#                duty=firstDuty
#                title="(s) "+firstTitle
#
#        if pos==1:
#            if pv==True:
#                title="(s) "+lastTitle
#                duty=lastDuty
#            if duty!="Directeur général":  
#                duty="Directeur g&eacute;n&eacute;ral f.f."
#
#        if level==0:
#            return "Le "+duty+","
#        else:
#            return title+"."
#
#    Meeting.getSignatoriesForPrinting=getSignatoriesForPrinting
#    #it'a a monkey patch because it's the only way to change the behaviour of the Meeting class
#
#    security.declarePublic('getDisplayableName')
#    def getDisplayableName(self, short=False, withHour=True, likeTitle=False):
#        '''Check doc in interfaces.py.'''
#        meeting = self.getSelf()
#        if likeTitle:
#            res = meeting.Title()
#        else:
#            if withHour: hour = ' (%H:%M)'
#            else:        hour = ''
#            if short:
#                res = meeting.getDate().strftime('%d/%m/%Y' + hour)
#            else:
#                res = meeting.portal_plonemeeting.getFormattedDate(
#                    meeting.getDate()) + meeting.getDate().strftime(hour)
#        return res
#
#    Meeting.getDisplayableName=getDisplayableName
#    #it'a a monkey patch because it's the only way to change the behaviour of the Meeting class
#
#    security.declarePublic('getPrintableItems')
#    def getPrintableItems(self, itemUids, late=False, ignore_review_states=[],
#                          privacy='*', oralQuestion='both', toDiscuss='both', categories=[],
#                          excludedCategories=[], firstNumber=1, renumber=False):
#        '''Returns a list of items.
#           An extra list of review states to ignore can be defined.
#           A privacy can also be given, and the fact that the item is an
#           oralQuestion or not (or both). Idem with toDiscuss.
#           Some specific categories can be given or some categories to exchude.
#           These 2 parameters are exclusive.  If renumber is True, a list of tuple
#           will be return with first element the number and second element, the item.
#           In this case, the firstNumber value can be used.'''
#        # We just filter ignore_review_states here and privacy and call
#        # getItemsInOrder(uids), passing the correct uids and removing empty
#        # uids.
#        # privacy can be '*' or 'public' or 'secret'
#        # oralQuestion can be 'both' or False or True
#        # toDiscuss can be 'both' or 'False' or 'True'
#        for elt in itemUids:
#            if elt == '': itemUids.remove(elt)
#        #no filtering, return the items ordered
#        if not categories and not ignore_review_states and privacy == '*' and oralQuestion == 'both' and toDiscuss == 'both':
#            return self.context.getItemsInOrder(late=late, uids=itemUids)
#        # Either, we will have to filter the state here and check privacy
#        filteredItemUids = []
#        uid_catalog = self.context.uid_catalog
#        for itemUid in itemUids:
#            obj = uid_catalog(UID=itemUid)[0].getObject()
#            if obj.queryState() in ignore_review_states:
#                continue
#            elif not (privacy == '*' or obj.getPrivacy() == privacy):
#                continue
#            elif not (oralQuestion == 'both' or obj.getOralQuestion() == oralQuestion):
#                continue
#            elif not (toDiscuss == 'both' or obj.getToDiscuss() == toDiscuss):
#                continue
#            elif categories and not obj.getCategory() in categories:
#                continue
#            elif excludedCategories and obj.getCategory() in excludedCategories:
#                continue
#            filteredItemUids.append(itemUid)
#        #in case we do not have anything, we return an empty list
#        if not filteredItemUids:
#            return []
#        else:
#            items = self.context.getItemsInOrder(late=late, uids=filteredItemUids)
#            if renumber:
#                #return a list of tuple with first element the number and second
#                #element the item itself
#                i = firstNumber
#                res = []
#                for item in items:
#                    res.append((i, item))
#                    i = i + 1
#                items = res
#            return items
#
#    security.declarePublic('getPrintableItemsByNumCategory')
#    def getPrintableItemsByNumCategory(self, late=False, uids=[],
#        catstoexclude=[], exclude=True, allItems=False):
#        '''Returns a list of items ordered by category number. If there are many
#           items by category, there is always only one category, even if the
#           user have chosen a different order. If exclude=True , catstoexclude
#           represents the category number that we don't want to print and if
#           exclude=False, catsexclude represents the category number that we
#           only want to print. This is useful when we want for exemple to
#           exclude a personnal category from the meeting an realize a separate
#           meeeting for this personal category. If allItems=True, we return
#           late items AND items in order.'''
#        def getPrintableNumCategory(current_cat):
#            '''Method used here above.'''
#            current_cat_id=current_cat.getId ()
#            current_cat_name=current_cat.Title()
#            current_cat_name=current_cat_name[0:2]
#            try :
#                catNum=int(current_cat_name)
#            except ValueError :
#                current_cat_name=current_cat_name[0:1]
#                try :
#                    catNum=int(current_cat_name)
#                except ValueError :
#                    catNum=current_cat_id
#            return catNum
#
#        itemsGetter = self.context.getItems
#        if late:
#            itemsGetter = self.context.getLateItems
#        items = itemsGetter()
#        if allItems:
#            items = self.context.getItems() + self.context.getLateItems()
#        # res contains all items by category, the key of res is the category
#        # number. Pay attention that the category number is obtain by extracting
#        # the 2 first caracters of the categoryname, thus the categoryname must
#        # be for exemple ' 2.travaux' or '10.Urbanisme. If not, the catnum takes
#        # the value of the id + 1000 to be sure to place those categories at the
#        # end.
#        res = {}
#        # First, we create the category and for each category, we create a
#        # dictionary that must contain the list of item in in res[catnum][1]
#        for item in items:
#            if uids :
#                if (item.UID() in uids) :
#                    inuid="ok"
#                else :
#                    inuid="ko"
#            else:
#                inuid="ok"
#            if (inuid=="ok") :
#                current_cat = item.getCategory(theObject=True)
#                catNum=getPrintableNumCategory(current_cat)
#                if res.has_key(catNum) :
#                    res[catNum][1][item.getItemNumber()] = item
#                else :
#                    res[catNum]={}
#                    #first value of the list is the category object
#                    res[catNum][0]=item.getCategory(True)
#                    #second value of the list is a list of items
#                    res[catNum][1]={}
#                    res[catNum][1][item.getItemNumber()] = item
#
#        # Now we must sort the res dictionary with the key (containing catnum)
#        # and copy it in the returned array.
#        reskey=res.keys()
#        reskey.sort()
#        ressort = []
#        for i in reskey:
#            if catstoexclude :
#                if (i in catstoexclude) :
#                    if (exclude==False) :
#                        guard=True
#                    else:
#                        guard=False
#                else:
#                    if (exclude==False) :
#                        guard=False
#                    else:
#                        guard=True
#            else :
#                guard=True
#
#            if (guard==True) :
#                k=0
#                ressorti=[]
#                ressorti.append(res[i][0])
#                resitemkey=res[i][1].keys()
#                resitemkey.sort()
#                ressorti1=[]
#                for j in resitemkey:
#                    k=k+1
#                    ressorti1.append([res[i][1][j],k])
#                ressorti.append(ressorti1)
#                ressort.append(ressorti)
#        return ressort
#
#    security.declarePublic('listAllAssemblyMembers')
#    def listAllAssemblyMembers(self):
#        '''Returns the active MeetingUsers having usage "assemblyMember".'''
#        meetingConfig = self.portal_plonemeeting.getMeetingConfig(self)
#        res = ((u.id, u.Title()) for u in meetingConfig.adapted().getAllMeetingUsers())
#        return DisplayList(res)
#
#    Meeting.listAllAssemblyMembers=listAllAssemblyMembers
#    #it'a a monkey patch because it's the only way to change the behaviour of the Meeting class
#
#    security.declarePublic('meeting_decideseveralitems')
#    def meeting_decideseveralitems(self, uids=None, toState='accept'):
#        '''Apply a decision to several MeetingItems at the same time in a Meeting.'''
#        if not uids:
#            msg = self.utranslate('no_selected_items', domain='PloneMeeting')
#            self.plone_utils.addPortalMessage(msg)
#        elif toState=='accept':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                if obj.queryState() in ('itemfrozen'):
#                    self.portal_workflow.doActionFor(obj, 'accept')
#        elif toState=='accept_but_modified':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                if obj.queryState() in ('itemfrozen'):
#                    self.portal_workflow.doActionFor(obj, 'accept_but_modify')
#        elif toState=='refuse':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                if obj.queryState() in ('itemfrozen'):
#                    self.portal_workflow.doActionFor(obj, 'refuse')
#        elif toState=='delay':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                if obj.queryState() in ('itemfrozen'):
#                    self.portal_workflow.doActionFor(obj, 'delay')
#        elif toState=='back':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                if obj.queryState() in ('accepted','refused','delayed','accepted_but_modified','pre_accept'):
#                    self.portal_workflow.doActionFor(obj, 'backToItemFrozen')
#        elif toState=='close':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                state = obj.queryState()
#                if state in ('accepted'):
#                    self.portal_workflow.doActionFor(obj, 'accept_and_close')
#                elif state in ('accepted_but_modified'):
#                    self.portal_workflow.doActionFor(obj, 'accept_but_modify_and_close')
#                elif state in ('delayed'):
#                    self.portal_workflow.doActionFor(obj, 'delay_and_close')
#                elif state in ('refused'):
#                    self.portal_workflow.doActionFor(obj, 'refuse_and_close')
#        elif toState=='reopen':
#            for uid in uids.split(',')[:-1]:
#                obj = self.uid_catalog.searchResults(UID=uid)[0].getObject()
#                state = obj.queryState()
#                if state in ('accepted_and_closed'):
#                    self.portal_workflow.doActionFor(obj, 'backToAccepted')
#                elif state in ('accepted_but_modified_and_closed'):
#                    self.portal_workflow.doActionFor(obj, 'backToAcceptedButModified')
#                elif state in ('delayed_and_closed'):
#                    self.portal_workflow.doActionFor(obj, 'backToDelayed')
#                elif state in ('refused_and_closed'):
#                    self.portal_workflow.doActionFor(obj, 'backToRefused')
#
#        return self.portal_plonemeeting.gotoReferer()
#
#    Meeting.meeting_decideseveralitems=meeting_decideseveralitems
#    #it'a a monkey patch because it's the only way to change the behaviour of the Meeting class
#
#    security.declarePublic('getJsItemUids')
#    def getJsItemUids(self):
#        '''Returns Javascript code for initializing a Javascript variable with
#           all item UIDs.'''
#        res = ''
#        user = self.portal_membership.getAuthenticatedMember()
#        if (user.has_role('MeetingManager')):
#         for uid in self.getRawItems():
#            res += 'itemUids["%s"] = true;\n' % uid
#         for uid in self.getRawLateItems():
#            res += 'itemUids["%s"] = true;\n' % uid
#        else:
#         res=''
#         for item in self.getItems():
#            if user.has_permission('View', item):
#               res += 'itemUids["%s"] = true;\n' % item.UID()
#         for item in self.getLateItems():
#            if user.has_permission('View', item):
#              res += 'itemUids["%s"] = true;\n' % item.UID()
#        return res
#
#    Meeting.getJsItemUids=getJsItemUids
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class


# ------------------------------------------------------------------------------
class CustomMeetingItemAndenne(MeetingItem):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    ###### Begin Overrides MeetingCommunes MeetingItemCustom adapter ###########################

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

#    ###### End Overrides MeetingCommunes MeetingItemCustom adapter #############################

#    security.declarePublic('getExtraFieldsToCopyWhenCloning')
#    def getExtraFieldsToCopyWhenCloning(self):
#        '''Lists the fields to keep when cloning an item'''
#        return ['formation_desc', 'formation_compte', 'template_flag']
#
#    security.declarePublic('showclosewritepvAction')
#    def showclosewritepvAction(self):
#        currentState = self.context.queryState()
#        member = self.context.portal_membership.getAuthenticatedMember()
#        if (member.has_role('MeetingManager') and self.context.getTowritepv()==True and currentState in ('accepted', 'accepted_but_modified','delayed','pre_accepted','refused')):
#            return True
#        else:
#            return False
#
#    security.declarePublic('showopenwritepvAction')
#    def showopenwritepvAction(self):
#        currentState = self.context.queryState()
#        member = self.context.portal_membership.getAuthenticatedMember()
#        if (member.has_role('MeetingManager') and self.context.getTowritepv()==False and currentState in ('accepted', 'accepted_but_modified','delayed','pre_accepted','refused')):
#            return True
#        else:
#            return False
#
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
#    security.declarePublic('updateMeetingItem')
#    def updateMeetingItem(self):
#        """
#           Update a MeetingItem object following a copygroups on-the-fly modification.
#        """
#        self.updateLocalRoles()
#        self.adapted().onEdit(isCreated=False)
#        self.reindexObject()
#
#    MeetingItem.updateMeetingItem=updateMeetingItem
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class
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
#    security.declarePublic('getPrintableCopyTo')
#    def getPrintableCopyTo(self):
#        """
#           For template only : get the copy group
#        """
#        groupsCopyto = self.context.getCopyGroups()
#        groupstr=''
#        if groupsCopyto:
#            for group in groupsCopyto:
#                ploneGroup = self.context.portal_groups.getGroupById(group)
#                # If the corresponding Plone group does not exist anymore,
#                # recreate it.
#                groupstr=groupstr + (ploneGroup.getProperty('title')).split('(')[0] + ','
#        if groupstr != '':
#            return 'Copie(s): ' + groupstr[0:-1]
#        else:
#            return ''
#
#    security.declarePublic('OnPaste')
#    def OnPaste(self):
#        self.context.at_post_create_script()
#
#    security.declarePublic('getPrintableNumCategory')
#    def getPrintableNumCategory(self):
#        current_cat = self.context.getCategory(theObject=True)
#        current_cat_id =current_cat.getId()
#        current_cat_name= current_cat.Title()
#        current_cat_name=current_cat_name[0:2]
#        try:
#            catNum=int(current_cat_name)
#        except ValueError:
#            current_cat_name=current_cat_name[0:1]
#            try:
#                catNum=int(current_cat_name)
#            except ValueError:
#                catNum=current_cat_id
#        return catNum
#
#    security.declarePublic('getPrintableTitleCategory')
#    def getPrintableTitleCategory(self):
#        '''return the name of the category without the first 3 caracteres representing the num'''
#        current_cat = self.context.getCategory(theObject=True)
#        current_cat_name= current_cat.Title()
#        current_cat_name=current_cat_name[3:]
#        return current_cat_name
#
#    security.declarePublic('titleProposingGroup')
#    def titleProposingGroup(self):
#        '''Return the MeetingGroup Title that may propose this item.'''
#        vocab=self.context.Vocabulary('proposingGroup')
#        value=self.context.displayValue(vocab[0],self.context.getProposingGroup())
#        return value
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
#
#    security.declarePublic('getcurrentdate')
#    def getcurrentdate(self):
#        from  DateTime import now
#        return now().strftime("%d/%m/%Y")
#
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

    MeetingItem.getDocReference=getDocReference
    #it'a a monkey patch because it's the only way to have a default method in the schema

    security.declarePublic('listUserGroup')
    def listUserGroup(self):
        '''Lists the Users that are associated to the proposing group(s) of the authenticated user.'''
        userCreatorGroups = self.portal_plonemeeting.getGroupsForUser(suffix="creators", zope=True)

        res = set()
        for group in userCreatorGroups:
            for user in group.getMemberIds():
                res.add( (user, self.portal_membership.getMemberById(user).getProperty('fullname')) )

        return DisplayList( tuple(res) )

    MeetingItem.listUserGroup=listUserGroup
    #it'a a monkey patch because it's the only way to have a default method in the schema


#
#    def listItemPresents(self):
#        '''Returns the list of attendees selectable as presents.'''
#        res = []
#        if self.getMeeting():
#            meeting = self.getMeeting()
#            # Get IDs of attendees
#            meetingAttendees = meeting.getAttendees(False, includeDeleted = True)
#            meetingConfig = self.portal_plonemeeting.getMeetingConfig(self)
#            for u in meetingConfig.getActiveMeetingUsers():
#                if u.id not in meetingAttendees:
#                    res.append( (u.id, u.Title()) )
#        return DisplayList( tuple(res) )
#
#    MeetingItem.listItemPresents=listItemPresents
#    # it'a a monkey patch
#
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
#    security.declarePublic('getAttendeesForPrinting')
#    def getAttendeesForPrinting(self):
#        '''Get the attendees list to print in templates.'''
#        return self.getMeeting().getAttendeesForPrinting()
#
#    MeetingItem.getAttendeesForPrinting=getAttendeesForPrinting
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class
#
#    security.declarePublic('getSignatoriesForPrinting')
#    def getSignatoriesForPrinting(self, pos=0, level=0, pv=False):
#        '''Returns the signatories in html mode for printing'''
#        return self.getMeeting().getSignatoriesForPrinting(pos=pos, level=level, pv=pv)
#
#    MeetingItem.getSignatoriesForPrinting=getSignatoriesForPrinting
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class
#
#    security.declarePublic('onDuplicate')
#    def onDuplicate(self):
#        '''This method is triggered when the users clicks on
#           "duplicate item".'''
#        user = self.portal_membership.getAuthenticatedMember()
#        newItem = self.clone(newOwnerId=user.id)
#        newItem.setTreatUser(user.id)
#        newItem.itemPresents = ()
#        newItem.itemSignatories = ()
#        newItem.itemAbsents = ()
#
#        #copy the content of decision in Projetpv and Decision for later use
#        if (user.has_permission('MeetingAndenne: Read pv', self)):
#            pv=self.getPv()
#            textpv=self.getTextpv()
#
#        wf_def = self.portal_workflow.getWorkflowsFor(newItem)[0]
#        wf_id= wf_def.getId()
#        wf_state = {
#                 'action': None,
#                 'actor': None,
#                 'comments': "Setting state to itemcreated",
#                 'review_state': "itemcreated"
#                 }
#        self.portal_workflow.setStatusOf(wf_id, newItem, wf_state)
#        if (user.has_permission('MeetingAndenne: Read pv', self) and user.has_permission('Modify portal content', newItem)):
#            newItem.setDecision(textpv)
#            newItem.setProjetpv(pv)
#
#        newItem.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
#        self.plone_utils.addPortalMessage(
#            self.utranslate('item_duplicated', domain='PloneMeeting'))
#        return self.REQUEST.RESPONSE.redirect(newItem.absolute_url())
#
#    MeetingItem.onDuplicate=onDuplicate
#    #it'a a monkey patch because it's the only way to have a default method in the schema
#
#    security.declarePublic('listAssociatedGroups')
#    def listAssociatedGroups(self):
#        '''Lists the groups that are associated to the proposing group(s) to
#           propose this item.  Return groups that have at least one creator...'''
#        res = []
#        tool = self.portal_plonemeeting
#        for group in tool.getActiveGroups(notEmptySuffix="creators"):
#            res.append( (group.id, group.Title()) )
#        res=sorted(res, key=lambda student: student[1])
#        return DisplayList( tuple(res) )
#
#    MeetingItem.listAssociatedGroups=listAssociatedGroups
#    #it'a a monkey patch because it's the only way to have a default method in the schema
#
#
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
#
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


    ### RAPCOLAUCON ###
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

#    security.declarePublic('getUserofAction')
#    def getUserofAction(self):
#            '''Returns the user of the last validate action that
#               was performed on object p_obj.'''
#            # Get the last validation date of the item
#            res = self.context.Creator()
#            objectHistory = self.context.workflow_history
#            if objectHistory:
#                objectHistory = objectHistory.values()[0] # We suppose here that the
#                # object is governed by only one workflow.
#                for step in objectHistory:
#                    if (step['action'] == 'validate'):
#                        res = step['actor']
#            return res
#
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
#    security.declarePublic('getUsersofGroup')
#    def getUsersofGroup(self,member):
#        '''Lists the Users that are associated to the proposing group(s) of the m_ user.'''
#        grp_tool = self.context.acl_users.source_groups
#        groups = grp_tool.getGroupsForPrincipal(member)
#        groups2 = []
#        for group in groups:
#            i = []
#            i=group.split('_')
#            if i[1] == 'observers':
#                g=i[0]+'_observers'
#                groups2.append(g)
#
#        res = []
#        for group in groups2:
#            grp_obj = grp_tool.getGroupById(group)
#            for user in grp_obj.getMemberIds():
#                '''if ( (user,self.portal_membership.getMemberById(user).getProperty('fullname')) in res ) == False:'''
#                res.append(user)
#        return res
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

#    security.declarePublic('getAllMeetingUsers')
#    def getAllMeetingUsers(self, usages=('assemblyMember',)):
#        '''Returns the active MeetingUsers having at least one usage among
#        p_usage.'''
#        brains = self.portal_catalog(portal_type='MeetingUser',getConfigId=self.id, indexUsages=' OR '.join(usages), sort_on='getObjPositionInParent')
#        return [b.getObject() for b in brains]
#
#    MeetingConfig.getAllMeetingUsers=getAllMeetingUsers
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#    security.declarePrivate('updatePortalTypes')
#    def updatePortalTypes(self):
#        '''Inhibits the reupdating of the portal_types linked to this meeting config.'''
#        pass
#
#    MeetingConfig.updatePortalTypes=updatePortalTypes
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#    security.declarePublic('getTopicResults')
#    def getTopicResults(self, topic, isFake):
#        '''This method computes results of p_topic. If p_topic is a fake one
#           (p_isFake is True), it means that some information in the request
#           will allow to perform a direct query in portal_catalog (the user
#           triggered an advanced search).'''
#        rq = self.REQUEST
#        # How must we sort the result?
#        sortKey = rq.get('sortKey', None)
#        sortOrder = 'reverse'
#        if sortKey and (rq.get('sortOrder', 'asc') == 'asc'):
#            sortOrder = None
#        # Is there a filter defined?
#        filterKey = rq.get('filterKey', '')
#        filterValue = rq.get('filterValue', '').decode('utf-8')
#        if not isFake:
#            # Execute the query corresponding to the topic.
#            if not sortKey:
#                sortCriterion = topic.getSortCriterion()
#                if sortCriterion: sortKey = sortCriterion.Field()
#                else: sortKey = 'created'
#            methodId = topic.getProperty(TOPIC_SEARCH_SCRIPT, None)
#            objectType = topic.getProperty(TOPIC_TYPE, 'Unknown')
#            batchSize = self.REQUEST.get('MaxShownFound') or \
#                        self.getParentNode().getMaxShownFound(objectType)
#            if methodId:
#                # Topic params are not sufficient, use a specific method.
#                # keep topics defined paramaters
#                kwargs={}
#                for criterion in topic.listSearchCriteria():
#                    # Only take criterion with a defined value into account
#                    criterionValue = criterion.value
#                    if criterionValue:
#                        kwargs[str(criterion.field)] = criterionValue
#                brains = getattr(self, methodId)(sortKey, sortOrder,
#                                                 filterKey, filterValue, **kwargs)
#            else:
#                # Execute the topic, but decide ourselves for sorting and
#                # filtering.
#                params = topic.buildQuery()
#                params['sort_on'] = sortKey
#                params['sort_order'] = sortOrder
#                if filterKey:
#                    params[filterKey] = Keywords(filterValue).get()
#                brains = self.portal_catalog(**params)
#            res = self.getParentNode().batchAdvancedSearch(
#                brains, topic, rq, batch_size=batchSize)
#        else:
#            # This is an advanced search. Use the Searcher.
#            searchedType = topic.getProperty('meeting_topic_type', 'MeetingFile')
#            return SearcherAndenne(self, searchedType, sortKey, sortOrder,
#                                   filterKey, filterValue).run()
#        return res
#
#    MeetingConfig.getTopicResults=getTopicResults
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#
#    security.declarePublic('getQueryColumns')
#    def getQueryColumns(self, metaType):
#        '''What columns must we show when displaying results of a query for
#           objects of p_metaType ?'''
#        res = ('title',)
#        if metaType == 'MeetingItem':
#            res += tuple(self.getUserParam('itemColumns'))
#        elif metaType == 'Meeting':
#            res += tuple(self.getUserParam('meetingColumns'))
#        elif metaType == 'CourrierFile':
#            res += tuple(self.listMailColumns())
#        else:
#            res = ('title','creationDate')
#        return res
#
#    MeetingConfig.getQueryColumns=getQueryColumns
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#
#    security.declarePrivate('listMailColumns')
#    def listMailColumns(self):
#        d = 'MeetingAndenne'
#        u = self.utranslate
#        res = [ ("creationDate", u('pm_creation_date', domain='PloneMeeting')),
#                ("refCourrier", u('MeetingAndenne_label_refCourrier', domain=d)),
#                ("destOrigin", u('MeetingAndenne_label_destOrigin', domain=d)),
#                ("destUsers", u('MeetingAndenne_label_destUsers', domain=d)),
#                ("actions", u("heading_actions", domain='plone')),
#        ]
#        return DisplayList(tuple(res))
#
#    MeetingConfig.listMailColumns=listMailColumns
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#
#    security.declarePublic('searchItemsToValidate')
#    def searchItemsToValidate(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
#        '''Return a list of items that the user can validate.
#           Items to validated are items in state 'proposed' for wich the current user has the
#           permission to trigger the 'validate' workflow transition.  To avoid waking up the
#           object, we will check that the current user is in the _reviewers group corresponding
#           to the item proposing group (that is indexed).  So if the item proposing group is
#           'secretariat' and the user is member of 'secretariat_reviewers',
#           then he is able to validate the item.'''
#        member = self.portal_membership.getAuthenticatedMember()
#        groupIds = self.portal_groups.getGroupsForPrincipal(member)
#        res = []
#        personnel = False
#        for groupId in groupIds:
#            if groupId.endswith('_reviewers'):
#                res.append(groupId[:-10])
#                if groupId[:-10] == "personnel":
#                    personnel = True
#
#        params = {'portal_type': self.getItemTypeName(),
#                  'review_state': 'proposed',
#                  'sort_on': sortKey,
#                  'sort_order': sortOrder
#                  }
#
#        if personnel:
#            params['getCategory'] = '45-personnel'
#        else:
#            params['getProposingGroup'] = res
#
#        # Manage filter
#        if filterKey: params[filterKey] = Keywords(filterValue).get()
#        # update params with kwargs
#        params.update(kwargs)
#        # Perform the query in portal_catalog
#        return self.portal_catalog(**params)
#
#    MeetingConfig.searchItemsToValidate = searchItemsToValidate
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#
#    security.declarePublic('searchItemsInCopy')
#    def searchItemsInCopy(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
#        '''Return a list of items for which the user is in copy.'''
#        member = self.portal_membership.getAuthenticatedMember()
#        groupIds = self.portal_groups.getGroupsForPrincipal(member)
#
#        params = {'portal_type': self.getItemTypeName(),
#                  'sort_on': sortKey,
#                  'sort_order': sortOrder,
#                  'getCopyGroups':' OR '.join(groupIds)
#                  }
#
#        # Manage filter
#        if filterKey: params[filterKey] = Keywords(filterValue).get()
#        # update params with kwargs
#        params.update(kwargs)
#        # Perform the query in portal_catalog
#        return self.portal_catalog(**params)
#
#    MeetingConfig.searchItemsInCopy = searchItemsInCopy
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#
#    security.declarePublic('searchItemsInGroup')
#    def searchItemsInGroup(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
#        '''Return the list of items belonging to the user's groups.'''
#        member = self.portal_membership.getAuthenticatedMember()
#        groupIds = self.portal_groups.getGroupsForPrincipal(member)
#        res = []
#
#        for groupId in groupIds:
#            group = groupId.split('_')
#            if group[0] not in res:
#                res.append(group[0])
#
#        params = {'portal_type': self.getItemTypeName(),
#                  'getProposingGroup': res,
#                  'sort_on': sortKey,
#                  'sort_order': sortOrder,
#                  }
#
#        # Manage filter
#        if filterKey: params[filterKey] = Keywords(filterValue).get()
#        # update params with kwargs
#        params.update(kwargs)
#        # Perform the query in portal_catalog
#        return self.portal_catalog(**params)
#
#    MeetingConfig.searchItemsInGroup = searchItemsInGroup
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class
#
#
#    security.declarePublic('searchMailsInCopy')
#    def searchMailsInCopy(self, sortKey, sortOrder, filterKey, filterValue, **kwargs):
#        '''Returns the list of mails for which the user is in copy.'''
#        member = self.portal_membership.getAuthenticatedMember()
#        params = {'portal_type': 'CourrierFile',
#                  'getDestUsers': member.id,
#                  'sort_on': sortKey,
#                  'sort_order': sortOrder,
#                  }
#
#        # Manage filter
#        if filterKey: params[filterKey] = Keywords(filterValue).get()
#        # update params with kwargs
#        params.update(kwargs)
#        # Perform the query in portal_catalog
#        return self.portal_catalog(**params)
#
#    MeetingConfig.searchMailsInCopy = searchMailsInCopy
#    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingConfig class


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

#    security.declarePublic('getSpecificAssemblyFor')
#    def getSpecificAssemblyFor(self, assembly, startTxt=''):
#        ''' Return the Assembly between two tag.
#            This method is used in templates.
#        '''
#        #Pierre Dupont - Bourgmestre,
#        #Charles Exemple - 1er Echevin,
#        #Echevin Un, Echevin Deux excusÃ©, Echevin Trois - Echevins,
#        #Jacqueline Exemple, Responsable du CPAS
#        #Absentes:
#        #Mademoiselle x
#        #ExcusÃ©s:
#        #Monsieur Y, Madame Z
#        res = []
#        tmp = ['<p class="mltAssembly">']
#        splitted_assembly = assembly.replace('<p>', '').replace('</p>', '').split('<br />')
#        start_text = startTxt == ''
#        for assembly_line in splitted_assembly:
#            assembly_line = assembly_line.strip()
#            #check if this line correspond to startTxt (in this cas, we can begin treatment)
#            if not start_text:
#                start_text = assembly_line.startswith(startTxt)
#                if start_text:
#                    #when starting treatment, add tag (not use if startTxt=='')
#                    res.append(assembly_line)
#                continue
#            #check if we must stop treatment...
#            if assembly_line.endswith(':'):
#                break
#            lines = assembly_line.split(',')
#            cpt = 1
#            my_line = ''
#            for line in lines:
#                if cpt == len(lines):
#                    my_line = "%s%s<br />" % (my_line, line)
#                    tmp.append(my_line)
#                else:
#                    my_line = "%s%s," % (my_line, line)
#                cpt = cpt + 1
#        if len(tmp) > 1:
#            tmp[-1] = tmp[-1].replace('<br />', '')
#            tmp.append('</p>')
#        else:
#            return ''
#        res.append(''.join(tmp))
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

    security.declarePublic('mayClose')
    def mayClose(self):
        res = False
        # The user just needs the "Review portal content" permission on the
        # object to close it.
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res

    security.declarePublic('mayDecide')
    def mayDecide(self):
        res = False
        if checkPermission(ReviewPortalContent, self.context):
            res = True
        return res


# ------------------------------------------------------------------------------
class MeetingItemCollegeAndenneWorkflowActions(MeetingItemWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemAndenneWorkflowActions'''

    implements(IMeetingItemCollegeAndenneWorkflowActions)
    security = ClassSecurityInfo()

    security.declarePrivate('doPre_accept')
    def doPre_accept(self, stateChange):
        pass

    security.declarePrivate('doAccept_but_modify')
    def doAccept_but_modify(self, stateChange):
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
