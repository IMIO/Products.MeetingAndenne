# -*- coding: utf-8 -*-
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import CategoryDescriptor

# College Category
collegeCategories = [
CategoryDescriptor('0100-abonnements-et-documentation-autres','100. Abonnements et documentation > Autres'),
CategoryDescriptor('0200-administration-autres','200. Administration > Autres'),
CategoryDescriptor('0210-administration-comite-de-direction','210. Administration > Comité de direction'),
CategoryDescriptor('0220-administration-controle-interne','220. Administration > Contrôle interne'),
CategoryDescriptor('0230-administration-organisation','230. Administration > Organisation'),
CategoryDescriptor('0240-administration-partenariat-provinceville','240. Administration > Partenariat  Province/Ville'),
CategoryDescriptor('0250-administration-pst','250. Administration > PST'),
CategoryDescriptor('0260-administration-rgpd','260. Administration > RGPD'),
CategoryDescriptor('0300-affaires-economiques-autres','300. Affaires économiques > Autres'),
CategoryDescriptor('0310-affaires-economiques-atelier-de-fabrication-numerique','310. Affaires économiques > Atelier de fabrication numérique'),
CategoryDescriptor('0320-affaires-economiques-cafes-et-restaurants','320. Affaires économiques > Cafés et restaurants'),
CategoryDescriptor('0330-affaires-economiques-commerce','330. Affaires économiques > Commerce'),
CategoryDescriptor('0340-affaires-economiques-emploi-et-insertion-socio-professionnelle','340. Affaires économiques > Emploi et insertion socio-professionnelle'),
CategoryDescriptor('0350-affaires-economiques-entreprises','350. Affaires économiques > Entreprises'),
CategoryDescriptor('0360-affaires-economiques-parcs-d-activites-economiques','360. Affaires économiques > Parcs d\'activités économiques'),
CategoryDescriptor('0370-affaires-economiques-port-autonome-de-namur','370. Affaires économiques > Port autonome de NAMUR'),
CategoryDescriptor('0380-affaires-economiques-promandenne','380. Affaires économiques > PromAndenne'),
CategoryDescriptor('0400-affaires-juridiques-autres','400. Affaires juridiques > Autres'),
CategoryDescriptor('0500-affaires-sociales-autres','500. Affaires sociales > Autres'),
CategoryDescriptor('0600-agriculture-et-animaux-autres','600. Agriculture et animaux > Autres'),
CategoryDescriptor('0610-agriculture-et-animaux-agriculture-urbaine','610. Agriculture et animaux > Agriculture urbaine'),
CategoryDescriptor('0620-agriculture-et-animaux-viticulture','620. Agriculture et animaux > Viticulture'),
CategoryDescriptor('0700-amenagement-du-territoire-autres','700. Aménagement du territoire > Autres'),
CategoryDescriptor('0710-amenagement-du-territoire-certificats-d-urbanisme','710. Aménagement du territoire > Certificats d\'urbanisme'),
CategoryDescriptor('0720-amenagement-du-territoire-divisions-de-biens','720. Aménagement du territoire > Divisions de biens'),
CategoryDescriptor('0730-amenagement-du-territoire-implantations','730. Aménagement du territoire > Implantations'),
CategoryDescriptor('0740-amenagement-du-territoire-permis-commerciaux','740. Aménagement du territoire > Permis commerciaux'),
CategoryDescriptor('0750-amenagement-du-territoire-permis-integres','750. Aménagement du territoire > Permis intégrés'),
CategoryDescriptor('0760-amenagement-du-territoire-permis-d-urbanisation','760. Aménagement du territoire > Permis d\'urbanisation'),
CategoryDescriptor('0770-amenagement-du-territoire-permis-d-urbanisme','770. Aménagement du territoire > Permis d\'urbanisme'),
CategoryDescriptor('0780-amenagement-du-territoire-permis-uniques','780. Aménagement du territoire > Permis uniques'),
CategoryDescriptor('0800-archives-autres','800. Archives > Autres'),
CategoryDescriptor('0900-associations-autres','900. Associations > Autres'),
CategoryDescriptor('1000-assurances-autres','1000. Assurances > Autres'),
CategoryDescriptor('1100-batiments-autres','1100. Bâtiments > Autres'),
CategoryDescriptor('1110-batiments-batiments-administration','1110. Bâtiments > Bâtiments / Administration'),
CategoryDescriptor('1120-batiments-batiments-associatif','1120. Bâtiments > Bâtiments / Associatif'),
CategoryDescriptor('1130-batiments-batiments-culte','1130. Bâtiments > Bâtiments / Culte'),
CategoryDescriptor('1140-batiments-batiments-culture','1140. Bâtiments > Bâtiments / Culture'),
CategoryDescriptor('1150-batiments-batiments-enseignement','1150. Bâtiments > Bâtiments / Enseignement'),
CategoryDescriptor('1160-batiments-batiments-salles','1160. Bâtiments > Bâtiments / Salles'),
CategoryDescriptor('1170-batiments-batiments-social','1170. Bâtiments > Bâtiments / Social'),
CategoryDescriptor('1180-batiments-batiments-sports','1180. Bâtiments > Bâtiments / Sports'),
CategoryDescriptor('1200-calamites-autres','1200. Calamités > Autres'),
CategoryDescriptor('1300-carrieres-autres','1300. Carrières > Autres'),
CategoryDescriptor('1400-cimetieres-autres','1400. Cimetières > Autres'),
CategoryDescriptor('1410-cimetieres-concessions','1410. Cimetières > Concessions'),
CategoryDescriptor('1420-cimetieres-travaux','1420. Cimetières > Travaux'),
CategoryDescriptor('1500-circulation-routiere-et-mobilite-autres','1500. Circulation routière et mobilité > Autres'),
CategoryDescriptor('1510-circulation-routiere-et-mobilite-besix-park','1510. Circulation routière et mobilité > BESIX PARK'),
CategoryDescriptor('1520-circulation-routiere-et-mobilite-plan-de-mobilite','1520. Circulation routière et mobilité > Plan de mobilité'),
CategoryDescriptor('1530-circulation-routiere-et-mobilite-rccr','1530. Circulation routière et mobilité > RCCR'),
CategoryDescriptor('1600-collectes-et-tombolas-autres','1600. Collectes et Tombolas > Autres'),
CategoryDescriptor('1700-college-et-conseil-autres','1700. Collège et Conseil > Autres'),
CategoryDescriptor('1710-college-et-conseil-college','1710. Collège et Conseil > Collège'),
CategoryDescriptor('1720-college-et-conseil-conseil','1720. Collège et Conseil > Conseil'),
CategoryDescriptor('1800-consommations-energetiques-communales-autres','1800. Consommations énergétiques communales > Autres'),
CategoryDescriptor('1810-consommations-energetiques-communales-eau','1810. Consommations énergétiques communales > Eau'),
CategoryDescriptor('1820-consommations-energetiques-communales-electricite','1820. Consommations énergétiques communales > Electricité'),
CategoryDescriptor('1830-consommations-energetiques-communales-gaz','1830. Consommations énergétiques communales > Gaz'),
CategoryDescriptor('1840-consommations-energetiques-communales-mazout-de-chauffage','1840. Consommations énergétiques communales > Mazout de chauffage'),
CategoryDescriptor('1900-cours-d-eau-autres','1900. Cours d\'eau > Autres'),
CategoryDescriptor('2000-cpas-autres','2000. CPAS > Autres'),
CategoryDescriptor('2010-cpas-comite-de-concertation','2010. CPAS > Comité de concertation'),
CategoryDescriptor('2020-cpas-financement','2020. CPAS > Financement'),
CategoryDescriptor('2030-cpas-organes','2030. CPAS > Organes'),
CategoryDescriptor('2040-cpas-tutelle','2040. CPAS > Tutelle'),
CategoryDescriptor('2100-cultes-autres','2100. Cultes > Autres'),
CategoryDescriptor('2200-culture-autres','2200. Culture > Autres'),
CategoryDescriptor('2210-culture-bibliotheque','2210. Culture > Bibliothèque'),
CategoryDescriptor('2220-culture-centre-culturel','2220. Culture > Centre culturel'),
CategoryDescriptor('2230-culture-evenements','2230. Culture > Evénements'),
CategoryDescriptor('2240-culture-musees','2240. Culture > Musées'),
CategoryDescriptor('2300-developpement-territorial-autres','2300. Développement territorial > Autres'),
CategoryDescriptor('2310-developpement-territorial-gal-et-pcdr','2310. Développement territorial > GAL et PCDR'),
CategoryDescriptor('2320-developpement-territorial-planification','2320. Développement territorial > Planification'),
CategoryDescriptor('2330-developpement-territorial-projets-specifiques','2330. Développement territorial > Projets spécifiques'),
CategoryDescriptor('2340-developpement-territorial-quartier-nouveau','2340. Développement territorial > Quartier nouveau'),
CategoryDescriptor('2350-developpement-territorial-renovation-urbaine','2350. Développement territorial > Rénovation urbaine'),
CategoryDescriptor('2360-developpement-territorial-revitalisation-urbaine-(ecoquartier)','2360. Développement territorial > Revitalisation urbaine (écoquartier)'),
CategoryDescriptor('2400-divers-autres','2400. Divers > Autres'),
CategoryDescriptor('2500-eau-autres','2500. Eau > Autres'),
CategoryDescriptor('2600-egouttage-et-epuration-autres','2600. Egouttage et épuration > Autres'),
CategoryDescriptor('2700-elections-autres','2700. Elections > Autres'),
CategoryDescriptor('2800-energies-autres','2800. Energies > Autres'),
CategoryDescriptor('2810-energies-pollec','2810. Energies > POLLEC'),
CategoryDescriptor('2900-enfance,-famille-et-jeunesse-autres','2900. Enfance, famille et jeunesse > Autres'),
CategoryDescriptor('2910-enfance,-famille-et-jeunesse-accueil-extrascolaire','2910. Enfance, famille et jeunesse > Accueil extrascolaire'),
CategoryDescriptor('2920-enfance,-famille-et-jeunesse-aires-de-jeux','2920. Enfance, famille et jeunesse > Aires de jeux'),
CategoryDescriptor('2930-enfance,-famille-et-jeunesse-creches-mcae','2930. Enfance, famille et jeunesse > Crèches - MCAE'),
CategoryDescriptor('2940-enfance,-famille-et-jeunesse-gardiennes-encadrees','2940. Enfance, famille et jeunesse > Gardiennes encadrées'),
CategoryDescriptor('2950-enfance,-famille-et-jeunesse-maison-des-jeunes-le-hangar','2950. Enfance, famille et jeunesse > Maison des Jeunes "Le Hangar"'),
CategoryDescriptor('2960-enfance,-famille-et-jeunesse-plaines-de-vacances','2960. Enfance, famille et jeunesse > Plaines de vacances'),
CategoryDescriptor('3000-enseignement-autres','3000. Enseignement > Autres'),
CategoryDescriptor('3010-enseignement-enseignement-fondamental-communal','3010. Enseignement > Enseignement fondamental communal'),
CategoryDescriptor('3020-enseignement-enseignement-promotion-sociale','3020. Enseignement > Enseignement promotion sociale'),
CategoryDescriptor('3100-environnement-autres','3100. Environnement > Autres'),
CategoryDescriptor('3110-environnement-depots-de-dechets','3110. Environnement > Dépôts de déchets'),
CategoryDescriptor('3120-environnement-permis-d-exploiter','3120. Environnement > Permis d\'exploiter'),
CategoryDescriptor('3200-festivites-autres','3200. Festivités > Autres'),
CategoryDescriptor('3210-festivites-affichage-evenementiel','3210. Festivités > Affichage événementiel'),
CategoryDescriptor('3220-festivites-brocantes','3220. Festivités > Brocantes'),
CategoryDescriptor('3230-festivites-debits-occasionnels','3230. Festivités > Débits occasionnels'),
CategoryDescriptor('3240-festivites-evenements','3240. Festivités > Evénements'),
CategoryDescriptor('3250-festivites-pret-de-materiel','3250. Festivités > Prêt de matériel'),
CategoryDescriptor('3300-finances-autres','3300. Finances > Autres'),
CategoryDescriptor('3310-finances-budget-et-compte','3310. Finances > Budget et compte'),
CategoryDescriptor('3320-finances-fiscalite','3320. Finances > Fiscalité'),
CategoryDescriptor('3330-finances-f.o.v.','3330. Finances > F.O.V.'),
CategoryDescriptor('3340-finances-subventions','3340. Finances > Subventions'),
CategoryDescriptor('3400-impetrants-de-voirie-autres','3400. Impétrants de voirie > Autres'),
CategoryDescriptor('3410-impetrants-de-voirie-eau','3410. Impétrants de voirie > Eau'),
CategoryDescriptor('3420-impetrants-de-voirie-eclairage-public','3420. Impétrants de voirie > Eclairage public'),
CategoryDescriptor('3430-impetrants-de-voirie-electricite','3430. Impétrants de voirie > Electricité'),
CategoryDescriptor('3440-impetrants-de-voirie-gaz','3440. Impétrants de voirie > Gaz'),
CategoryDescriptor('3450-impetrants-de-voirie-telecommunications','3450. Impétrants de voirie > Télécommunications'),
CategoryDescriptor('3460-impetrants-de-voirie-teledistribution','3460. Impétrants de voirie > Télédistribution'),
CategoryDescriptor('3500-informatique-et-nouvelles-technologies-autres','3500. Informatique et nouvelles technologies > Autres'),
CategoryDescriptor('3600-intercommunales-autres','3600. Intercommunales > Autres'),
CategoryDescriptor('3700-logement-autres','3700. Logement > Autres'),
CategoryDescriptor('3710-logement-agence-immobiliere-sociale','3710. Logement > Agence immobilière sociale'),
CategoryDescriptor('3720-logement-les-logis-andennais','3720. Logement > Les Logis Andennais'),
CategoryDescriptor('3730-logement-permis-de-location','3730. Logement > Permis de location'),
CategoryDescriptor('3800-loisirs-autres','3800. Loisirs > Autres'),
CategoryDescriptor('3810-loisirs-marches-et-assimiles','3810. Loisirs > Marches et assimilés'),
CategoryDescriptor('3900-marches-publics-autres','3900. Marchés publics > Autres'),
CategoryDescriptor('3910-marches-publics-centrale','3910. Marchés publics > Centrale'),
CategoryDescriptor('3920-marches-publics-fournitures','3920. Marchés publics > Fournitures'),
CategoryDescriptor('3930-marches-publics-in-house','3930. Marchés publics > In House'),
CategoryDescriptor('3940-marches-publics-services','3940. Marchés publics > Services'),
CategoryDescriptor('3950-marches-publics-travaux','3950. Marchés publics > Travaux'),
CategoryDescriptor('4000-materiels-autres','4000. Matériels > Autres'),
CategoryDescriptor('4010-materiels-equipements-de-bureau','4010. Matériels > Equipements de bureau'),
CategoryDescriptor('4020-materiels-equipements-techniques','4020. Matériels > Equipements techniques'),
CategoryDescriptor('4030-materiels-materiel-roulant','4030. Matériels > Matériel roulant'),
CategoryDescriptor('4040-materiels-mobilier-urbain','4040. Matériels > Mobilier urbain'),
CategoryDescriptor('4050-materiels-pret-de-materiel','4050. Matériels > Prêt de matériel'),
CategoryDescriptor('4100-parcs-et-plantations-autres','4100. Parcs et plantations > Autres'),
CategoryDescriptor('4200-patrimoine-autres','4200. Patrimoine > Autres'),
CategoryDescriptor('4210-patrimoine-atlas','4210. Patrimoine > Atlas'),
CategoryDescriptor('4220-patrimoine-baux','4220. Patrimoine > Baux'),
CategoryDescriptor('4230-patrimoine-contentieux','4230. Patrimoine > Contentieux'),
CategoryDescriptor('4240-patrimoine-immobilier','4240. Patrimoine > Immobilier'),
CategoryDescriptor('4250-patrimoine-occupations-precaires','4250. Patrimoine > Occupations précaires'),
CategoryDescriptor('4300-personnel-autres','4300. Personnel > Autres'),
CategoryDescriptor('4310-personnel-accidents-de-travail','4310. Personnel > Accidents de travail'),
CategoryDescriptor('4320-personnel-enseignants-eic','4320. Personnel > Enseignants - EIC'),
CategoryDescriptor('4330-personnel-enseignants-fondamental','4330. Personnel > Enseignants - Fondamental'),
CategoryDescriptor('4340-personnel-evaluations','4340. Personnel > Evaluations'),
CategoryDescriptor('4350-personnel-grades-legaux','4350. Personnel > Grades légaux'),
CategoryDescriptor('4360-personnel-missions-de-service','4360. Personnel > Missions de service'),
CategoryDescriptor('4370-personnel-stages','4370. Personnel > Stages'),
CategoryDescriptor('4400-population-etat-civil-autres','4400. Population - Etat civil > Autres'),
CategoryDescriptor('4410-population-etat-civil-communication-d-informations','4410. Population - Etat civil > Communication d\'informations'),
CategoryDescriptor('4420-population-etat-civil-inscriptions','4420. Population - Etat civil > Inscriptions'),
CategoryDescriptor('4430-population-etat-civil-radiations','4430. Population - Etat civil > Radiations'),
CategoryDescriptor('4500-poste-et-telecommunications-autres','4500. Poste et Télécommunications > Autres'),
CategoryDescriptor('4510-poste-et-telecommunications-desserte-internet','4510. Poste et Télécommunications > Desserte Internet'),
CategoryDescriptor('4520-poste-et-telecommunications-services-postaux','4520. Poste et Télécommunications > Services postaux'),
CategoryDescriptor('4530-poste-et-telecommunications-telephonie-mobile-et-fixe','4530. Poste et Télécommunications > Téléphonie mobile et fixe'),
CategoryDescriptor('4600-relations-internationales-autres','4600. Relations internationales > Autres'),
CategoryDescriptor('4700-relations-publiques-autres','4700. Relations publiques > Autres'),
CategoryDescriptor('4710-relations-publiques-ceremonies-et-receptions','4710. Relations publiques > Cérémonies et réceptions'),
CategoryDescriptor('4720-relations-publiques-evenements','4720. Relations publiques > Evénements'),
CategoryDescriptor('4730-relations-publiques-site-internet-communal','4730. Relations publiques > Site Internet communal'),
CategoryDescriptor('4800-salles-et-assimiles-autres','4800. Salles et assimilés > Autres'),
CategoryDescriptor('4810-salles-et-assimiles-maison-des-associations','4810. Salles et assimilés > Maison des Associations'),
CategoryDescriptor('4820-salles-et-assimiles-salles-communales','4820. Salles et assimilés > Salles communales'),
CategoryDescriptor('4830-salles-et-assimiles-salle-polyvalente','4830. Salles et assimilés > Salle polyvalente'),
CategoryDescriptor('4840-salles-et-assimiles-refectoires-scolaires','4840. Salles et assimilés > Réfectoires scolaires'),
CategoryDescriptor('4900-sante-publique-autres','4900. Santé publique > Autres'),
CategoryDescriptor('5000-securite-publique-autres','5000. Sécurité publique > Autres'),
CategoryDescriptor('5010-securite-publique-plan-de-prevention-et-de-securite','5010. Sécurité publique > Plan de prévention et de sécurité'),
CategoryDescriptor('5020-securite-publique-planification-d-urgence','5020. Sécurité publique > Planification d\'urgence'),
CategoryDescriptor('5030-securite-publique-prison','5030. Sécurité publique > Prison'),
CategoryDescriptor('5040-securite-publique-prevention-des-incendies','5040. Sécurité publique > Prévention des incendies'),
CategoryDescriptor('5050-securite-publique-zone-de-police','5050. Sécurité publique > Zone de Police'),
CategoryDescriptor('5100-seniors-autres','5100. Seniors > Autres'),
CategoryDescriptor('5200-services-de-secours-autres','5200. Services de secours > Autres'),
CategoryDescriptor('5210-services-de-secours-zone-de-secours-nage','5210. Services de secours > Zone de secours NAGE'),
CategoryDescriptor('5300-sports-autres','5300. Sports > Autres'),
CategoryDescriptor('5310-sports-evenements','5310. Sports > Evénements'),
CategoryDescriptor('5320-sports-installations-sportives','5320. Sports > Installations sportives'),
CategoryDescriptor('5330-sports-regie-des-sports','5330. Sports > Régie des Sports'),
CategoryDescriptor('5400-tourisme-autres','5400. Tourisme > Autres'),
CategoryDescriptor('5410-tourisme-activites','5410. Tourisme > Activités'),
CategoryDescriptor('5420-tourisme-hebergements','5420. Tourisme > Hébergements'),
CategoryDescriptor('5430-tourisme-promotion','5430. Tourisme > Promotion'),
CategoryDescriptor('5500-transports-en-commun-autres','5500. Transports en commun > Autres'),
CategoryDescriptor('5510-transports-en-commun-bus','5510. Transports en commun > Bus'),
CategoryDescriptor('5520-transports-en-commun-trains','5520. Transports en commun > Trains'),
CategoryDescriptor('5600-travaux-autres','5600. Travaux > Autres'),
CategoryDescriptor('5700-voiries-autres','5700. Voiries > Autres'),
CategoryDescriptor('5710-voiries-communales','5710. Voiries > Communales'),
CategoryDescriptor('5720-voiries-regionales','5720. Voiries > Régionales'),
CategoryDescriptor('5730-voiries-denominations','5730. Voiries > Dénominations')
]

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
agendaRccTemplate = PodTemplateDescriptor('agenda', 'Rapport du Col. au Con.')
agendaRccTemplate.podTemplate = 'MeetingAndenneRccRapport.odt'
agendaRccTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                              'here.portal_plonemeeting.isManager(here)'

itemRccTemplate = PodTemplateDescriptor('item', 'Aperçu')
itemRccTemplate.podTemplate = 'MeetingItemAndenneRccApercu.odt'
itemRccTemplate.podCondition = 'python:here.meta_type=="MeetingItem"'

rapColAuConTemplates = [ agendaRccTemplate, itemRccTemplate ]

# Users and groups -------------------------------------------------------------
groups = ()

# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = MeetingConfigDescriptor(
    'meeting-config-college', 'College Communal',
    'College communal', isDefault = True)

collegeMeeting.podTemplates = collegeTemplates
collegeMeeting.categories = collegeCategories

# rapcolaucon
rapcolauconMeeting = MeetingConfigDescriptor(
    'rapport-col-au-con', 'Rapport Col. au Con.',
    'Rapport Col. au Con.' )

rapcolauconMeeting.podTemplates = rapColAuConTemplates

# ------------------------------------------------------------------------------
data = PloneMeetingConfiguration('Mes séances',
                                 (collegeMeeting, rapcolauconMeeting),
                                 groups)