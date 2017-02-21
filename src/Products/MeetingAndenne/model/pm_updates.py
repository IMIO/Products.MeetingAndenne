# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import MultiSelectionWidget
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.PloneMeeting.config import WriteRiskyConfig
from Products.PloneMeeting.Meeting import Meeting
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingFile import MeetingFile
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.MeetingUser import MeetingUser


# Schema updates related to MeetingItem ----------------------------------------)
def update_item_schema(baseSchema):
    specificSchema = Schema((

            StringField(
                name='refdoc',
                default_method="getDocReference",
                widget=StringWidget(
                    size= 100,
                    label='Refdoc',
                    label_msgid='MeetingAndenne_label_refDoc',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
            ),
            StringField(
                name='verifUser',
                default_method="Creator",
                widget=StringWidget(
                    visible=False,
                    format="select",
                    label='Verifuser',
                    label_msgid='MeetingAndenne_label_verifUser',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
            ),
            StringField(
                name='yourrefdoc',
                widget=StringWidget(
                    size= 100,
                    label='yourRefdoc',
                    label_msgid='MeetingAndenne_label_yourrefDoc',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True
            ),
            DateTimeField(
                name='formation_date1',
                default_method="getTrainingDate",
                widget=DateTimeField._properties['widget'](
                    label='formation_date1',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_date1',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=True
            ),
            DateTimeField(
                name='formation_date2',
                default_method="getTrainingDate",
                widget=DateTimeField._properties['widget'](
                    label='formation_date2',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_date2',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=True
            ),
            StringField(
                name='formation_periode',
                widget=StringWidget(
                    size= 100,
                    label='formation_periode',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_periode',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True
            ),
            LinesField(
                name='formation_users',
                widget=MultiSelectionWidget(
                    size=10,
                    condition="python: here.adapted().isformation()",
                    label='formation_users',
                    label_msgid='MeetingAndenne_label_formation_users',
                    i18n_domain='PloneMeeting',
                ),
                enforceVocabulary=True,
                multiValued=1,
                vocabulary='listDestUsers',
                default_method="Creator",
            ),
            StringField(
                name='formation_user',
                default='',
                widget=StringWidget(
                    size=100,
                    label='formation_user',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_user',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True
            ),
            StringField(
                name='formation_type',
                widget=SelectionWidget(
                    condition="python: here.adapted().isformation()",
                    label='formation_type',
                    label_msgid='MeetingAndenne_label_formation_type',
                    i18n_domain='PloneMeeting',
                ),
                vocabulary=("une formation","un atelier","un séminaire","une réunion de travail","une séance d'information","un colloque","un salon"),
                default="une formation"
            ),
            TextField(
                name='formation_desc',
                default="cette formation à pour but...",
                widget=TextAreaWidget(
                    label='formation_desc',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_desc',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
            ),
            StringField(
                name='formation_objet',
                default='formation_objet',
                widget=StringWidget(
                    size=100,
                    label='formation_objet',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_objet',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=True
            ),
            StringField(
                name='template_flag',
                widget=StringWidget(
                    size= 100,
                    label='template_flag',
                    label_msgid='MeetingAndenne_label_template_flag',
                    i18n_domain='PloneMeeting',
                ),
                default="normal"
            ),
            StringField(
                name='formation_place',
                default='formation_place',
                widget=StringWidget(
                    size= 100,
                    condition="python: here.adapted().isformation()",
                    label='formation_place',
                    label_msgid='MeetingAndenne_label_formation_place',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=True
            ),
            StringField(
                name='formation_name',
                default='formation_name',
                 widget=StringWidget(
                    size= 100,
                    label='formation_name',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_name',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=True
            ),
            StringField(
                name='formation_mod',
                widget=SelectionWidget(
                    format="radio",
                    label='formation_mod',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_mod',
                    i18n_domain='PloneMeeting',
                ),
                vocabulary="listFormationMod",
                searchable=True
            ),
            StringField(
                name='formation_compte',
                default="IBAN: BEXX-XXXX-XXXX-XXXX BIC:XXXX BE XX",
                widget=StringWidget(
                    size= 100,
                    label='formation_compte',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_compte',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True
            ),
            StringField(
                name='formation_compte_name',
                widget=StringWidget(
                    size= 100,
                    label='formation_compte_name',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_compte_name',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True
            ),
            StringField(
                name='formation_compte_com',
                widget=StringWidget(
                    size= 100,
                    label='formation_compte_com',
                    condition="python: here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_formation_compte_com',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True
            ),
            StringField(
                name='treatUser',
                default_method="Creator",
                widget=SelectionWidget(
                    format="select",
                    label='Treatuser',
                    label_msgid='MeetingAndenne_label_treatUser',
                    i18n_domain='PloneMeeting',
                ),
                vocabulary='listUserGroup',
                searchable=True,
            ),
            TextField(
                name='projetpv',
                widget=RichWidget(
                    label='Projetpv',
                    condition="python: not here.adapted().isformation()",
                    label_msgid='MeetingAndenne_label_projetpv',
                    i18n_domain='PloneMeeting',
                ),
                read_permission="PloneMeeting: Read decision",
                default_content_type="text/html",
                searchable=True,
                write_permission="PloneMeeting: Write decision",
                allowable_content_types=('text/html',),
                default_output_type="text/html"
            ),
            TextField(
                name='pv',
                widget=RichWidget(
                    label='Pv',
                    label_msgid='MeetingAndenne_label_pv',
                    i18n_domain='PloneMeeting',
                ),
                read_permission="MeetingAndenne: Read pv",
                default_content_type="text/html",
                searchable=True,
                write_permission="MeetingAndenne: Write pv",
                allowable_content_types=('text/html',),
                default_output_type="text/html"
            ),
            TextField(
                name='textpv',
                widget=RichWidget(
                    label='Textpv',
                    label_msgid='MeetingAndenne_label_textpv',
                    i18n_domain='PloneMeeting',
                ),
                read_permission="MeetingAndenne: Read pv",
                default_content_type="text/html",
                searchable=True,
                write_permission="MeetingAndenne: Write pv",
                allowable_content_types=('text/html',),
                default_output_type="text/html"
            ),
            BooleanField(
                name='isconfidential',
                widget=BooleanWidget(
                    label='IsConfidential',
                    label_msgid='MeetingAndenne_label_IsConfidential',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                default=False
            ),
            LinesField(
                name='itemPresents',
                widget=MultiSelectionWidget(
                    visible=False
                    format="checkbox",
                    label='Itempresents',
                    label_msgid='MeetingAndenne_label_itemPresents',
                    i18n_domain='PloneMeeting',
                ),
                multiValued=1,
            ),
            BooleanField(
                name='towritepv',
                widget=BooleanField._properties['widget'](
                    visible=False,
                    label='Printannexe',
                    label_msgid='Meetingandenne_label_Printannexe',
                    i18n_domain='PloneMeeting',
                ),
                write_permission="PloneMeeting: Write towritepv",
                default=True
            ),
        ),
    )

    completeItemSchema = baseSchema + specificSchema.copy()
    completeItemSchema['title'].widget.condition='python: not here.adapted().isformation()'
    completeItemSchema['decision'].widget.condition='python: not here.adapted().isformation()'
    completeItemSchema['description'].widget.condition='python: not here.adapted().isformation()'
#    completeItemSchema['proposingGroup'].default_method='getDefaultProposingGroup'
    completeItemSchema['copyGroups'].write_permission="MeetingAndenne: Write copygroup"
    completeItemSchema['description'].widget.label_method='getLabelForDescription'

    completeItemSchema.moveField('refdoc', pos='top')
    completeItemSchema.moveField('yourrefdoc', pos=2)
    completeItemSchema.moveField('treatUser', pos=8)
    completeItemSchema.moveField('projetpv', pos=25)
    completeItemSchema.moveField('pv', pos=25)
    completeItemSchema.moveField('textpv', pos=24)
    completeItemSchema.moveField('isconfidential', pos='top')

    return completeItemSchema
MeetingItem.schema = update_item_schema(MeetingItem.schema)


# Schema updates related to Meeting --------------------------------------------
def update_meeting_schema(baseSchema):
    specificSchema = Schema((

        TextField(
            name='postObservations',
            allowable_content_types=('text/html',),
            widget=RichWidget(
                condition="python: here.showObs('postObservations')",
                rows=15,
                label='Postobservations',
                label_msgid='MeetingAndenne_label_postObservations',
                i18n_domain='PloneMeeting',
            ),
            default_content_type="text/html",
            default_output_type="text/x-html-safe",
            optional=True,
        ),
    ),
    )

    completeMeetingSchema = baseSchema + specificSchema.copy()
    completeMeetingSchema.moveField('postObservations', after='observations')

    return completeMeetingSchema
Meeting.schema = update_meeting_schema(Meeting.schema)


# Schema updates related to MeetingFile ----------------------------------------
def update_file_schema(baseSchema):
#    specificSchema = Schema((
#
#            BooleanField(
#                name='toPrint',
#                widget=BooleanField._properties['widget'](
#                    label='Printannexe',
#                    label_msgid='Meetingandenne_label_Printannexe',
#                    i18n_domain='PloneMeeting',
#                ),
#                default=True
#            ),
#        ),
#    )
#
#    completeFileSchema = baseSchema + specificSchema.copy()
    completeFileSchema = baseSchema
    completeFileSchema['toPrint'].default=True

    return completeFileSchema
MeetingFile.schema = update_file_schema(MeetingFile.schema)


# Schema updates related to MeetingUser ----------------------------------------
def update_muser_schema(baseSchema):
    specificSchema = Schema((

            DateTimeField(
                name='start_date_function',
                widget=DateTimeField._properties['widget'](
                    label='start_date_function',
                    label_msgid='MeetingAndenne_label_start_date_function',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=False
            ),
            DateTimeField(
                name='end_date_function',
                widget=DateTimeField._properties['widget'](
                    label='end_date_function',
                    label_msgid='MeetingAndenne_label_end_date_function',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                required=False
            ),
        ),
    )

    completeUserSchema = baseSchema + specificSchema.copy()
    return completeUserSchema
MeetingUser.schema = update_muser_schema(MeetingUser.schema)


# Schema updates related to MeetingConfig --------------------------------------
def update_config_schema(baseSchema):
    specificSchema = Schema((

            BooleanField(
                name='initItemDecisionIfEmptyOnDecide',
                default=True,
                widget=BooleanField._properties['widget'](
                    description="InitItemDecisionIfEmptyOnDecide",
                    description_msgid="init_item_decision_if_empty_on_decide",
                    label='Inititemdecisionifemptyondecide',
                    label_msgid='MeetingAndenne_label_initItemDecisionIfEmptyOnDecide',
                    i18n_domain='PloneMeeting'),
                write_permission=WriteRiskyConfig,
            ),
        ),
    )

    completeConfigSchema = baseSchema + specificSchema.copy()
    return completeConfigSchema
MeetingConfig.schema = update_config_schema(MeetingConfig.schema)


# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses
registerClasses()