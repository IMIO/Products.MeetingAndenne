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
from Products.PloneMeeting.MeetingFileType import MeetingFileType
from Products.PloneMeeting.MeetingGroup import MeetingGroup
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.MeetingUser import MeetingUser
from Products.MeetingAndenne.vocabularies import SubCategoriesVocabulary
from collective.dynatree.atwidget import DynatreeWidget


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
            StringField(
                name='treatUser',
                default_method="Creator",
                widget=SelectionWidget(
                    format="select",
                    label='Treatuser',
                    label_msgid='MeetingAndenne_label_treatUser',
                    i18n_domain='PloneMeeting',
                ),
                vocabulary='listTreatUsers',
                searchable=True,
            ),
            TextField(
                name='projetpv',
                widget=RichWidget(
                    rows=15,
                    label='Projetpv',
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
                    rows=15,
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
                    rows=15,
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
                    label_msgid='MeetingAndenne_label_isConfidential',
                    i18n_domain='PloneMeeting',
                ),
                searchable=True,
                default=False
            ),
            LinesField(
                name='itemPresents',
                widget=MultiSelectionWidget(
                    visible=False,
                    format="checkbox",
                    label='Itempresents',
                    label_msgid='MeetingAndenne_label_itemPresents',
                    i18n_domain='PloneMeeting',
                ),
                multiValued=1,
            ),
        ),
    )

    completeItemSchema = baseSchema + specificSchema.copy()
    completeItemSchema['title'].widget.condition="python: not hasattr(here, 'template') or not here.queryState()=='itemcreated' or here.portal_membership.getAuthenticatedMember().has_role('Manager')"    

    completeItemSchema['copyGroups'].write_permission="MeetingAndenne: Write copygroup"
    completeItemSchema['description'].widget.label_method='getLabelForDescription'
    completeItemSchema['budgetInfos'].widget.rows=12
    completeItemSchema['itemSignatories'].optional=True
    completeItemSchema['proposingGroup'].default_method="getDefaultProposingGroup"


    completeItemSchema['category'].widget=DynatreeWidget(
            condition="python: here.showCategory()",
            description="Category",
            description_msgid="item_category_descr",
            label='Category',
            label_msgid='PloneMeeting_label_category',
            i18n_domain='PloneMeeting',
            leafsOnly=True,
            rootVisible=True,
            selectMode=1,
            sparse=False,
        )
    completeItemSchema['category'].vocabulary=SubCategoriesVocabulary()


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

    return completeFileSchema
MeetingFile.schema = update_file_schema(MeetingFile.schema)


# Schema updates related to MeetingFileType ----------------------------------------
def update_filetype_schema(baseSchema):
#    specificSchema = Schema((
#
#            StringField(
#                name='relatedTo',
#                default='item',
#                widget=SelectionWidget(
#                    description_msgid="related_to_descr",
#                    description="RelatedTo",
#                    label='Relatedto',
#                    label_msgid='PloneMeeting_label_relatedTo',
#                    i18n_domain='PloneMeeting',
#                ),
#                enforceVocabulary=True,
#                write_permission="PloneMeeting: Write risky config",
#                vocabulary='listRelatedTo',
#            ),
#        ),
#    )
#
#    completeFileSchema = baseSchema + specificSchema.copy()
    completeFileTypeSchema = baseSchema

    return completeFileTypeSchema
MeetingFileType.schema = update_filetype_schema(MeetingFileType.schema)


# Schema updates related to MeetingGroup ---------------------------------------
def update_group_schema(baseSchema):
    specificSchema = Schema((

            BooleanField(
                name='usePrevalidation',
                widget=BooleanField._properties['widget'](
                    label='Useprevalidation',
                    label_msgid='MeetingAndenne_label_usePrevalidation',
                    i18n_domain='PloneMeeting',
                ),
                default=False
            ),
        ),
    )

    completeGroupSchema = baseSchema + specificSchema.copy()

    return completeGroupSchema
MeetingGroup.schema = update_group_schema(MeetingGroup.schema)


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
                name='useSubCategories',
                default=False,
                widget=BooleanField._properties['widget'](
                    description="UseSubCategories",
                    description_msgid="use_sub_categories_descr",
                    label='Usesubcategories',
                    label_msgid='MeetingAndenne_label_useSubCategories',
                    i18n_domain='PloneMeeting'),
                write_permission=WriteRiskyConfig,
            ),
            LinesField(
                name='selectableAssociatedGroups',
                widget=MultiSelectionWidget(
                    size=20,
                    description="SelectableAssociatedGroups",
                    description_msgid="selectable_associated_groups_descr",
                    label='Selectableassociatedgroups',
                    label_msgid='MeetingAndenne_label_selectableAssociatedGroups',
                    i18n_domain='PloneMeeting',
                ),
                schemata="advices",
                multiValued=1,
                vocabulary='listSelectableAssociatedGroups',
                enforceVocabulary=True,
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