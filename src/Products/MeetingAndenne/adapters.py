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
from persistent.mapping import PersistentMapping
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
     TOPIC_SEARCH_SCRIPT, TOPIC_SEARCH_FILTERS, TOPIC_TYPE, MEETINGREVIEWERS
from Products.PloneMeeting.Meeting import MeetingWorkflowActions, \
     MeetingWorkflowConditions, Meeting
from Products.PloneMeeting.MeetingItem import MeetingItem, \
     MeetingItemWorkflowConditions, MeetingItemWorkflowActions
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingFile import MeetingFile
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.ToolPloneMeeting import ToolPloneMeeting
from Products.PloneMeeting.interfaces import IMeetingCustom, IMeetingItemCustom, \
                                             IMeetingConfigCustom, IMeetingFileCustom, \
                                             IMeetingGroupCustom, IToolPloneMeetingCustom
from Products.MeetingAndenne.interfaces import \
     IMeetingItemCollegeAndenneWorkflowActions, IMeetingItemCollegeAndenneWorkflowConditions, \
     IMeetingCollegeAndenneWorkflowActions, IMeetingCollegeAndenneWorkflowConditions, \
     IMeetingItemFormation
from Products.MeetingAndenne.config import MAIL_TYPES, SEARCH_TYPES
from Products.MeetingAndenne.SearcherAndenne import SearcherAndenne
from Products.PloneMeeting.utils import checkPermission, getCustomAdapter, prepareSearchValue
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.model.adaptations import WF_DOES_NOT_EXIST_WARNING, WF_APPLIED
from DateTime import DateTime

# Some lines added for the OCR functionalities
import os, os.path, time, unicodedata
import transaction
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

