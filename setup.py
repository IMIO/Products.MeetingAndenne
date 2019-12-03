from setuptools import setup, find_packages
import os

version = '3.3.2'

setup(name='Products.MeetingAndenne',
      version=version,
      description="PloneMeeting profile for city of Andenne",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://www.imio.be/produits/gestion-des-deliberations',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
            test=['unittest2',
                  'zope.testing',
                  'plone.testing',
                  'plone.app.testing',
                  'plone.app.robotframework',
                  'Products.CMFPlacefulWorkflow',
                  'zope.testing',
                  'Products.PloneTestCase'],
            templates=['Genshi',
                  ]),
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'Pillow',
          'Products.PloneMeeting',
          'collective.dynatree'],
      entry_points={},
      )
