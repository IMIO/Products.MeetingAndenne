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