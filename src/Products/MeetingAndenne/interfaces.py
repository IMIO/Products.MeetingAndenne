# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Copyright (c) 2011 by CommunesPlone.org
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

__author__ = """Gauthier Bastien <gbastien@commune.sambreville.be>"""
__docformat__ = 'plaintext'

# ------------------------------------------------------------------------------
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.PloneMeeting.interfaces import \
    IMeetingItemWorkflowConditions, IMeetingItemWorkflowActions, \
    IMeetingWorkflowActions, IMeetingWorkflowConditions

# ------------------------------------------------------------------------------
class IMeetingItemCollegeAndenneWorkflowActions(IMeetingItemWorkflowActions):
    '''This interface represents a meeting item as viewed by the specific meeting
       item workflow that is defined in this MeetingCommunes product.'''
    def doPre_accept(stateChange):
        """
          Triggered while doing the 'pre_accept' transition
        """
    def doAccept_but_modify(stateChange):
        """
          Triggered while doing the 'accept_but_modify' transition
        """
    def doAccept_but_modify_and_close(stateChange):
        """
          Triggered while doing the 'accept_but_modify_and_close' transition
        """
    def doAccept_and_close(stateChange):
        """
          Triggered while doing the 'accept_and_close' transition
        """
    def doDelay_and_close(stateChange):
        """
          Triggered while doing the 'delay_and_close' transition
        """
    def doRefuse_and_close(stateChange):
        """
          Triggered while doing the 'refuse_and_close' transition
        """

class IMeetingItemCollegeAndenneWorkflowConditions(IMeetingItemWorkflowConditions):
    '''This interface represents a meeting item as viewed by the specific meeting
       workflow that is defined in this MeetingCommunes product.'''
    def mayDecide():
        """
          Guard for the 'decide' transition
        """
    def mayPrevalidate():
        """
          Guard for the 'prevalidate' transition
        """
#    def mayValidate():
#        """
#          Guard for the 'validate' transition
#        """

class IMeetingCollegeAndenneWorkflowActions(IMeetingWorkflowActions):
    '''This interface represents a meeting as viewed by the specific meeting
       workflow that is defined in this MeetingCommunes product.'''
    def doDecide(stateChange):
        """
          Triggered while doing the 'decide' transition
        """

class IMeetingCollegeAndenneWorkflowConditions(IMeetingWorkflowConditions):
    '''This interface represents a meeting as viewed by the specific meeting
       workflow that is defined in this MeetingCommunes product.'''
    def mayFreeze():
        """
          Guard for the 'freeze' transition
        """
    def mayClose():
        """
          Guard for the 'close' transitions
        """
    def mayDecide():
        """
          Guard for the 'decide' transition
        """

class ICourrierFile(Interface):
    '''Marker interface for .MeetingAndenne.CourrierFile
    '''

class IMeetingAndenneLayer(IDefaultBrowserLayer):
    """
      Define a layer so some elements are only added for it
    """
    pass

# ------------------------------------------------------------------------------