adaptations.performWorkflowAdaptations = customPerformWorkflowAdaptations


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
        if not useforpv:
            # normal usage
            res = meeting.getSignatories(theObjects=True, includeDeleted=False,includeReplacements=userepl)
        else:
            # utiisé dans la partie adopté en séance des PV , pour que le  "Directeur General" et "Bourgmestre" soit affiché même si ils sont absent (on prend les signataire par defaut de la seance) 
            tool = getToolByName(self.context, 'portal_plonemeeting')
            cfg = tool.getMeetingConfig(self.context)
            for user in cfg.getMeetingUsers(usages=('signer',)):
                if user.getSignatureIsDefault():
                    res.append(user)

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

    security.declarePublic('getStrikedAssembly')
    def getStrikedAssembly(self, groupByDuty=True,strikefirst=True,strikemidle=True,strikelast=False,userepl=True):
        '''
          Generates a HTML version of the assembly :
          - strikes absents (represented using [[Member assembly name]])
          - add a 'mltAssembly' class to generated <p> so it can be used in the Pod Template
          If p_groupByDuty is True, the result will be generated with members having the same
          duty grouped, and the duty only displayed once at the end of the list of members
          having this duty...  This is only relevant if MeetingUsers are enabled.
        '''
        meeting = self.getSelf()
        repl = meeting.getUserReplacements()
        repl2 = [repl[user] for user in repl]
        repl3 = {}
        for user in repl:
         repl3[repl[user]]=user
        # either we use free textarea to define assembly...
        if meeting.getAssembly():
            tool = getToolByName(meeting, 'portal_plonemeeting')
            return tool.toHTMLStrikedContent(meeting.getAssembly())
        # ... or we use MeetingUsers
        elif meeting.getAttendees():
            res = []
            attendeeIds = meeting.getAttendees()
            groupedByDuty = OrderedDict()
            m = 0
            UsedMeetingUsers = [mUser for mUser in meeting.getAllUsedMeetingUsers(usages=['assemblyMember','signer', ])] # ADDED BY FABMAR : just added signer for rongos from original
            UsedMeetingUsersMinusreplacedIds = [mUser.getId() for mUser in meeting.getAllUsedMeetingUsers(usages=['assemblyMember', 'signer', ]) if mUser.getId() not in repl2] # ADDED BY FABMAR
            for mUser in UsedMeetingUsers:
                ### ADDED BY FABMAR FROM ORIGINAL
                userId = mUser.getId()
                userTitle = mUser.Title()
                userDuty = mUser.getDuty()
                strikeme = True
                deleteme = False
                if userepl == True:
                    ### ce members est-il a remplacer?
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
                            ### ce membre n'est pas a remplacer mais peut-être qu'il remplace quelqu'un qu'on a pas décidé de ne pas barrer (dans quel cas , il ne faut plus le faire apparaitre)
                            if userId in repl2 and not ((strikefirst==True and UsedMeetingUsersMinusreplacedIds.index(repl3[userId])==0) or (strikemidle==True and UsedMeetingUsersMinusreplacedIds.index(repl3[userId])>0 and UsedMeetingUsersMinusreplacedIds.index(repl3[userId])<len(UsedMeetingUsersMinusreplacedIds)-1) or (strikelast==True and UsedMeetingUsersMinusreplacedIds.index(repl3[userId])==len(UsedMeetingUsersMinusreplacedIds)-1)):
                                deleteme = True 
                            else:
                                ### ce membre n'est pas a remplacer et il ne remplace personne, on va juste verifié si il doit être barré ou pas
                                if not ((strikefirst==True and m==0) or (strikemidle==True and m>0 and m<len(UsedMeetingUsers)-1) or (strikelast==True and m==len(UsedMeetingUsers)-1)):
                                    ### on a pas décidé de barrer donc il faut uniquement supprimer la personne sinon on a décidé de barrer le membre, c'est le comportement par défaut, on ne fait rien
                                    if not userId in attendeeIds: #il faut juste verifié que il est bien absent avant de l'enlever
                                        deleteme = True
                    else: 
                        # il n'y a pas de remplacement, on regarde juste si on barre ou pas
                        if not ((strikefirst==True and m==0) or (strikemidle==True and m>0 and m<len(UsedMeetingUsers)-1) or (strikelast==True and m==len(UsedMeetingUsers)-1)):
                            ### on a pas décidé de barrer donc il faut uniquement supprimer la personne sinon on a décidé de barrer le membre, c'est le comportement par défaut, on ne fait rien
                            if not userId in attendeeIds: #il faut juste verifié que il est bien absent avant de l'enlever
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
        groupstr=''
        if groupsCopyTo:
            for group in groupsCopyTo:
                ploneGroup = self.context.portal_groups.getGroupById(group)
                groupstr += ploneGroup.getProperty('title').split('(')[0] + ','
        if groupstr != '':
            return 'Copie(s): ' + groupstr[0:-1]
        else:
            return ''

    security.declarePublic('getPrintableNumCategory')
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

    security.declarePublic('getSignatoriesForPrinting') 
    def getSignatoriesForPrinting (self, pos=0, level=0, useforpv=False, userepl=True):
        # new from plonemeeting 3.3 :print sigantories in template relative to position ans level. pos 0 and level 0 is the first sigantory (bg) and function. 
        # pos 0 and level 1 is the first signatory (bg) with Name
        res = []
        i = 0
        item = self.getSelf()
        if not useforpv:
            # normal usage
            res = item.getItemSignatories(theObjects=True, includeDeleted=False, includeReplacements=userepl)       
        else:
            # utiisé dans la partie adopté en séance des PV , pour que le  "Directeur General" et "Bourgmestre" soit affiché même si ils sont absent (on prend les signataire par defaut de la seance)
            tool = getToolByName(self.context, 'portal_plonemeeting')
            cfg = tool.getMeetingConfig(self.context)
            for user in cfg.getMeetingUsers(usages=('signer',)):
                if user.getSignatureIsDefault():
                    res.append(user)

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

    security.declarePublic('adapted')
    def adapted(self):
        '''Gets the "adapted" version of myself. If no custom adapter is found,
           this method returns me.'''
        if not hasattr(self, 'template'):
            return getCustomAdapter(self)
        else:
            res = self
            cmd = "res = I%s(self)" % getattr(self, 'template')
            try:
                exec cmd
            except TypeError:
                pass
            return res

    MeetingItem.adapted = adapted
    # it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

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

    security.declarePublic('getExtraFieldsToCopyWhenCloning')
    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc):
        '''Lists the fields to keep when cloning an item'''
        return ['projetpv', 'textpv', 'pv']

    security.declarePrivate('replaceBr')
    def replaceBr (self,text):
        description = text

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

    security.declarePrivate('onEdit')
    def onEdit(self, isCreated):
        tool = self.context.portal_plonemeeting

        # replace div by p, because xhtmlparlser convert div to page-break and it causes problems in text align justify
        # replace line breaks by </p><p> because line breaks are in <p> and causes justify problems
        description = self.context.Description()
        description = description.replace("<div", "<p").replace("</div>", "</p>")
        self.context.setDescription(self.context.replaceBr(description))

        decision = self.context.getDecision()
        decision = decision.replace("<div", "<p").replace("</div>", "</p>")
        self.context.setDecision(self.context.replaceBr(decision))

        projetpv = self.context.getProjetpv()
        projetpv = projetpv.replace("<div", "<p").replace("</div>", "</p>")
        self.context.setProjetpv(self.context.replaceBr(projetpv))

        textpv = self.context.getTextpv()
        textpv = textpv.replace("<div", "<p").replace("</div>", "</p>")
        self.context.setTextpv(self.context.replaceBr(textpv))

        pv = self.context.getPv()
        pv = pv.replace("<div", "<p").replace("</div>", "</p>")
        self.context.setPv(self.context.replaceBr(pv))

        # Add local roles corresponding to the proposing group if item category is personnel or if item is confidential
        if self.context.getCategory() == "45-personnel" or self.context.getIsconfidential() == True:
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
                if self.context.getCategory() == "45-personnel":
                    MEETINGROLESTOADD['MeetingPreReviewer'] = ( personnelGroup, 'prereviewers' )
                    if self.context.getIsconfidential() == True:
                        MEETINGROLESTOADD['MeetingObserverLocal'] = ( meetingGroup, 'prereviewers' )
                else:
                    MEETINGROLESTOADD['MeetingPreReviewer'] = ( meetingGroup, 'prereviewers' )
            else:
                MEETINGROLESTOADD['MeetingPreReviewer'] = ( meetingGroup, 'prereviewers' )
                if self.context.getCategory() == "45-personnel":
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
        newItem.setDecision(self.getTextpv())
        newItem.setProjetpv(self.getPv())
        newItem.reindexObject(idxs=['getDecision', 'getProjetpv'])

        self.plone_utils.addPortalMessage(
            translate('item_duplicated', domain='PloneMeeting', context=self.REQUEST))
        return self.REQUEST.RESPONSE.redirect(newItem.absolute_url())

    MeetingItem.onDuplicate = onDuplicate
    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingItem class

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
        isPersonnel = False
        for groupId in groupIds:
            for reviewer_suffix, review_state in MEETINGREVIEWERS.items():
                if groupId.startswith('personnel'):
                    isPersonnel = True
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
        if isPersonnel:
            del params['reviewProcessInfo']
            params['getCategory'] = '45-personnel'
            params['review_state'] = 'proposed'
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
class CustomMeetingFileAndenne(MeetingFile):
    '''Adapter that adapts a meeting File implementing IMeetingFile to the
       interface IMeetingFileCustom.'''
    implements(IMeetingFileCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

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

    MeetingFile.indexExtractedText=indexExtractedText
    #it'a a monkey patch because it's the only way to change the behaviour of the MeetingFile class


# ------------------------------------------------------------------------------
class CustomMeetingGroupAndenne(MeetingGroup):
    '''Adapter that adapts a meeting group item implementing IMeetingGroup to the
       interface IMeetingGroupCustom.'''
    implements(IMeetingGroupCustom)
    security = ClassSecurityInfo()

    def __init__(self, group):
        self.context = group


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

    security.declarePublic('getSearchTypeFor')
    def getSearchTypeFor(self, meetingType):
        '''
            Returns the portal_type to be used in a search local to the given meeting type.
        '''
        return SEARCH_TYPES[meetingType]

    security.declarePublic('getMailTypesForSearch')
    def getMailTypesForSearch(self):
        '''
            Returns the ids and titles of all the available mail types for
            search purposes.
        '''
        return MAIL_TYPES.items()


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

    security.declarePublic('doDelay_and_close')
    def doDelay_and_close(self, stateChange):
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
        if item.getCategory() == "45-personnel":
            return len(userMeetingGroups) > 0
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
        userMeetingGroups = tool.getGroupsForUser(suffix="prereviewers")
        return group in userMeetingGroups or user.has_role('Manager', item)

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
InitializeClass(CustomMeetingConfigAndenne)
InitializeClass(CustomMeetingFileAndenne)
InitializeClass(CustomMeetingGroupAndenne)
InitializeClass(CustomToolMeetingAndenne)
InitializeClass(MeetingCollegeAndenneWorkflowActions)
InitializeClass(MeetingCollegeAndenneWorkflowConditions)
InitializeClass(MeetingItemCollegeAndenneWorkflowActions)
InitializeClass(MeetingItemCollegeAndenneWorkflowConditions)
# ------------------------------------------------------------------------------
