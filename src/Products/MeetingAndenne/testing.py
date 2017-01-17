# -*- coding: utf-8 -*-
from plone.testing import z2, zca
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
from Products.PloneMeeting.testing import PloneMeetingLayer
import Products.MeetingAndenne
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE

MA_ZCML = zca.ZCMLSandbox(filename="testing.zcml",
                          package=Products.MeetingAndenne,
                          name='MA_ZCML')

MA_Z2 = z2.IntegrationTesting(bases=(z2.STARTUP, MC_ZCML),
                              name='MA_Z2')

MA_TESTING_PROFILE = PloneMeetingLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingAndenne,
    additional_z2_products=('Products.MeetingAndenne',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow',
                            'Products.PasswordStrength'),
    gs_profile_id='Products.MeetingAndenne:testing',
    name="MA_TESTING_PROFILE")

MA_TESTING_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(MA_TESTING_PROFILE,), name="MA_TESTING_PROFILE_FUNCTIONAL")

MA_EXAMPLES_FR_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=Products.MeetingAndenne,
    additional_z2_products=('Products.MeetingAndenne',
                            'Products.PloneMeeting',
                            'Products.CMFPlacefulWorkflow'),
    gs_profile_id='Products.MeetingAndenne:examples_fr',
    name="MA_TESTING_PROFILE")

MA_TESTING_ROBOT = FunctionalTesting(
    bases=(
        MA_EXAMPLES_FR_TESTING_PROFILE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="MA_TESTING_ROBOT",
)
