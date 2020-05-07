# -*- coding: utf-8 -*-

from Products.PloneMeeting.profiles import MeetingConfigDescriptor


MeetingConfigDescriptor.multiSelectFields += ('selectableAssociatedGroups', 'itemCopyGroupsStates', )
