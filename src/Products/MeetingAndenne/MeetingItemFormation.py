# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.Archetypes.ClassGen import generateClass
from zope.interface import implements
import interfaces

#from Products.PloneMeeting.config import *

from Globals import InitializeClass
from DateTime import DateTime
from zope.i18n import translate
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.MeetingAndenne.adapters import CustomMeetingItemAndenne
from Products.MeetingAndenne.interfaces import IMeetingItemFormation

from Products.MeetingAndenne.config import *
from Products.MeetingAndenne.utils import *

# ------------------------------------------------------------------------------

# Some lines added for the OCR functionalities
#import os, os.path, time, unicodedata
#import transaction

import logging
logger = logging.getLogger( 'MeetingAndenne' )

schema = Schema((

    StringField(
        name='training_type',
        default="training",
        widget=SelectionWidget(
            label='Type',
            label_msgid='MeetingAndenne_label_training_type',
            i18n_domain='PloneMeeting',
        ),
        vocabulary='listTrainingTypes'
    ),

    StringField(
        name='training_purpose',
        default="purpose",
        widget=StringWidget(
            size=100,
            label='Purpose',
            label_msgid='MeetingAndenne_label_training_purpose',
            i18n_domain='PloneMeeting',
        ),
        required=True
    ),

    DateTimeField(
        name='training_startDate',
        default_method="getTrainingDate",
        widget=DateTimeField._properties['widget'](
            label='Startdate',
            label_msgid='MeetingAndenne_label_training_startDate',
            i18n_domain='PloneMeeting',
        ),
        required=True
    ),

    DateTimeField(
        name='training_endDate',
        default_method="getTrainingDate",
        widget=DateTimeField._properties['widget'](
            label='Enddate',
            label_msgid='MeetingAndenne_label_training_endDate',
            i18n_domain='PloneMeeting',
        ),
        required=True
    ),

    StringField(
        name='training_periodicity',
        widget=StringWidget(
            size= 100,
            label='Periodicity',
            label_msgid='MeetingAndenne_label_training_periodicity',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_organiser',
        default="organiser",
        widget=StringWidget(
            size= 100,
            label='Organiser',
            label_msgid='MeetingAndenne_label_training_organiser',
            i18n_domain='PloneMeeting',
        ),
        required=True
    ),

    StringField(
        name='training_place',
        default="place",
        widget=StringWidget(
            size= 100,
            label='Place',
            label_msgid='MeetingAndenne_label_training_place',
            i18n_domain='PloneMeeting',
        ),
        required=True
    ),

    LinesField(
        name='training_users',
        default_method="Creator",
        widget=MultiSelectionWidget(
            size=10,
            label='Users',
            label_msgid='MeetingAndenne_label_training_users',
            i18n_domain='PloneMeeting',
        ),
        enforceVocabulary=True,
        multiValued=1,
        vocabulary='listTrainingUsers',
    ),

    StringField(
        name='training_additionalUsers',
        default="",
        widget=StringWidget(
            size=100,
            label='Additionalusers',
            label_msgid='MeetingAndenne_label_training_additionalUsers',
            i18n_domain='PloneMeeting',
        ),
    ),

    TextField(
        name='training_description',
        default_method="getTrainingDescription",
        widget=TextAreaWidget(
            label='Description',
            label_msgid='MeetingAndenne_label_training_description',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_registrationFee',
        widget=StringWidget(
            size= 100,
            label='Registrationfee',
            label_msgid='MeetingAndenne_label_training_registrationFee',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_syllabusCosts',
        widget=StringWidget(
            size= 100,
            label='Syllabuscosts',
            label_msgid='MeetingAndenne_label_training_syllabusCosts',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_travelExpenses',
        widget=StringWidget(
            size= 100,
            label='Travelexpenses',
            label_msgid='MeetingAndenne_label_training_travelExpenses',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_parkingFees',
        widget=StringWidget(
            size= 100,
            label='Parkingfees',
            label_msgid='MeetingAndenne_label_training_parkingFees',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_accomodationExpenses',
        widget=StringWidget(
            size= 100,
            label='Accomodationexpenses',
            label_msgid='MeetingAndenne_label_training_accomodationExpenses',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_otherFees',
        widget=StringWidget(
            size= 100,
            label='Otherfees',
            label_msgid='MeetingAndenne_label_training_otherFees',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_paymentTerms',
        widget=SelectionWidget(
            format="radio",
            label='Paymentterms',
            label_msgid='MeetingAndenne_label_training_paymentTerms',
            i18n_domain='PloneMeeting',
        ),
        vocabulary='listPaymentTerms',
    ),

    StringField(
        name='training_accountNumber',
        default="IBAN: BEXX-XXXX-XXXX-XXXX BIC:XXXX BE XX",
        widget=StringWidget(
            size= 100,
            label='Accountnumber',
            label_msgid='MeetingAndenne_label_training_accountNumber',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_accountName',
        widget=StringWidget(
            size= 100,
            label='Accountname',
            label_msgid='MeetingAndenne_label_training_accountName',
            i18n_domain='PloneMeeting',
        ),
    ),

    StringField(
        name='training_acceptanceGiro',
        widget=StringWidget(
            size= 100,
            label='Acceptancegiro',
            label_msgid='MeetingAndenne_label_training_acceptanceGiro',
            i18n_domain='PloneMeeting',
        ),
    ),
),
)

MeetingItemFormation_schema = MeetingItem.schema.copy() + schema.copy()
MeetingItemFormation_schema['title'].widget.condition = "python: not here.queryState()=='itemcreated' or here.portal_membership.getAuthenticatedMember().has_role('Manager')"
MeetingItemFormation_schema['category'].widget.visible = {"edit": "invisible" }
MeetingItemFormation_schema['budgetRelated'].widget.label_msgid_template_edit = 'MeetingAndenne_label_training_budgetRelated'


class MeetingItemFormation(CustomMeetingItemAndenne):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCustom.'''
    implements(IMeetingItemFormation)
    security = ClassSecurityInfo()

    meta_type = 'MeetingItem'
    schema = MeetingItemFormation_schema

    def __init__(self, item):
        self.context = item

    def getExtraFieldsToCopyWhenCloning(self, cloned_to_same_mc):
        ''' Lists the fields to keep when cloning an item'''
        return ['template']

    security.declarePublic('getTrainingDate')
    def getTrainingDate(self):
        '''Returns current date.'''
        return DateTime()

    MeetingItem.getTrainingDate = getTrainingDate
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePublic('getTrainingDescription')
    def getTrainingDescription(self):
        '''Returns the training_description translation.'''
        d = "PloneMeeting"
        requestContext = self.getSelf().REQUEST
        return translate('training_description', domain=d, context=requestContext).encode('utf-8')

    MeetingItem.getTrainingDescription = getTrainingDescription
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePrivate('listTrainingUsers')
    def listTrainingUsers(self):
        '''List the users that will be selectable to be in destination (view only) for this
           item.'''
        pgp = self.portal_membership
        res = []
        for user in pgp.listMembers():
            if user.getProperty('listed'):
                res.append( (user.getId(), user.getProperty('fullname')) )
        res = sorted( res, key=collateDisplayListsValues )
        return DisplayList( tuple(res) )

    MeetingItem.listTrainingUsers = listTrainingUsers
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePrivate('listTrainingTypes')
    def listTrainingTypes(self):
        '''List the training types selectable in a training form.'''
        d = "PloneMeeting"
        requestContext = self.getSelf().REQUEST
        res = DisplayList((
            ("training", translate('a_training', domain=d, context=requestContext)),
            ("workshop", translate('a_workshop', domain=d, context=requestContext)),
            ("seminar", translate('a_seminar', domain=d, context=requestContext)),
            ("workSession", translate('a_work_session', domain=d, context=requestContext)),
            ("informationSession", translate('an_information_session', domain=d, context=requestContext)),
            ("symposium", translate('a_symposium', domain=d, context=requestContext)),
            ("show", translate('a_show', domain=d, context=requestContext)),
        ))
        return res

    MeetingItem.listTrainingTypes = listTrainingTypes
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePublic('listPaymentTerms')
    def listPaymentTerms(self):
        '''List the payment terms selectable in a training form.'''
        d = "PloneMeeting"
        requestContext = self.getSelf().REQUEST
        res = DisplayList((
            ("after", translate('payment_after', domain=d, context=requestContext)),
            ("before", translate('payment_before', domain=d, context=requestContext)),
        ))
        return res

    MeetingItem.listPaymentTerms = listPaymentTerms
    # it'a a monkey patch because it's the only way to add a behaviour to the MeetingItem class

    security.declarePrivate('extractBudget')
    def extractBudget(self):
        if (not self.context.budgetRelated):
            return ['','']

        returnValue = ['XXXX','YYYY']
        budget_array = self.context.budgetInfos().replace(';',' ').replace('>',' ').replace('&',' ').replace('<',' ').split()
        for element in budget_array:
            price = element.replace('.','').replace(',','.')
            if isFloat(price):
                returnValue[0] = element
                break
        for element in budget_array:
            article = element.replace('.','').replace('/','').replace('-','')
            if isFloat(article) and element.count('/') == 1:
                returnValue[1] = element
                break
        return returnValue

    security.declarePublic('onEdit')
    def onEdit(self, isCreated):
        if isCreated:
            self.context.setRefdoc(self.context.getDocReference())
            self.context.setVerifUser(self.context.Creator())
            self.context.setTreatUser(self.context.Creator())
            self.context.training_purpose = ""
            self.context.training_startDate = ""
            self.context.training_endDate = ""
            self.context.training_organiser = ""
            self.context.training_place = ""
        else:
            description1 = self.context.translate('MeetingAndenne_training_description1', domain='PloneMeeting').encode('utf-8')
            description2 = self.context.translate('MeetingAndenne_training_description2free', domain='PloneMeeting').encode('utf-8')
            description3 = ''
            description4 = self.context.translate('MeetingAndenne_training_description4', domain='PloneMeeting').encode('utf-8')
            decision1 = self.context.translate('MeetingAndenne_training_decision1', domain='PloneMeeting').encode('utf-8')
            decision2 = self.context.translate('MeetingAndenne_training_decision2free', domain='PloneMeeting').encode('utf-8')
            decision3 = ''
            decision4 = self.context.translate('MeetingAndenne_training_decision4', domain='PloneMeeting').encode('utf-8')

            trainingTypes = self.listTrainingTypes()
            trainingType = trainingTypes.getValue(self.context.getTraining_type()).encode('utf-8')

            if self.context.getTraining_periodicity() != "":
                periodicity = ", " + self.context.getTraining_periodicity() + ","
            else:
                periodicity = ""

            i = 0
            users = ""
            participants = self.context.getTraining_users()
            additionalUsers = self.context.getTraining_additionalUsers()
            for user in participants:
                i += 1
                ploneUser = self.context.portal_membership.getMemberById(user)
                if ploneUser.getProperty('function'):
                    function = ", " + ploneUser.getProperty('function')
                else:
                    function = ""
                if ploneUser.getProperty('gender'):
                    gender = ploneUser.getProperty('gender')
                    if gender == 'homme':
                        gender = "Monsieur "
                    elif gender == 'femme':
                        gender = "Madame "
                    else:
                        gender = ""
                else:
                    gender= ""
                if i > 1:
                    if len(participants) == i and additionalUsers == "":
                        users += " et "
                    else:
                        users += ", "
                users += gender + ploneUser.getProperty('fullname') + function
            if additionalUsers != "":
                if users != "":
                    users += ", " + additionalUsers
                else:
                    users = addiotionalUsers
            if i < 2:
                usertitle = " - " + users
            else:
                usertitle = ""

            budget_array = self.extractBudget()
            price = budget_array[0]
            registrationFee = self.context.getTraining_registrationFee()
            budget = budget_array[1]
            description3 = ''
            decision3 = ''
            payment = ''

            description1 %= { 'training_type': trainingType,
                              'training_purpose': self.context.getTraining_purpose(),
                              'training_startDate': self.context.getTraining_startDate().strftime("%d %B %Y à %H:%M"),
                              'training_endDate': self.context.getTraining_endDate().strftime("%d %B %Y à %H:%M"),
                              'training_periodicity': periodicity,
                              'training_organiser': self.context.getTraining_organiser(),
                            }

            decision1 %= { 'training_type': trainingType,
                           'training_purpose': self.context.getTraining_purpose(),
                           'training_startDate': self.context.getTraining_startDate().strftime("%d %B %Y à %H:%M"),
                           'training_endDate': self.context.getTraining_endDate().strftime("%d %B %Y à %H:%M"),
                           'training_periodicity': self.context.getTraining_periodicity(),
                           'training_organiser': self.context.getTraining_organiser(),
                           'training_place': self.context.getTraining_place(),
                           'training_users': users,
                         }

            if price != '':
                description2 = self.context.translate('MeetingAndenne_training_description2', domain='PloneMeeting').encode('utf-8') % \
                                { 'training_price': price, 'training_budget': budget }
                decision2 = self.context.translate('MeetingAndenne_training_decision2', domain='PloneMeeting').encode('utf-8') % \
                                { 'training_price': price, 'training_budget': budget }

                registrationFee = self.context.getTraining_registrationFee()
                syllabusCosts = self.context.getTraining_syllabusCosts()
                travelExpenses = self.context.getTraining_travelExpenses()
                parkingFees = self.context.getTraining_parkingFees()
                accomodationExpenses = self.context.getTraining_accomodationExpenses()
                otherFees = self.context.getTraining_otherFees()

                if syllabusCosts != '' or travelExpenses != '' or parkingFees != '' or accomodationExpenses != '' or otherFees != '':
                    if syllabusCosts:
                        syllabusCostsText = self.context.translate('MeetingAndenne_training_syllabusCosts', domain='PloneMeeting').encode('utf-8') % { 'training_syllabusCosts': syllabusCosts }
                    else:
                        syllabusCostsText = ""
                    if travelExpenses:
                        travelExpensesText = self.context.translate('MeetingAndenne_training_travelExpenses', domain='PloneMeeting').encode('utf-8') % { 'training_travelExpenses': travelExpenses }
                    else:
                        travelExpensesText = ""
                    if parkingFees:
                        parkingFeesText = self.context.translate('MeetingAndenne_training_parkingFees', domain='PloneMeeting').encode('utf-8') % { 'training_parkingFees': parkingFees }
                    else:
                        parkingFeesText = ""
                    if accomodationExpenses:
                        accomodationExpensesText = self.context.translate('MeetingAndenne_training_accomodationExpenses', domain='PloneMeeting').encode('utf-8') % { 'training_accomodationExpenses': accomodationExpenses }
                    else:
                        accomodationExpensesText = ""
                    if otherFees:
                        otherFeesText = self.context.translate('MeetingAndenne_training_otherFees', domain='PloneMeeting').encode('utf-8') % { 'training_otherFees': otherFees }
                    else:
                        otherFeesText = ""

                    description3 = self.context.translate('MeetingAndenne_training_description3', domain='PloneMeeting').encode('utf-8') + \
                                    syllabusCostsText + travelExpensesText + parkingFeesText + accomodationExpensesText + otherFeesText
                    decision3 = self.context.translate('MeetingAndenne_training_decision3', domain='PloneMeeting').encode('utf-8') + \
                                    syllabusCostsText + travelExpensesText + parkingFeesText + accomodationExpensesText + otherFeesText

                if self.context.getTraining_paymentTerms():
                    terms = self.listPaymentTerms()
                    if self.context.getTraining_paymentTerms() == 'after':
                        payment = "<p>" + terms.values()[0].encode('utf-8') + "</p>"
                    else:
                        payment = "<p>" + terms.values()[1].encode('utf-8') + \
                                    self.context.translate('MeetingAndenne_training_accountNumber', domain='PloneMeeting').encode('utf-8') + \
                                    self.context.getTraining_accountNumber() + " " + \
                                    self.context.translate('MeetingAndenne_training_accountName', domain='PloneMeeting').encode('utf-8') + \
                                    self.context.getTraining_accountName() + " " + \
                                    self.context.translate('MeetingAndenne_training_acceptanceGiro', domain='PloneMeeting').encode('utf-8') + \
                                    self.context.getTraining_acceptanceGiro() + "</p>"

            # On ne remplace pas le titre si on est en mode template car le titre doit rester le meme pour l'affichage du template
            if self.context.queryState() != "active":
                self.context.setTitle("Demande de formation - " + self.context.getTraining_purpose() + usertitle)
            self.context.setDescription(description1 + "<p>" + self.context.getTraining_description() + "</p>" + description2 + description3 + description4)
            self.context.setDecision(decision1 + decision2 + payment + decision3 + decision4)

        CustomMeetingItemAndenne.onEdit(self, isCreated)


generateClass(MeetingItemFormation)

# Create missing accessors and mutators in MeetingItem class
meetingItemSchema = MeetingItem.schema
MeetingItem.schema = MeetingItemFormation.schema
generateClass(MeetingItem)
MeetingItem.schema = meetingItemSchema

##code-section module-footer #fill in your manual code here
#/#code-section module-footer