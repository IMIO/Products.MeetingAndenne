# -*- coding: utf-8 -*-
from Products.PloneMeeting.profiles import PodTemplateDescriptor

# College Pod templates ----------------------------------------------------------------
agendaTemplate = PodTemplateDescriptor('agenda', 'O.J.')
agendaTemplate.podTemplate = 'MeetingAndenne.odt'
agendaTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

agendaCPASTemplate = PodTemplateDescriptor('agendaCPAS', 'O.J. - CPAS')
agendaCPASTemplate.podTemplate = 'MeetingAndenneCPAS.odt'
agendaCPASTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

agendaPersonnelTemplate = PodTemplateDescriptor('agendaPersonnel', 'O.J. - Personnel')
agendaPersonnelTemplate.podTemplate = 'MeetingAndennePersonnel.odt'
agendaPersonnelTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

lateAgendaTemplate = PodTemplateDescriptor('lateAgenda', 'O.J. Comp.')
lateAgendaTemplate.podTemplate = 'MeetingAndenneLate.odt'
lateAgendaTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

lateAgendaCPASTemplate = PodTemplateDescriptor('lateAgendaCPAS', 'O.J. Comp. - CPAS')
lateAgendaCPASTemplate.podTemplate = 'MeetingAndenneLateCPAS.odt'
lateAgendaCPASTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

lateAgendaPersonnelTemplate = PodTemplateDescriptor('lateAgendaPersonnel', 'O.J. Comp. - Personnel')
lateAgendaPersonnelTemplate.podTemplate = 'MeetingAndenneLatePersonnel.odt'
lateAgendaPersonnelTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

lateAgendaPersonnelTemplate = PodTemplateDescriptor('lateAgendaPersonnel', 'O.J. Comp. - Personnel')
lateAgendaPersonnelTemplate.podTemplate = 'MeetingAndenneLatePersonnel.odt'
lateAgendaPersonnelTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

agendaListTemplate = PodTemplateDescriptor('agendaList', 'Liste des points')
agendaListTemplate.podTemplate = 'MeetingAndenneList.odt'
agendaListTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

decisionTemplate = PodTemplateDescriptor('pv', 'P.V.')
decisionTemplate.podTemplate = 'MeetingAndennePV.odt'
decisionTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here) and ' \
                              'here.queryState() in [\'decided\', \'closed\']'

itemPropositionTemplate = PodTemplateDescriptor('itemProposition', 'Proposition au collège')
itemPropositionTemplate.podTemplate = 'MeetingItemAndenneProposition.odt'
itemPropositionTemplate.podCondition = 'python:here.meta_type=="MeetingItem"'

itemDeliberationTemplate = PodTemplateDescriptor('itemDeliberation', 'Délibération')
itemDeliberationTemplate.podTemplate = 'MeetingItemAndenneDeliberation.odt'
itemDeliberationTemplate.podCondition = 'python:here.meta_type=="MeetingItem" and here.queryState() not in ("itemcreated", ' \
                                            '"proposed", "prevalidated", "validated", "presented", "itemfrozen")'

itemExecutionTemplate = PodTemplateDescriptor('itemExecution', 'Note d\'exécution')
itemExecutionTemplate.podTemplate = 'MeetingItemAndenneExecution.odt'
itemExecutionTemplate.podCondition = 'python:here.meta_type=="MeetingItem" and here.queryState() not in ("itemcreated", ' \
                                            '"proposed", "prevalidated", "validated", "presented", "itemfrozen")'

collegeTemplates = [ agendaTemplate, agendaCPASTemplate, agendaPersonnelTemplate,
                     lateAgendaTemplate, lateAgendaCPASTemplate, lateAgendaPersonnelTemplate,
                     agendaListTemplate, decisionTemplate,
                     itemPropositionTemplate, itemDeliberationTemplate, itemExecutionTemplate ]

# RapColAuCon Pod templates ----------------------------------------------------------------

# Users and groups -------------------------------------------------------------
#collegeMeeting.podTemplates = collegeTemplates
# ------------------------------------------------------------------------------
