# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 by Imio.be
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

import locale
from Products.CMFCore.utils import getToolByName
from Products.PloneMeeting.utils import sendMail
import logging
logger = logging.getLogger('MeetingAndenne')

# MeetingAndenneError-related constants ----------------------------------------

# ------------------------------------------------------------------------------
def isFloat(string):
    '''Returns whether the given string is convertible to a float or not.'''
    try:
        float(string)
        return True
    except ValueError:
        return False

def collateDisplayListsKeys(displayListTuple):
    '''Function used to collate DisplayLists tuples by key.'''
    return locale.strxfrm(displayListTuple[0])

def collateDisplayListsValues(displayListTuple):
    '''Function used to collate DisplayLists tuples by value.'''
    return locale.strxfrm(displayListTuple[1])

def getMeetingUser(obj, id):
    '''Gets the MeetingUser object defined on a given obj (item or meeting)
       and having the given id.'''
    cfg = obj.portal_plonemeeting.getMeetingConfig(obj)
    return getattr(cfg.meetingusers, id, None)

def sendMailToCopyGroupsIfRelevant(obj, event, mapping={}):
    '''An event just occurred on item obj. If the corresponding meeting config
       specifies that a mail needs to be sent, this function will send a mail.
       The mail subject and body are defined from i18n labels that derive from
       the event name. The mail will be sent to every user present in a
       copy_group defined on this item. Some mapping can be received and used
       afterward in mail subject and mail body translations.
       If mail sending is activated (or in test mode) and enabled for this
       event, this method returns True.'''
    tool = getToolByName(obj, 'portal_plonemeeting')
    groupsTool = getToolByName(obj, 'portal_groups')
    membershipTool = getToolByName(obj, 'portal_membership')
    currentUser = membershipTool.getAuthenticatedMember()
    cfg = tool.getMeetingConfig(obj)
    # Do not send the mail if mail mode is "deactivated".
    if cfg.getMailMode() == 'deactivated':
        return
    # Do not send mail if the event is unknown.
    if event not in cfg.getMailItemEvents() and \
       event not in cfg.getMailMeetingEvents():
        return
    # Ok, send a mail. Who are the recipients ?
    recipients = set()
    adap = obj.adapted()
    copyGroups = obj.getCopyGroups()
    if copyGroups:
        for group in copyGroups:
            ploneGroup = groupsTool.getGroupById(group)
            groupMembers = ploneGroup.getMemberIds()
            for userId in groupMembers:
                user = membershipTool.getMemberById(userId)
                # do not warn user doing the action
                if not user or userId == currentUser.getId():
                    continue
                if not user.getProperty('email'):
                    continue

                recipient = tool.getMailRecipient(user)
                # Must we avoid sending mail to this recipient for some custom reason?
                if not adap.includeMailRecipient(event, userId):
                    continue
                # Has the user unsubscribed to this event in his preferences ?
                itemEvents = cfg.getUserParam('mailItemEvents', request=obj.REQUEST, userId=userId)
                meetingEvents = cfg.getUserParam('mailMeetingEvents', request=obj.REQUEST, userId=userId)
                if (event not in itemEvents) and (event not in meetingEvents):
                    continue
                # After all, we will add this guy to the list of recipients.
                recipients.add(recipient)
    if recipients:
        sendMail(list(recipients), obj, event, mapping=mapping)
    return True
