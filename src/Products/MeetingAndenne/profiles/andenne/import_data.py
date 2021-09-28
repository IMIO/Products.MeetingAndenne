# -*- coding: utf-8 -*-

import sys

from DateTime import DateTime
from Products.PloneMeeting.profiles import CategoryDescriptor
from Products.PloneMeeting.profiles import GroupDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.profiles import MeetingUserDescriptor
from Products.PloneMeeting.profiles import PloneGroupDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import PodTemplateDescriptor
#from Products.PloneMeeting.profiles import RecurringItemDescriptor
from Products.PloneMeeting.profiles import UserDescriptor

today = DateTime().strftime('%Y/%m/%d')


# File types -------------------------------------------------------------------
annexe = MeetingFileTypeDescriptor('annexe', 'Annexe', 'attach.png', '')
annexeCahier = MeetingFileTypeDescriptor('annexeCahier', 'Cahier des Charges', 'cahier.gif', '')
annexeDecision = MeetingFileTypeDescriptor('annexeDecision', 'Annexe à la décision', 'attach.png',
                                           '', 'item_decision')
annexeAvis = MeetingFileTypeDescriptor('annexeAvis', 'Annexe à un avis',
                                       'attach.png', '', 'advice')
annexeAvisLegal = MeetingFileTypeDescriptor('annexeAvisLegal', 'Extrait article de loi',
                                            'legalAdvice.png', '', 'advice')
annexeNoteExecution = MeetingFileTypeDescriptor('noteExecution', 'Note d\'exécution signée',
                                                'executionNote.png', '', 'item_pv')
annexeDeliberation = MeetingFileTypeDescriptor('deliberation', 'Délibération signée',
                                                'executionNote.png', '', 'item_pv')


# Pod templates ----------------------------------------------------------------

# College Pod templates --------------------------------------------------------
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

# Conseil Pod templates --------------------------------------------------------
agendaListCouncilTemplate = PodTemplateDescriptor('agendaList', 'O.J.')
agendaListCouncilTemplate.podTemplate = 'MeetingAndenneListCouncil.odt'
agendaListCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                            'here.portal_plonemeeting.isManager(here)'

lateAgendaListCouncilTemplate = PodTemplateDescriptor('lateAgendaList', 'O.J. Comp.')
lateAgendaListCouncilTemplate.podTemplate = 'MeetingAndenneListCouncilLate.odt'
lateAgendaListCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                                'here.portal_plonemeeting.isManager(here)'

coordinatedAgendaListCouncilTemplate = PodTemplateDescriptor('coordinatedAgendaList', 'O.J. Coord.')
coordinatedAgendaListCouncilTemplate.podTemplate = 'MeetingAndenneListCouncilCoordinated.odt'
coordinatedAgendaListCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                                    'here.portal_plonemeeting.isManager(here)'

publicAgendaCouncilTemplate = PodTemplateDescriptor('publicAgenda', 'N.S. publiques')
publicAgendaCouncilTemplate.podTemplate = 'MeetingAndenneCouncilPublic.odt'
publicAgendaCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                        'here.portal_plonemeeting.isManager(here)'

secretAgendaCouncilTemplate = PodTemplateDescriptor('secretAgenda', 'N.S. huis clos')
secretAgendaCouncilTemplate.podTemplate = 'MeetingAndenneCouncilPrivate.odt'
secretAgendaCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                        'here.portal_plonemeeting.isManager(here)'

latePublicAgendaCouncilTemplate = PodTemplateDescriptor('latePublicAgenda', 'N.S. publiques comp.')
latePublicAgendaCouncilTemplate.podTemplate = 'MeetingAndenneCouncilLatePublic.odt'
latePublicAgendaCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                        'here.portal_plonemeeting.isManager(here)'

lateSecretAgendaCouncilTemplate = PodTemplateDescriptor('lateSecretAgenda', 'N.S. huis clos comp.')
lateSecretAgendaCouncilTemplate.podTemplate = 'MeetingAndenneCouncilLatePrivate.odt'
lateSecretAgendaCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                        'here.portal_plonemeeting.isManager(here)'

decisionCouncilTemplate = PodTemplateDescriptor('pv', 'P.V.')
decisionCouncilTemplate.podTemplate = 'MeetingAndenneCouncilPV.odt'
decisionCouncilTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                        'here.portal_plonemeeting.isManager(here) and ' \
                                        'here.queryState() in [\'decided\', \'closed\']'

itemCouncilExecutiveSummaryTemplate = PodTemplateDescriptor('item', 'Note de synthèse')
itemCouncilExecutiveSummaryTemplate.podTemplate = 'MeetingItemAndenneCouncilNS.odt'
itemCouncilExecutiveSummaryTemplate.podCondition = 'python:here.meta_type=="MeetingItem"'

itemCouncilDeliberationTemplate = PodTemplateDescriptor('itemDeliberation', 'Délibération')
itemCouncilDeliberationTemplate.podTemplate = 'MeetingItemAndenneCouncilDeliberation.odt'
itemCouncilDeliberationTemplate.podCondition = 'python:here.meta_type=="MeetingItem" and here.queryState() not in ("itemcreated", ' \
                                            '"proposed", "prevalidated", "validated", "presented", "itemfrozen")'

itemCouncilExecutionTemplate = PodTemplateDescriptor('itemExecution', 'Note d\'exécution')
itemCouncilExecutionTemplate.podTemplate = 'MeetingItemAndenneCouncilExecution.odt'
itemCouncilExecutionTemplate.podCondition = 'python:here.meta_type=="MeetingItem" and here.queryState() not in ("itemcreated", ' \
                                        '"proposed", "prevalidated", "validated", "presented", "itemfrozen")'

councilTemplates = [ agendaListCouncilTemplate, lateAgendaListCouncilTemplate, coordinatedAgendaListCouncilTemplate,
                     publicAgendaCouncilTemplate, secretAgendaCouncilTemplate, latePublicAgendaCouncilTemplate,
                     lateSecretAgendaCouncilTemplate, decisionCouncilTemplate, itemCouncilExecutiveSummaryTemplate,
                     itemCouncilDeliberationTemplate, itemCouncilExecutionTemplate ]

# RapColAuCon Pod templates ----------------------------------------------------
agendaRccTemplate = PodTemplateDescriptor('agenda', 'Rapport du Col. au Con.')
agendaRccTemplate.podTemplate = 'MeetingAndenneRccRapport.odt'
agendaRccTemplate.podCondition = 'python:(here.meta_type=="Meeting") and ' \
                                    'here.portal_plonemeeting.isManager(here)'

itemRccTemplate = PodTemplateDescriptor('item', 'Aperçu')
itemRccTemplate.podTemplate = 'MeetingItemAndenneRccApercu.odt'
itemRccTemplate.podCondition = 'python:here.meta_type=="MeetingItem"'

rapColAuConTemplates = [ agendaRccTemplate, itemRccTemplate ]


# Categories -------------------------------------------------------------------

# College Categories -----------------------------------------------------------
collegeCategories = [
    CategoryDescriptor('1-abonnements-et-documentation', '1. Abonnements et documentation'),
    CategoryDescriptor('2-accueil-extrascolaire', '2. Accueil extrascolaire'),
    CategoryDescriptor('3-administration', '3. Administration'),
    CategoryDescriptor('4-affaires-economiques', '4. Affaires économiques'),
    CategoryDescriptor('5-affaires-juridiques-et-patrimoine', '5. Affaires juridiques et patrimoniales'),
    CategoryDescriptor('6-affaires-sociales', '6. Affaires sociales'),
    CategoryDescriptor('7-agriculture-et-animaux', '7. Agriculture et animaux'),
    CategoryDescriptor('8-amenagement-du-territoire', '8. Aménagement du territoire'),
    CategoryDescriptor('9-archives', '9. Archives'),
    CategoryDescriptor('10-associations', '10. Associations'),
    CategoryDescriptor('11-assurances', '11. Assurances'),
    CategoryDescriptor('12-batiments-du-culte', '12. Bâtiments du culte'),
    CategoryDescriptor('13-batiments-scolaires', '13. Bâtiments scolaires'),
    CategoryDescriptor('14-autres-batiments', '14. Autres bâtiments'),
    CategoryDescriptor('15-calamites', '15. Calamités'),
    CategoryDescriptor('16-ceremonies-et-receptions', '16. Cérémonies et Réceptions'),
    CategoryDescriptor('17-cimetieres', '17. Cimetières'),
    CategoryDescriptor('18-circulation-et-securite-routieres', '18. Circulation routière et mobilité'),
    CategoryDescriptor('19-collectes-et-tombolas', '19. Collectes et tombolas'),
    CategoryDescriptor('20-college-et-conseil', '20. Collège et Conseil'),
    CategoryDescriptor('21-cours-deau', "21. Cours d'eau"),
    CategoryDescriptor('22-culte', '22. Culte'),
    CategoryDescriptor('23-culture-et-loisirs-non-sportifs', '23. Culture et Loisirs non sportifs'),
    CategoryDescriptor('24-debits-de-boissons', '24. Débits de boissons'),
    CategoryDescriptor('25-developpement-territorial', '25. Développement territorial'),
    CategoryDescriptor('26-divers', '26. Divers'),
    CategoryDescriptor('27-eau', '27. Eau'),
    CategoryDescriptor('28-egouttage-et-epuration', '28. Egouttage et Epuration'),
    CategoryDescriptor('29-elections', '29. Elections'),
    CategoryDescriptor('30-electricite', '30. Electricité'),
    CategoryDescriptor('31-energie', '31. Energie'),
    CategoryDescriptor('32-enfance-famille-et-jeunesse', '32. Enfance, Famille et Jeunesse'),
    CategoryDescriptor('33-enseignement', '33. Enseignement'),
    CategoryDescriptor('34-environnement-et-carrieres', '34. Environnement et carrières'),
    CategoryDescriptor('35-equipements-techniques', '35. Equipements techniques'),
    CategoryDescriptor('36-etat-civil-et-population', '36. Etat civil et Population'),
    CategoryDescriptor('37-finances', '37. Finances'),
    CategoryDescriptor('38-gaz', '38. Gaz'),
    CategoryDescriptor('39-informatique-et-nouvelles-technologies', '39. Informatique et Nouvelles technologies'),
    CategoryDescriptor('40-installations-sportives', '40. Installations sportives'),
    CategoryDescriptor('41-intercommunales', '41. Intercommunales'),
    CategoryDescriptor('42-logement', '42. Logement'),
    CategoryDescriptor('43-marches-publics', '43. Marchés publics'),
    CategoryDescriptor('44-parcs-et-plantations', '44. Parcs et Plantations'),
    CategoryDescriptor('45-personnel', '45. Personnel'),
    CategoryDescriptor('46-port-autonome', '46. Port autonome'),
    CategoryDescriptor('47-prison', '47. Prison'),
    CategoryDescriptor('48-regies', '48. Régies'),
    CategoryDescriptor('49-relations-internationales', '49. Relations internationales'),
    CategoryDescriptor('50-relations-publiques', '50. Relations publiques'),
    CategoryDescriptor('51-salles', '51. Salles'),
    CategoryDescriptor('53-securite-publique', '53. Sécurité publique'),
    CategoryDescriptor('52-sante-publique', '52. Santé publique'),
    CategoryDescriptor('54-sports', '54. Sports'),
    CategoryDescriptor('55-telecommunications', '55. Télécom.'),
    CategoryDescriptor('56-teledistributions', '56. Télédistribution'),
    CategoryDescriptor('57-tourisme', '57. Tourisme'),
    CategoryDescriptor('58-transports-en-commun', '58. Transports en commun'),
    CategoryDescriptor('59-travaux', '59. Travaux'),
    CategoryDescriptor('60-troisieme-age', '60. Troisième âge'),
    CategoryDescriptor('61-vehicules', '61. Véhicules'),
    CategoryDescriptor('62-voiries-et-dependances', '62. Voiries et dépendances'),
    CategoryDescriptor('63-centre-ville-revitalisation', '63. Centre-Ville - Revitalisation'),
    CategoryDescriptor('64-cpas', '64. Cpas'),
    CategoryDescriptor('65-nage', '65. Zone de secours NAGE'),
    CategoryDescriptor('0100-abonnements-et-documentation-autres', '100. Abonnements et documentation > Autres'),
    CategoryDescriptor('0200-administration-autres', '200. Administration > Autres'),
    CategoryDescriptor('0210-administration-comite-de-direction', '210. Administration > Comité de direction'),
    CategoryDescriptor('0220-administration-controle-interne', '220. Administration > Contrôle interne'),
    CategoryDescriptor('0230-administration-organisation', '230. Administration > Organisation'),
    CategoryDescriptor('0240-administration-partenariat-provinceville', '240. Administration > Partenariat  Province/Ville'),
    CategoryDescriptor('0250-administration-pst', '250. Administration > PST'),
    CategoryDescriptor('0260-administration-rgpd', '260. Administration > RGPD'),
    CategoryDescriptor('0300-affaires-economiques-autres', '300. Affaires économiques > Autres'),
    CategoryDescriptor('0310-affaires-economiques-atelier-de-fabrication-numerique', '310. Affaires économiques > Atelier de fabrication numérique'),
    CategoryDescriptor('0320-affaires-economiques-cafes-et-restaurants', '320. Affaires économiques > Cafés et restaurants'),
    CategoryDescriptor('0330-affaires-economiques-commerce', '330. Affaires économiques > Commerce'),
    CategoryDescriptor('0340-affaires-economiques-emploi-et-insertion-socio-professionnelle', '340. Affaires économiques > Emploi et insertion socio-professionnelle'),
    CategoryDescriptor('0350-affaires-economiques-entreprises', '350. Affaires économiques > Entreprises'),
    CategoryDescriptor('0360-affaires-economiques-parcs-d-activites-economiques', "360. Affaires économiques > Parcs d'activités économiques"),
    CategoryDescriptor('0370-affaires-economiques-port-autonome-de-namur', '370. Affaires économiques > Port autonome de NAMUR'),
    CategoryDescriptor('0380-affaires-economiques-promandenne', '380. Affaires économiques > PromAndenne'),
    CategoryDescriptor('0400-affaires-juridiques-autres', '400. Affaires juridiques > Autres'),
    CategoryDescriptor('0500-affaires-sociales-autres', '500. Affaires sociales > Autres'),
    CategoryDescriptor('0600-agriculture-et-animaux-autres', '600. Agriculture et animaux > Autres'),
    CategoryDescriptor('0610-agriculture-et-animaux-agriculture-urbaine', '610. Agriculture et animaux > Agriculture urbaine'),
    CategoryDescriptor('0620-agriculture-et-animaux-viticulture', '620. Agriculture et animaux > Viticulture'),
    CategoryDescriptor('0700-amenagement-du-territoire-autres', '700. Aménagement du territoire > Autres'),
    CategoryDescriptor('0710-amenagement-du-territoire-certificats-d-urbanisme', "710. Aménagement du territoire > Certificats d'urbanisme"),
    CategoryDescriptor('0720-amenagement-du-territoire-divisions-de-biens', '720. Aménagement du territoire > Divisions de biens'),
    CategoryDescriptor('0730-amenagement-du-territoire-implantations', '730. Aménagement du territoire > Implantations'),
    CategoryDescriptor('0740-amenagement-du-territoire-permis-commerciaux', '740. Aménagement du territoire > Permis commerciaux'),
    CategoryDescriptor('0750-amenagement-du-territoire-permis-integres', '750. Aménagement du territoire > Permis intégrés'),
    CategoryDescriptor('0760-amenagement-du-territoire-permis-d-urbanisation', "760. Aménagement du territoire > Permis d'urbanisation"),
    CategoryDescriptor('0770-amenagement-du-territoire-permis-d-urbanisme', "770. Aménagement du territoire > Permis d'urbanisme"),
    CategoryDescriptor('0780-amenagement-du-territoire-permis-uniques', '780. Aménagement du territoire > Permis uniques'),
    CategoryDescriptor('0800-archives-autres', '800. Archives > Autres'),
    CategoryDescriptor('0900-associations-autres', '900. Associations > Autres'),
    CategoryDescriptor('1000-assurances-autres', '1000. Assurances > Autres'),
    CategoryDescriptor('1100-batiments-autres', '1100. Bâtiments > Autres'),
    CategoryDescriptor('1110-batiments-batiments-administration', '1110. Bâtiments > Bâtiments / Administration'),
    CategoryDescriptor('1120-batiments-batiments-associatif', '1120. Bâtiments > Bâtiments / Associatif'),
    CategoryDescriptor('1130-batiments-batiments-culte', '1130. Bâtiments > Bâtiments / Culte'),
    CategoryDescriptor('1140-batiments-batiments-culture', '1140. Bâtiments > Bâtiments / Culture'),
    CategoryDescriptor('1150-batiments-batiments-enseignement', '1150. Bâtiments > Bâtiments / Enseignement'),
    CategoryDescriptor('1160-batiments-batiments-salles', '1160. Bâtiments > Bâtiments / Salles'),
    CategoryDescriptor('1170-batiments-batiments-social', '1170. Bâtiments > Bâtiments / Social'),
    CategoryDescriptor('1180-batiments-batiments-sports', '1180. Bâtiments > Bâtiments / Sports'),
    CategoryDescriptor('1200-calamites-autres', '1200. Calamités > Autres'),
    CategoryDescriptor('1300-carrieres-autres', '1300. Carrières > Autres'),
    CategoryDescriptor('1400-cimetieres-autres', '1400. Cimetières > Autres'),
    CategoryDescriptor('1410-cimetieres-concessions', '1410. Cimetières > Concessions'),
    CategoryDescriptor('1420-cimetieres-travaux', '1420. Cimetières > Travaux'),
    CategoryDescriptor('1500-circulation-routiere-et-mobilite-autres', '1500. Circulation routière et mobilité > Autres'),
    CategoryDescriptor('1510-circulation-routiere-et-mobilite-besix-park', '1510. Circulation routière et mobilité > BESIX PARK'),
    CategoryDescriptor('1520-circulation-routiere-et-mobilite-plan-de-mobilite', '1520. Circulation routière et mobilité > Plan de mobilité'),
    CategoryDescriptor('1530-circulation-routiere-et-mobilite-rccr', '1530. Circulation routière et mobilité > RCCR'),
    CategoryDescriptor('1600-collectes-et-tombolas-autres', '1600. Collectes et Tombolas > Autres'),
    CategoryDescriptor('1700-college-et-conseil-autres', '1700. Collège et Conseil > Autres'),
    CategoryDescriptor('1710-college-et-conseil-college', '1710. Collège et Conseil > Collège'),
    CategoryDescriptor('1720-college-et-conseil-conseil', '1720. Collège et Conseil > Conseil'),
    CategoryDescriptor('1800-consommations-energetiques-communales-autres', '1800. Consommations énergétiques communales > Autres'),
    CategoryDescriptor('1810-consommations-energetiques-communales-eau', '1810. Consommations énergétiques communales > Eau'),
    CategoryDescriptor('1820-consommations-energetiques-communales-electricite', '1820. Consommations énergétiques communales > Electricité'),
    CategoryDescriptor('1830-consommations-energetiques-communales-gaz', '1830. Consommations énergétiques communales > Gaz'),
    CategoryDescriptor('1840-consommations-energetiques-communales-mazout-de-chauffage', '1840. Consommations énergétiques communales > Mazout de chauffage'),
    CategoryDescriptor('1900-cours-d-eau-autres', "1900. Cours d'eau > Autres"),
    CategoryDescriptor('2000-cpas-autres', '2000. CPAS > Autres'),
    CategoryDescriptor('2010-cpas-comite-de-concertation', '2010. CPAS > Comité de concertation'),
    CategoryDescriptor('2020-cpas-financement', '2020. CPAS > Financement'),
    CategoryDescriptor('2030-cpas-organes', '2030. CPAS > Organes'),
    CategoryDescriptor('2040-cpas-tutelle', '2040. CPAS > Tutelle'),
    CategoryDescriptor('2100-cultes-autres', '2100. Cultes > Autres'),
    CategoryDescriptor('2200-culture-autres', '2200. Culture > Autres'),
    CategoryDescriptor('2210-culture-bibliotheque', '2210. Culture > Bibliothèque'),
    CategoryDescriptor('2220-culture-centre-culturel', '2220. Culture > Centre culturel'),
    CategoryDescriptor('2230-culture-evenements', '2230. Culture > Evénements'),
    CategoryDescriptor('2240-culture-musees', '2240. Culture > Musées'),
    CategoryDescriptor('2300-developpement-territorial-autres', '2300. Développement territorial > Autres'),
    CategoryDescriptor('2310-developpement-territorial-gal-et-pcdr', '2310. Développement territorial > GAL et PCDR'),
    CategoryDescriptor('2320-developpement-territorial-planification', '2320. Développement territorial > Planification'),
    CategoryDescriptor('2330-developpement-territorial-projets-specifiques', '2330. Développement territorial > Projets spécifiques'),
    CategoryDescriptor('2340-developpement-territorial-quartier-nouveau', '2340. Développement territorial > Quartier nouveau'),
    CategoryDescriptor('2350-developpement-territorial-renovation-urbaine', '2350. Développement territorial > Rénovation urbaine'),
    CategoryDescriptor('2360-developpement-territorial-revitalisation-urbaine-(ecoquartier)', '2360. Développement territorial > Revitalisation urbaine (écoquartier)'),
    CategoryDescriptor('2400-divers-autres', '2400. Divers > Autres'),
    CategoryDescriptor('2500-eau-autres', '2500. Eau > Autres'),
    CategoryDescriptor('2600-egouttage-et-epuration-autres', '2600. Egouttage et épuration > Autres'),
    CategoryDescriptor('2700-elections-autres', '2700. Elections > Autres'),
    CategoryDescriptor('2800-energies-autres', '2800. Energies > Autres'),
    CategoryDescriptor('2810-energies-pollec', '2810. Energies > POLLEC'),
    CategoryDescriptor('2900-enfance,-famille-et-jeunesse-autres', '2900. Enfance, famille et jeunesse > Autres'),
    CategoryDescriptor('2910-enfance,-famille-et-jeunesse-accueil-extrascolaire', '2910. Enfance, famille et jeunesse > Accueil extrascolaire'),
    CategoryDescriptor('2920-enfance,-famille-et-jeunesse-aires-de-jeux', '2920. Enfance, famille et jeunesse > Aires de jeux'),
    CategoryDescriptor('2930-enfance,-famille-et-jeunesse-creches-mcae', '2930. Enfance, famille et jeunesse > Crèches - MCAE'),
    CategoryDescriptor('2940-enfance,-famille-et-jeunesse-gardiennes-encadrees', '2940. Enfance, famille et jeunesse > Gardiennes encadrées'),
    CategoryDescriptor('2950-enfance,-famille-et-jeunesse-maison-des-jeunes-le-hangar', '2950. Enfance, famille et jeunesse > Maison des Jeunes "Le Hangar"'),
    CategoryDescriptor('2960-enfance,-famille-et-jeunesse-plaines-de-vacances', '2960. Enfance, famille et jeunesse > Plaines de vacances'),
    CategoryDescriptor('3000-enseignement-autres', '3000. Enseignement > Autres'),
    CategoryDescriptor('3010-enseignement-enseignement-fondamental-communal', '3010. Enseignement > Enseignement fondamental communal'),
    CategoryDescriptor('3020-enseignement-enseignement-promotion-sociale', '3020. Enseignement > Enseignement promotion sociale'),
    CategoryDescriptor('3100-environnement-autres', '3100. Environnement > Autres'),
    CategoryDescriptor('3110-environnement-depots-de-dechets', '3110. Environnement > Dépôts de déchets'),
    CategoryDescriptor('3120-environnement-permis-d-exploiter', "3120. Environnement > Permis d'exploiter"),
    CategoryDescriptor('3200-festivites-autres', '3200. Festivités > Autres'),
    CategoryDescriptor('3210-festivites-affichage-evenementiel', '3210. Festivités > Affichage événementiel'),
    CategoryDescriptor('3220-festivites-brocantes', '3220. Festivités > Brocantes'),
    CategoryDescriptor('3230-festivites-debits-occasionnels', '3230. Festivités > Débits occasionnels'),
    CategoryDescriptor('3240-festivites-evenements', '3240. Festivités > Evénements'),
    CategoryDescriptor('3250-festivites-pret-de-materiel', '3250. Festivités > Prêt de matériel'),
    CategoryDescriptor('3300-finances-autres', '3300. Finances > Autres'),
    CategoryDescriptor('3310-finances-budget-et-compte', '3310. Finances > Budget et compte'),
    CategoryDescriptor('3320-finances-fiscalite', '3320. Finances > Fiscalité'),
    CategoryDescriptor('3330-finances-f.o.v.', '3330. Finances > F.O.V.'),
    CategoryDescriptor('3340-finances-subventions', '3340. Finances > Subventions'),
    CategoryDescriptor('3400-impetrants-de-voirie-autres', '3400. Impétrants de voirie > Autres'),
    CategoryDescriptor('3410-impetrants-de-voirie-eau', '3410. Impétrants de voirie > Eau'),
    CategoryDescriptor('3420-impetrants-de-voirie-eclairage-public', '3420. Impétrants de voirie > Eclairage public'),
    CategoryDescriptor('3430-impetrants-de-voirie-electricite', '3430. Impétrants de voirie > Electricité'),
    CategoryDescriptor('3440-impetrants-de-voirie-gaz', '3440. Impétrants de voirie > Gaz'),
    CategoryDescriptor('3450-impetrants-de-voirie-telecommunications', '3450. Impétrants de voirie > Télécommunications'),
    CategoryDescriptor('3460-impetrants-de-voirie-teledistribution', '3460. Impétrants de voirie > Télédistribution'),
    CategoryDescriptor('3500-informatique-et-nouvelles-technologies-autres', '3500. Informatique et nouvelles technologies > Autres'),
    CategoryDescriptor('3600-intercommunales-autres', '3600. Intercommunales > Autres'),
    CategoryDescriptor('3700-logement-autres', '3700. Logement > Autres'),
    CategoryDescriptor('3710-logement-agence-immobiliere-sociale', '3710. Logement > Agence immobilière sociale'),
    CategoryDescriptor('3720-logement-les-logis-andennais', '3720. Logement > Les Logis Andennais'),
    CategoryDescriptor('3730-logement-permis-de-location', '3730. Logement > Permis de location'),
    CategoryDescriptor('3800-loisirs-autres', '3800. Loisirs > Autres'),
    CategoryDescriptor('3810-loisirs-marches-et-assimiles', '3810. Loisirs > Marches et assimilés'),
    CategoryDescriptor('3900-marches-publics-autres', '3900. Marchés publics > Autres'),
    CategoryDescriptor('3910-marches-publics-centrale', '3910. Marchés publics > Centrale'),
    CategoryDescriptor('3920-marches-publics-fournitures', '3920. Marchés publics > Fournitures'),
    CategoryDescriptor('3930-marches-publics-in-house', '3930. Marchés publics > In House'),
    CategoryDescriptor('3940-marches-publics-services', '3940. Marchés publics > Services'),
    CategoryDescriptor('3950-marches-publics-travaux', '3950. Marchés publics > Travaux'),
    CategoryDescriptor('4000-materiels-autres', '4000. Matériels > Autres'),
    CategoryDescriptor('4010-materiels-equipements-de-bureau', '4010. Matériels > Equipements de bureau'),
    CategoryDescriptor('4020-materiels-equipements-techniques', '4020. Matériels > Equipements techniques'),
    CategoryDescriptor('4030-materiels-materiel-roulant', '4030. Matériels > Matériel roulant'),
    CategoryDescriptor('4040-materiels-mobilier-urbain', '4040. Matériels > Mobilier urbain'),
    CategoryDescriptor('4050-materiels-pret-de-materiel', '4050. Matériels > Prêt de matériel'),
    CategoryDescriptor('4100-parcs-et-plantations-autres', '4100. Parcs et plantations > Autres'),
    CategoryDescriptor('4200-patrimoine-autres', '4200. Patrimoine > Autres'),
    CategoryDescriptor('4210-patrimoine-atlas', '4210. Patrimoine > Atlas'),
    CategoryDescriptor('4220-patrimoine-baux', '4220. Patrimoine > Baux'),
    CategoryDescriptor('4230-patrimoine-contentieux', '4230. Patrimoine > Contentieux'),
    CategoryDescriptor('4240-patrimoine-immobilier', '4240. Patrimoine > Immobilier'),
    CategoryDescriptor('4250-patrimoine-occupations-precaires', '4250. Patrimoine > Occupations précaires'),
    CategoryDescriptor('4300-personnel-autres', '4300. Personnel > Autres'),
    CategoryDescriptor('4310-personnel-accidents-de-travail', '4310. Personnel > Accidents de travail'),
    CategoryDescriptor('4320-personnel-enseignants-eic', '4320. Personnel > Enseignants - EIC'),
    CategoryDescriptor('4330-personnel-enseignants-fondamental', '4330. Personnel > Enseignants - Fondamental'),
    CategoryDescriptor('4340-personnel-evaluations', '4340. Personnel > Evaluations'),
    CategoryDescriptor('4350-personnel-grades-legaux', '4350. Personnel > Grades légaux'),
    CategoryDescriptor('4360-personnel-missions-de-service', '4360. Personnel > Missions de service'),
    CategoryDescriptor('4370-personnel-stages', '4370. Personnel > Stages'),
    CategoryDescriptor('4400-population-etat-civil-autres', '4400. Population - Etat civil > Autres'),
    CategoryDescriptor('4410-population-etat-civil-communication-d-informations', "4410. Population - Etat civil > Communication d'informations"),
    CategoryDescriptor('4420-population-etat-civil-inscriptions', '4420. Population - Etat civil > Inscriptions'),
    CategoryDescriptor('4430-population-etat-civil-radiations', '4430. Population - Etat civil > Radiations'),
    CategoryDescriptor('4500-poste-et-telecommunications-autres', '4500. Poste et Télécommunications > Autres'),
    CategoryDescriptor('4510-poste-et-telecommunications-desserte-internet', '4510. Poste et Télécommunications > Desserte Internet'),
    CategoryDescriptor('4520-poste-et-telecommunications-services-postaux', '4520. Poste et Télécommunications > Services postaux'),
    CategoryDescriptor('4530-poste-et-telecommunications-telephonie-mobile-et-fixe', '4530. Poste et Télécommunications > Téléphonie mobile et fixe'),
    CategoryDescriptor('4600-relations-internationales-autres', '4600. Relations internationales > Autres'),
    CategoryDescriptor('4700-relations-publiques-autres', '4700. Relations publiques > Autres'),
    CategoryDescriptor('4710-relations-publiques-ceremonies-et-receptions', '4710. Relations publiques > Cérémonies et réceptions'),
    CategoryDescriptor('4720-relations-publiques-evenements', '4720. Relations publiques > Evénements'),
    CategoryDescriptor('4730-relations-publiques-site-internet-communal', '4730. Relations publiques > Site Internet communal'),
    CategoryDescriptor('4800-salles-et-assimiles-autres', '4800. Salles et assimilés > Autres'),
    CategoryDescriptor('4810-salles-et-assimiles-maison-des-associations', '4810. Salles et assimilés > Maison des Associations'),
    CategoryDescriptor('4820-salles-et-assimiles-salles-communales', '4820. Salles et assimilés > Salles communales'),
    CategoryDescriptor('4830-salles-et-assimiles-salle-polyvalente', '4830. Salles et assimilés > Salle polyvalente'),
    CategoryDescriptor('4840-salles-et-assimiles-refectoires-scolaires', '4840. Salles et assimilés > Réfectoires scolaires'),
    CategoryDescriptor('4900-sante-publique-autres', '4900. Santé publique > Autres'),
    CategoryDescriptor('5000-securite-publique-autres', '5000. Sécurité publique > Autres'),
    CategoryDescriptor('5010-securite-publique-plan-de-prevention-et-de-securite', '5010. Sécurité publique > Plan de prévention et de sécurité'),
    CategoryDescriptor('5020-securite-publique-planification-d-urgence', "5020. Sécurité publique > Planification d'urgence"),
    CategoryDescriptor('5030-securite-publique-prison', '5030. Sécurité publique > Prison'),
    CategoryDescriptor('5040-securite-publique-prevention-des-incendies', '5040. Sécurité publique > Prévention des incendies'),
    CategoryDescriptor('5050-securite-publique-zone-de-police', '5050. Sécurité publique > Zone de Police'),
    CategoryDescriptor('5100-seniors-autres', '5100. Seniors > Autres'),
    CategoryDescriptor('5200-services-de-secours-autres', '5200. Services de secours > Autres'),
    CategoryDescriptor('5210-services-de-secours-zone-de-secours-nage', '5210. Services de secours > Zone de secours NAGE'),
    CategoryDescriptor('5300-sports-autres', '5300. Sports > Autres'),
    CategoryDescriptor('5310-sports-evenements', '5310. Sports > Evénements'),
    CategoryDescriptor('5320-sports-installations-sportives', '5320. Sports > Installations sportives'),
    CategoryDescriptor('5330-sports-regie-des-sports', '5330. Sports > Régie des Sports'),
    CategoryDescriptor('5400-tourisme-autres', '5400. Tourisme > Autres'),
    CategoryDescriptor('5410-tourisme-activites', '5410. Tourisme > Activités'),
    CategoryDescriptor('5420-tourisme-hebergements', '5420. Tourisme > Hébergements'),
    CategoryDescriptor('5430-tourisme-promotion', '5430. Tourisme > Promotion'),
    CategoryDescriptor('5800-transition-autres', '5800. Transition > Autres'),
    CategoryDescriptor('5810-transition-ecologique', '5810. Transition > Écologique'),
    CategoryDescriptor('5820-transition-numerique', '5820. Transition > Numérique'),
    CategoryDescriptor('5500-transports-en-commun-autres', '5500. Transports en commun > Autres'),
    CategoryDescriptor('5510-transports-en-commun-bus', '5510. Transports en commun > Bus'),
    CategoryDescriptor('5520-transports-en-commun-trains', '5520. Transports en commun > Trains'),
    CategoryDescriptor('5600-travaux-autres', '5600. Travaux > Autres'),
    CategoryDescriptor('5700-voiries-autres', '5700. Voiries > Autres'),
    CategoryDescriptor('5705-voiries-autorisation-de-chantier', '5705. Voiries > Autorisation de chantier'),
    CategoryDescriptor('5710-voiries-communales', '5710. Voiries > Communales'),
    CategoryDescriptor('5720-voiries-regionales', '5720. Voiries > Régionales'),
    CategoryDescriptor('5730-voiries-denominations', '5730. Voiries > Dénominations'),
]

# Conseil Categories -----------------------------------------------------------
councilCategories = [
    CategoryDescriptor('accueil-extrascolaire', 'Accueil extrascolaire'),
    CategoryDescriptor('administration', 'Administration'),
    CategoryDescriptor('affaires-economiques', 'Affaires économiques'),
    CategoryDescriptor('affaires-generales', 'Affaires générales'),
    CategoryDescriptor('affaires-sociales', 'Affaires sociales'),
    CategoryDescriptor('amenagement-du-territoire', 'Aménagement du territoire'),
    CategoryDescriptor('associations', 'Associations'),
    CategoryDescriptor('assurances', 'Assurances'),
    CategoryDescriptor('carrieres', 'Carrières'),
    CategoryDescriptor('circulation-routiere-et-mobilite', 'Circulation routière et mobilité'),
    CategoryDescriptor('contentieux', 'Contentieux'),
    CategoryDescriptor('cours-d-eau', 'Cours d\'eau'),
    CategoryDescriptor('cpas-andenne', 'C.P.A.S. d\'Andenne'),
    CategoryDescriptor('cultes', 'Cultes'),
    CategoryDescriptor('culture', 'Culture'),
    CategoryDescriptor('declaration-de-politique-communale', 'Déclaration de politique communale'),
    CategoryDescriptor('developpement-territorial', 'Développement territorial'),
    CategoryDescriptor('divers', 'Divers'),
    CategoryDescriptor('egouttage-et-epuration', 'Égouttage et épuration'),
    CategoryDescriptor('energie', 'Énergie'),
    CategoryDescriptor('enseignement', 'Enseignement'),
    CategoryDescriptor('environnement', 'Environnement'),
    CategoryDescriptor('finances', 'Finances'),
    CategoryDescriptor('funerailles-et-sepultures', 'Funérailles et sépultures'),
    CategoryDescriptor('impetrants-de-voirie-eau', 'Impétrants de voirie - Eau'),
    CategoryDescriptor('impetrants-de-voirie-eclairage-public', 'Impétrants de voirie - Éclairage public'),
    CategoryDescriptor('impetrants-de-voirie-electricite', 'Impétrants de voirie - Électricité'),
    CategoryDescriptor('impetrants-de-voirie-gaz', 'Impétrants de voirie - Gaz'),
    CategoryDescriptor('impetrants-de-voirie-telecommunications', 'Impétrants de voirie - Télécommunications'),
    CategoryDescriptor('instances-communales-college-communal', 'Instances communales - Collège communal'),
    CategoryDescriptor('instances-communales-conseil-communal', 'Instances communales - Conseil communal'),
    CategoryDescriptor('instances-communales-commissions-communales', 'Instances communales - Commissions communales'),
    CategoryDescriptor('intercommunales', 'Intercommunales'),
    CategoryDescriptor('logement', 'Logement'),
    CategoryDescriptor('marches-publics-autres', 'Marchés publics - Autres'),
    CategoryDescriptor('marches-publics-marches-de-fournitures', 'Marchés publics - Marchés de fournitures'),
    CategoryDescriptor('marches-publics-marches-de-services', 'Marchés publics - Marchés de services'),
    CategoryDescriptor('marches-publics-marches-de-travaux', 'Marchés publics - Marchés de travaux'),
    CategoryDescriptor('patrimoine', 'Patrimoine'),
    CategoryDescriptor('personnel', 'Personnel'),
    CategoryDescriptor('police', 'Police'),
    CategoryDescriptor('revitalisation-urbaine', 'Revitalisation urbaine'),
    CategoryDescriptor('securite', 'Sécurité'),
    CategoryDescriptor('seniors', 'Seniors'),
    CategoryDescriptor('sports-installations-sportives', 'Sports - Installations sportives'),
    CategoryDescriptor('sports-regie-sportive-communale-andennaise', 'Sports - Régie sportive communale andennaise'),
    CategoryDescriptor('transports-en-commun', 'Transports en commun'),
    CategoryDescriptor('travaux', 'Travaux'),
    CategoryDescriptor('tutelle', 'Tutelle'),
    CategoryDescriptor('voiries', 'Voiries'),
    CategoryDescriptor('zone-de-police-des-arches', 'Zone de police des Arches'),
    CategoryDescriptor('zone-de-secours-nage', 'Zone de secours NAGE'),
    CategoryDescriptor('questions-et-interpellations', 'Questions et interpellations'),
]

# RapColAuCon Categories -------------------------------------------------------
rapColAuConCategories = [
    CategoryDescriptor('1-la-ville', '1. La Ville'),
    CategoryDescriptor('2-affaires-juridiques-et-patrimoniales', '2. Affaires juridiques et patrimoniales'),
    CategoryDescriptor('3-affaires-sociales', '3. Affaires sociales'),
    CategoryDescriptor('4-bien-etre-animal', '4. Bien-être animal'),
    CategoryDescriptor('5-carrieres', '5. Carrières'),
    CategoryDescriptor('6-culte', '6. Culte'),
    CategoryDescriptor('7-culture', '7. Culture'),
    CategoryDescriptor('8-developpement-territorial', '8. Développement territorial'),
    CategoryDescriptor('9-economie-et-emploi', '9. Economie et Emploi'),
    CategoryDescriptor('10-energie', '10. Energie'),
    CategoryDescriptor('11-enfance', '11. Enfance'),
    CategoryDescriptor('12-enseignement', '12. Enseignement'),
    CategoryDescriptor('13-environnement', '13. Environnement'),
    CategoryDescriptor('14-festivites-tourisme-et-loisirs', '14. Festivités, tourisme et loisirs'),
    CategoryDescriptor('15-informatique', '15. Informatique'),
    CategoryDescriptor('16-logement', '16. Logement'),
    CategoryDescriptor('17-personnel', '17. Personnel'),
    CategoryDescriptor('18-population-et-etat-civil', '18. Population et état civil'),
    CategoryDescriptor('19-relations-internationales', '19. Relations internationales'),
    CategoryDescriptor('20-relations-publiques', '20. Relations publiques'),
    CategoryDescriptor('21-secretariat-communal', '21. Secrétariat général'),
    CategoryDescriptor('22-securite', '22. Sécurité'),
    CategoryDescriptor('23-seniors', '23. Seniors'),
    CategoryDescriptor('24-sports', '24. Sports'),
    CategoryDescriptor('25-transition', '25. Transition'),
    CategoryDescriptor('26-travaux', '26. Travaux'),
    CategoryDescriptor('27.-abreviations', '27. Abréviations'),
]


# Users and groups -------------------------------------------------------------
manager = UserDescriptor( 'manager', [] )
dgen = UserDescriptor( 'dgen', [], email="test@test.be", fullname="Directeur général" )
dgenadj = UserDescriptor( 'dgenadj', [], email="test@test.be", fullname="Directeur général adjoint" )
bourgmestre = UserDescriptor( 'bourgmestre', [], email="test@test.be", fullname="Bourgmestre" )
echevin = UserDescriptor( 'echevin', [], email="test@test.be", fullname="Echevin Powerobserver" )
restrictedObserver = UserDescriptor( 'restrictedObserver', [], email="test@test.be", fullname="Restricted Observer" )
pvWriter = UserDescriptor( 'pvWriter', [], email="test@test.be", fullname="Redacteur de PV" )

roboscan = UserDescriptor ( 'roboscan', [],email='roboscan@ac.andenne.be', fullname='Robotscanner' )


prevalidationFor = ( 'logement', 'service-acte', 'service-festivites', 'service-juridique-vb', 'zonet' )

groups = [
    GroupDescriptor('a-l-e', 'A.L.E.', 'ALE'),
    GroupDescriptor('accueil-extra-scolaire', "Service de l'Accueil extrascolaire", 'aec'),
    GroupDescriptor('archeologie-andennaise', 'Archéologie andennaise', 'archand'),
    GroupDescriptor('bibliotheque', 'Bibliothèque', 'biblio'),
    GroupDescriptor('cabinet-du-bourgmestre', 'Cabinet du Bourgmestre', 'cab_bg'),
    GroupDescriptor('cabinet-costantini', 'Cabinet de Benjamin COSTANTINI', 'cab_costantini'),
    GroupDescriptor('cabinet-cruspin', 'Cabinet de Sandrine CRUSPIN', 'cab_cruspin'),
    GroupDescriptor('cabinet-havelange', 'Cabinet de Guy HAVELANGE', 'cab_havelange'),
    GroupDescriptor('cabinet-leonard', 'Cabinet de Françoise LEONARD', 'cab_leonard'),
    GroupDescriptor('cabinet-malisoux', "Cabinet d'Elisabeth MALISOUX", 'cab_malisoux'),
    GroupDescriptor('cabinet-sampaoli', 'Cabinet de Vincent SAMPAOLI', 'cab_sampaoli'),
    GroupDescriptor('cabinet-soree', 'Service des Archives', 'cab_soree'),
    GroupDescriptor('centre-culturel', 'Centre Culturel', 'cc'),
    GroupDescriptor('complexe-sportif', 'Régie des Sports', 'complexe'),
    GroupDescriptor('cpas', 'CPAS', 'cpas'),
    GroupDescriptor('dag-citoyennete-et-loisirs', 'DAG - Citoyenneté et Loisirs', 'dag_citoyennete_loisirs'),
    GroupDescriptor('dag-solidarites-et-transition', 'DAG - Solidarités et Transition', 'dag_solidarites_transition'),
    GroupDescriptor('developpement-territorial', 'Développement Territorial', 'DT'),
    GroupDescriptor('direction-generale-r-gossiaux', 'Direction Générale (R. GOSSIAUX)', 'dirgenrongos'),
    GroupDescriptor('dpo', 'DPO', 'dpo'),
    GroupDescriptor('echevins', 'Echevins', 'echevins'),
    GroupDescriptor('ecole-industrielle', 'Ecole industrielle', 'EIC'),
    GroupDescriptor('enseignement', "Service de l’Enseignement", 'enseignement'),
    GroupDescriptor('fablab', 'FabLab', 'fablab'),
    GroupDescriptor('informatique', "Service de l'Informatique", 'informatique'),
    GroupDescriptor('le-phare', 'Le Phare', 'phare'),
    GroupDescriptor('logement', 'Logement', 'logement'),
    GroupDescriptor('musee-de-la-ceramique', 'Musée de la Céramique', 'musee'),
    GroupDescriptor('personnel', 'Direction des Ressources humaines', 'personnel'),
    GroupDescriptor('planu', 'PLANU', 'planu'),
    GroupDescriptor('police', 'Zone de Police des Arches', 'police'),
    GroupDescriptor('prevention', 'Service interne de Prévention', 'SIPP'),
    GroupDescriptor('promandenne', 'PromAndenne', 'promandenne'),
    GroupDescriptor('qualite-habitat', 'Service Qualité Habitat', 'qualitehabitat'),
    GroupDescriptor('regie-des-quartiers', 'Régie des Quartiers', 'rqa'),
    GroupDescriptor('secretariat', 'Secrétariat général', 'secretariat'),
    GroupDescriptor('service-acte', 'Services de la Cohésion sociale', 'acte'),
    GroupDescriptor('service-assurances', 'Service des Assurances', 'servassurance'),
    GroupDescriptor('service-carriere', 'Service Carrière', 'carriere'),
    GroupDescriptor('service-cellule-logistique-r-gobin', 'Service logistique', 'cellog'),
    GroupDescriptor('service-des-travaux', 'Direction des Services techniques', 'travaux'),
    GroupDescriptor('service-emploi', "Service de l'Emploi", 'emploi'),
    GroupDescriptor('service-environnement', "Service de l'Environnement", 'environnement'),
    GroupDescriptor('service-festivites', 'Service des Festivités et du Tourisme', 'festivites'),
    GroupDescriptor('service-finances', 'Direction des Services financiers', 'finances'),
    GroupDescriptor('service-juridique', 'Direction des Services juridiques', 'SJ'),
    GroupDescriptor('service-juridique-oc', 'Direction des Services juridiques (OC)', 'SJOC'),
    GroupDescriptor('service-juridique-pt', 'Direction des Services juridiques (PT)', 'SJPT'),
    GroupDescriptor('service-juridique-vb', 'Direction des Services juridiques (VB)', 'SJVB'),
    GroupDescriptor('service-patrimoine', 'Service du Patrimoine', 'patrimoine'),
    GroupDescriptor('service-plaine', 'Service des Plaines', 'plaine'),
    GroupDescriptor('service-population', "Service de la Population et de l'Etat civil", 'population'),
    GroupDescriptor('service-relations-publiques', 'Service des Relations publiques', 'relpub'),
    GroupDescriptor('service-transition', 'Service Transition', 'transition'),
    GroupDescriptor('service-urbanisme', "Service de l’Aménagement du Territoire", 'urbanisme'),
    GroupDescriptor('sri', 'Zone de secours NAGE', 'SRI'),
    GroupDescriptor('zonet', 'SAGEISS', 'ZoneT')
]

for group in groups:
    agent = UserDescriptor( 'agent' + group.acronym, [], email='test@test.be', fullname='Agent ' + group.title)
    chef = UserDescriptor( 'chef' + group.acronym, [], email='test@test.be', fullname='Chef ' + group.title)
    mailViewer = UserDescriptor( 'courrier' + group.acronym, [], email='test@test.be', fullname='Lecteur courrier ' + group.title)

    group.creators.append(agent)
    group.reviewers.append(chef)
    group.mailviewers.append(mailViewer)
    group.observers.extend( [agent, chef, mailViewer] )
    group.pvwriters.append(pvWriter)

    if group.id in prevalidationFor:
        group.usePrevalidation=True
        prevalidator = UserDescriptor( 'souschef' + group.acronym, [], email='test@test.be', fullname='Sous-chef ' + group.title)
        group.prereviewers.append(prevalidator)
        group.observers.append(prevalidator)


# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = MeetingConfigDescriptor(
    'meeting-config-college', 'Collège Communal',
    'College communal', isDefault=True )
collegeMeeting.meetingManagers = [ 'manager', 'dgen', 'dgenadj', 'agentinformatique', 'chefinformatique' ]
collegeMeeting.assembly = ''
collegeMeeting.signatures = ''
collegeMeeting.certifiedSignatures = [
    { 'signatureNumber': '1',
      'name': u'Premier Echevin',
      'function': u'Le Bourgmestre f.f.',
      'date_from': '2020/01/06',
      'date_to': '2020/01/10',
    },
    { 'signatureNumber': '1',
      'name': u'Bourgmestre',
      'function': u'Le Bourgmestre',
      'date_from': '',
      'date_to': '',
    },
    { 'signatureNumber': '2',
      'name': u'Deuxième Directeur',
      'function': u'Le Directeur général f.f.',
      'date_from': '2020/01/06',
      'date_to': '2020/01/10',
    },
    { 'signatureNumber': '2',
      'name': u'Directeur Général',
      'function': u'Le Directeur général',
      'date_from': '',
      'date_to': '',
    },
]
#collegeMeeting.places = ''
collegeMeeting.budgetDefault = '<p>1) Montant de la dépense : <b>XXX  EUR TVAC</b><br />2) Article budgétaire  : <b>XXXX/XXX-XX </b><br />3) Libellé de cet article : <b>XXX</b><br />4) Crédit initial : <b>XXX EUR</b><br />5) Crédit disponible : <b>XXX EUR</b><br />6) Infos prises le <b>XXX</b> auprès de <b>XXX</b><br />7) Observations : <b>NEANT</b><br /><br /><font color="red">&laquo; ATTENTION : depuis le 1er septembre 2013, tout projet de décision ayant une incidence financière ou budgétaire supérieure à <b>22.000,00 euros</b> doit obligatoirement être accompagné d&rsquo;un avis de légalité écrit, préalable et motivé du Directeur financier. L&rsquo;avis fait partie intégrante de la décision; il doit en être fait état dans la présentation du point (proposition de décision), ainsi que dans la délibération (reproduction in extenso) lorsqu&rsquo;une délibération est établie. (Article L 1124-40 &sect; 1er-3&deg; CDLD). &raquo;</font></p>'
# collegeMeeting.defaultMeetingItemMotivation = ''
collegeMeeting.shortName = 'College'
#collegeMeeting.yearlyInitMeetingNumber = False
#collegeMeeting.configVersion = ''
#collegeMeeting.itemCreatedOnlyUsingTemplate = False
collegeMeeting.enableAnnexToPrint = True
collegeMeeting.annexToPrintDefault = True
collegeMeeting.annexDecisionToPrintDefault = True
#collegeMeeting.annexAdviceToPrintDefault = False
collegeMeeting.usedItemAttributes = [ 'budgetInfos',
                                      'associatedGroups',
                                      'observations',
                                      'toDiscuss',
                                      'itemSignatories',
                                    ]
#collegeMeeting.historizedItemAttributes = []
#collegeMeeting.recordItemHistoryStates = ()
collegeMeeting.usedMeetingAttributes = [ 'startDate', 'endDate',
                                         'signatories', 'attendees', 'absents', 'lateAttendees',
                                         'place', 'observations', 'postObservations',
                                       ]
#collegeMeeting.historizedMeetingAttributes = []
#collegeMeeting.recordMeetingHistoryStates = ()
collegeMeeting.useGroupsAsCategories = False
#collegeMeeting.toDiscussSetOnItemInsert = True
collegeMeeting.toDiscussDefault = False
#collegeMeeting.toDiscussLateDefault = True
#collegeMeeting.toDiscussShownForLateItems = True
collegeMeeting.itemReferenceFormat = ''
collegeMeeting.insertingMethodsOnAddItem = ( { 'insertingMethod': 'on_categories',
                                               'reverse': '0'
                                             },
                                           )
#collegeMeeting.allItemTags = ''
#collegeMeeting.sortAllItemTags => False
collegeMeeting.xhtmlTransformFields = [ 'MeetingItem.description', 'MeetingItem.textpv', 'MeetingItem.pv',
                                        'MeetingItem.projetpv', 'MeetingItem.decision', 'MeetingItem.observations',
                                        'Meeting.observations', 'Meeting.postObservations',
                                      ]
collegeMeeting.xhtmlTransformTypes = [ 'removeBlanks', ]
#collegeMeeting.publishDeadlineDefault => 5.9:30
#collegeMeeting.freezeDeadlineDefault => 1.14:30
#collegeMeeting.preMeetingDateDefault => 4.08:30
collegeMeeting.useUserReplacements = True
#collegeMeeting.enableAnnexConfidentiality = False
#collegeMeeting.annexConfidentialFor = ()
#collegeMeeting.enableAdviceConfidentiality = False
#collegeMeeting.adviceConfidentialityDefault = False
#collegeMeeting.adviceConfidentialFor = ()
#collegeMeeting.meetingConfigsToCloneTo = []
collegeMeeting.itemWorkflow = 'meetingitemcollegeandenne_workflow'
collegeMeeting.itemConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowConditions'
collegeMeeting.itemActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowActions'
collegeMeeting.meetingWorkflow = 'meetingcollegeandenne_workflow' 
collegeMeeting.meetingConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowConditions'
collegeMeeting.meetingActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowActions'
collegeMeeting.itemDecidedStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                     'pre_accepted', 'refused', 'refused_and_closed', 'delayed', 'delayed_and_closed',
                                   ]
collegeMeeting.workflowAdaptations = [ 'pre_validation_keep_reviewer_permissions', ]
collegeMeeting.transitionsToConfirm = [ 'Meeting.freeze', 'Meeting.close', 'MeetingItem.backToPrevalidated',
                                        'MeetingItem.backToItemCreated', 'MeetingItem.backToProposed', 'MeetingItem.delay',
                                      ]
collegeMeeting.transitionsForPresentingAnItem = [ 'propose', 'validate', 'present' ]
#collegeMeeting.onTransitionFieldTransforms = []
collegeMeeting.onMeetingTransitionItemTransitionToTrigger = [
    { 'meeting_transition': 'freeze',
      'item_transition': 'itemfreeze'
    },
    { 'meeting_transition': 'decide',
      'item_transition': 'itemfreeze',
    },
]
#collegeMeeting.meetingPresentItemWhenNoCurrentMeetingStates = []
collegeMeeting.itemAutoSentToOtherMCStates = []
#collegeMeeting.itemManualSentToOtherMCStates = []
collegeMeeting.useCopies = True
collegeMeeting.selectableCopyGroups = [ 'a-l-e_observers', 'accueil-extra-scolaire_reviewers', 'archeologie-andennaise_mailviewers',
                                        'bibliotheque_reviewers', 'cabinet-du-bourgmestre_reviewers', 'cabinet-costantini_reviewers',
                                        'cabinet-cruspin_reviewers', 'cabinet-havelange_reviewers', 'cabinet-leonard_reviewers',
                                        'cabinet-malisoux_reviewers', 'cabinet-sampaoli_reviewers', 'cabinet-soree_reviewers',
                                        'centre-culturel_mailviewers', 'complexe-sportif_observers', 'cpas_mailviewers',
                                        'dag-citoyennete-et-loisirs_reviewers', 'dag-solidarites-et-transition_reviewers',
                                        'developpement-territorial_observers',
                                        'direction-generale-r-gossiaux_reviewers', 'dpo_reviewers', 'ecole-industrielle_reviewers',
                                        'enseignement_observers', 'enseignement_reviewers', 'fablab_observers', 'informatique_observers',
                                        'informatique_reviewers', 'le-phare_reviewers', 'musee-de-la-ceramique_reviewers', 'personnel_observers',
                                        'planu_reviewers', 'police_mailviewers', 'prevention_observers', 'promandenne_mailviewers',
                                        'qualite-habitat_observers', 'qualite-habitat_reviewers', 'secretariat_reviewers', 'service-acte_reviewers',
                                        'service-assurances_observers', 'service-carriere_observers', 'service-cellule-logistique-r-gobin_reviewers',
                                        'service-des-travaux_reviewers', 'service-emploi_reviewers', 'service-environnement_reviewers',
                                        'service-festivites_observers', 'service-festivites_reviewers', 'service-finances_observers',
                                        'service-finances_reviewers', 'service-juridique_observers', 'service-juridique-oc_reviewers',
                                        'service-juridique-pt_reviewers', 'service-juridique-vb_reviewers', 'service-patrimoine_observers',
                                        'service-plaine_reviewers', 'service-population_reviewers', 'service-relations-publiques_reviewers',
                                        'service-transition_observers', 'service-urbanisme_reviewers', 'sri_mailviewers', 'zonet_observers',
                                        'zonet_reviewers',
                                     ]
collegeMeeting.itemCopyGroupsStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                        'pre_accepted', 'itemfrozen', 'presented', 'refused', 'refused_and_closed', 'delayed',
                                        'delayed_and_closed', 'validated',
                                      ]
#collegeMeeting.hideItemHistoryCommentsToUsersOutsideProposingGroup = False
#collegeMeeting.restrictAccessToSecretItems = False
collegeMeeting.meetingTopicStates = ( 'frozen', 'created' )
collegeMeeting.decisionTopicStates = ( 'closed', 'decided' )
#collegeMeeting.maxShownMeetings = 5
#collegeMeeting.maxDaysDecisions = 60
collegeMeeting.meetingAppDefaultView = 'topic_searchmyitems'
collegeMeeting.itemsListVisibleColumns = [ 'actions', 'annexes', 'categoryOrProposingGroup', 'creator', 'state' ]
collegeMeeting.itemsListVisibleFields = [ 'decision', ]
collegeMeeting.itemColumns = [ 'actions', 'annexes', 'advices', 'creator', 'creationDate', 'state' ]
#collegeMeeting.meetingColumns = [ 'creator', 'creationDate', 'state', 'actions' ]
collegeMeeting.maxShownAvailableItems = 300
collegeMeeting.maxShownMeetingItems = 300
collegeMeeting.maxShownLateItems = 300
#collegeMeeting.enableGotoPage = False
#collegeMeeting.enableGotoItem = True
#collegeMeeting.openAnnexesInSeparateWindows = False
#collegeMeeting.mailMode = 'activated'
#collegeMeeting.mailFormat = 'text'
collegeMeeting.mailItemEvents = [ 'itemDelayed', 'adviceToGive', 'returnedToProposingGroup', 'event_add_pv_annex' ]
#collegeMeeting.mailMeetingEvents = []

collegeMeeting.categories = collegeCategories
collegeMeeting.meetingFileTypes = [ annexe, annexeCahier, annexeDecision, annexeAvis, annexeAvisLegal,
                                    annexeNoteExecution, annexeDeliberation ]
collegeMeeting.podTemplates = collegeTemplates
#collegeMeeting.toDoListTopics = [<ATTopic at /commune/portal_plonemeeting/meeting-config-college/topics/searchitemstovalidate>, <ATTopic at /commune/portal_plonemeeting/meeting-config-college/topics/searchallitemstoadvice>, <ATTopic at /commune/portal_plonemeeting/meeting-config-college/topics/searchallitemsincopy>]

#collegeMeeting.useAdvices = False
#collegeMeeting.itemAdviceStates = []
#collegeMeeting.itemAdviceEditStates = []
#collegeMeeting.itemAdviceViewStates = []
#collegeMeeting.itemBudgetInfosStates = []
#collegeMeeting.powerAdvisersGroups = []
collegeMeeting.itemPowerObserversStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                            'pre_accepted', 'itemfrozen', 'refused', 'refused_and_closed', 'delayed', 'delayed_and_closed',
                                          ]
#collegeMeeting.meetingPowerObserversStates = [ 'frozen', 'closed', 'decided' ]
#collegeMeeting.itemRestrictedPowerObserversStates = []
#collegeMeeting.meetingRestrictedPowerObserversStates = []
#collegeMeeting.usedAdviceTypes = ( 'positive', 'positive_with_remarks', 'negative', 'nil' )
#collegeMeeting.defaultAdviceType = 'positive'
#collegeMeeting.enforceAdviceMandatoriness = False
#collegeMeeting.enableAdviceInvalidation = False
#collegeMeeting.itemAdviceInvalidateStates = []
#collegeMeeting.adviceStyle = 'standard'
#collegeMeeting.defaultAdviceHiddenDuringRedaction = False
#collegeMeeting.transitionReinitializingDelays = ''
#collegeMeeting.customAdvisers = []
#collegeMeeting.useVotes = False
#collegeMeeting.votesEncoder = ( 'theVoterHimself', )
#collegeMeeting.usedVoteValues => ( 'not_yet', 'yes', 'no', 'abstain' )
#collegeMeeting.defaultVoteValue = 'not_yet'
#collegeMeeting.voteCondition = 'True'

collegeMeeting.lastMeetingNumberInParliamentaryTerm = 0
collegeMeeting.useSubCategories = True
collegeMeeting.selectableAssociatedGroups = [ 'accueil-extra-scolaire_observers', 'archeologie-andennaise_observers', 'bibliotheque_observers',
                                              'cabinet-soree_observers', 'complexe-sportif_observers', 'cpas_observers',
                                              'dag-citoyennete-et-loisirs_observers', 'dag-solidarites-et-transition_observers',
                                              'developpement-territorial_observers',
                                              'direction-generale-r-gossiaux_observers', 'dpo_observers', 'ecole-industrielle_observers',
                                              'enseignement_observers', 'fablab_observers', 'informatique_observers', 'le-phare_observers',
                                              'musee-de-la-ceramique_observers', 'personnel_observers', 'planu_observers', 'prevention_observers',
                                              'qualite-habitat_observers', 'secretariat_observers', 'service-acte_observers',
                                              'service-assurances_observers', 'service-carriere_observers', 'service-cellule-logistique-r-gobin_observers',
                                              'service-des-travaux_observers', 'service-emploi_observers', 'service-environnement_observers',
                                              'service-festivites_observers', 'service-finances_observers', 'service-juridique_observers',
                                              'service-juridique-oc_observers', 'service-juridique-pt_observers', 'service-juridique-vb_observers',
                                              'service-patrimoine_observers', 'service-plaine_observers', 'service-population_observers',
                                              'service-relations-publiques_observers', 'service-transition_observers', 'service-urbanisme_observers',
                                              'zonet_observers',
                                            ]

bourgmestre_mu = MeetingUserDescriptor('claeer',
                                       duty = 'Bourgmestre',
                                       replacementDuty = "Bourgmestre f.f.",
                                       usages = ['assemblyMember', 'signer', ],
                                       signatureIsDefault = True)
Echevin1 = MeetingUserDescriptor('vinsam',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', ])
Echevin2 = MeetingUserDescriptor('bencos',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', ])
Echevin3 = MeetingUserDescriptor('guyhav',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', ])
Echevin4 = MeetingUserDescriptor('fraleo',
                                 gender = 'f',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', ])
Echevin5 = MeetingUserDescriptor('elimal',
                                 gender = 'f',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', ])
CAPS_mu = MeetingUserDescriptor('sancru',
                                gender = 'f',
                                duty = "Présidente du Conseil de l'Action sociale",
                                usages = ['assemblyMember', 'signer', ])
dgen_mu = MeetingUserDescriptor('dgen',
                                duty = 'Directeur Général',
                                replacementDuty = "Directeur Général f.f.",
                                usages = ['assemblyMember', 'signer', ],
                                signatureIsDefault = True)
dgenadj_mu = MeetingUserDescriptor('dgenadj',
                                duty = 'Directeur général adjoint',
                                replacementDuty = "Directeur général adjoint f.f.",
                                usages = ['signer', ])

collegeMeeting.meetingUsers = [ bourgmestre_mu, Echevin1, Echevin2, Echevin3, Echevin4, Echevin5, CAPS_mu, dgen_mu, dgenadj_mu ]
college_meetingUsersTitles = { 'claeer': 'Claude EERDEKENS', 'vinsam': 'Vincent SAMPAOLI', 'bencos': 'Benjamin COSTANTINI',
                                'guyhav': 'Guy HAVELANGE', 'fraleo': 'Françoise LEONARD', 'elimal': 'Elisabeth MALISOUX',
                                'sancru': 'Sandrine CRUSPIN', 'dgen': 'Directeur général', 'dgenadj': 'Directeur général adjoint'
}

college_powerobservers = PloneGroupDescriptor( 'meeting-config-college_powerobservers',
                                               'meeting-config-college_powerobservers',
                                               [] )
echevin.ploneGroups = [ college_powerobservers, ]

college_restrictedpowerobservers = PloneGroupDescriptor( 'meeting-config-college_restrictedpowerobservers',
                                                         'meeting-config-college_restrictedpowerobservers',
                                                         [] )
restrictedObserver.ploneGroups = [ college_restrictedpowerobservers, ]


# conseil
councilMeeting = MeetingConfigDescriptor(
    'meeting-config-council', 'Conseil Communal',
    'Conseil communal' )
councilMeeting.meetingManagers = [ 'manager', 'dgen', 'dgenadj', 'agentinformatique', 'chefinformatique' ]
councilMeeting.assembly = ''
councilMeeting.signatures = ''
councilMeeting.certifiedSignatures = [
    { 'signatureNumber': '1',
      'name': u'Premier Echevin',
      'function': u'Le Bourgmestre f.f.',
      'date_from': '2020/01/06',
      'date_to': '2020/01/10',
    },
    { 'signatureNumber': '1',
      'name': u'Bourgmestre',
      'function': u'Le Bourgmestre',
      'date_from': '',
      'date_to': '',
    },
    { 'signatureNumber': '2',
      'name': u'Deuxième Directeur',
      'function': u'Le Directeur général f.f.',
      'date_from': '2020/01/06',
      'date_to': '2020/01/10',
    },
    { 'signatureNumber': '2',
      'name': u'Directeur Général',
      'function': u'Le Directeur général',
      'date_from': '',
      'date_to': '',
    },
]
#councilMeeting.places = ''
councilMeeting.budgetDefault = '<p>1) Montant de la dépense : <b>XXX  EUR TVAC</b><br />2) Article budgétaire  : <b>XXXX/XXX-XX </b><br />3) Libellé de cet article : <b>XXX</b><br />4) Crédit initial : <b>XXX EUR</b><br />5) Crédit disponible : <b>XXX EUR</b><br />6) Infos prises le <b>XXX</b> auprès de <b>XXX</b><br />7) Observations : <b>NEANT</b><br /><br /><font color="red">&laquo; ATTENTION : depuis le 1er septembre 2013, tout projet de décision ayant une incidence financière ou budgétaire supérieure à <b>22.000,00 euros</b> doit obligatoirement être accompagné d&rsquo;un avis de légalité écrit, préalable et motivé du Directeur financier. L&rsquo;avis fait partie intégrante de la décision; il doit en être fait état dans la présentation du point (proposition de décision), ainsi que dans la délibération (reproduction in extenso) lorsqu&rsquo;une délibération est établie. (Article L 1124-40 &sect; 1er-3&deg; CDLD). &raquo;</font></p>'
councilMeeting.shortName = 'Council'
councilMeeting.yearlyInitMeetingNumber = True
councilMeeting.enableAnnexToPrint = True
councilMeeting.annexToPrintDefault = True
councilMeeting.annexDecisionToPrintDefault = True
councilMeeting.usedItemAttributes = [ 'budgetInfos',
                                      'associatedGroups',
                                      'emergency',
                                      'notes',
                                      'observations',
                                      'itemSignatories',
                                      'privacy',
                                      'completeness',
                                      'questioners',
                                      'answerers',
                                    ]
councilMeeting.usedMeetingAttributes = [ 'startDate', 'endDate',
                                         'signatories', 'attendees', 'excused', 'absents',
                                         'lateAttendees', 'place', 'notes', 'observations',
                                         'postObservations',
                                       ]
councilMeeting.useGroupsAsCategories = False
councilMeeting.itemReferenceFormat = "python: 'Ref. ' + str(here.getItemNumber(relativeTo='meetingConfig'))"
councilMeeting.insertingMethodsOnAddItem = ( { 'insertingMethod': 'on_privacy',
                                               'reverse': '0'
                                             },
                                             { 'insertingMethod': 'on_categories',
                                               'reverse': '0'
                                             },
                                           )
councilMeeting.xhtmlTransformFields = [ 'MeetingItem.description', 'MeetingItem.textpv', 'MeetingItem.pv',
                                        'MeetingItem.projetpv', 'MeetingItem.decision', 'MeetingItem.notes',
                                        'MeetingItem.observations',
                                        'Meeting.notes', 'Meeting.observations', 'Meeting.postObservations',
                                      ]
councilMeeting.xhtmlTransformTypes = [ 'removeBlanks', ]
councilMeeting.useUserReplacements = True
councilMeeting.itemWorkflow = 'meetingitemcollegeandenne_workflow'
councilMeeting.itemConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowConditions'
councilMeeting.itemActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowActions'
councilMeeting.meetingWorkflow = 'meetingcollegeandenne_workflow' 
councilMeeting.meetingConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowConditions'
councilMeeting.meetingActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowActions'
councilMeeting.itemDecidedStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                     'pre_accepted', 'refused', 'refused_and_closed', 'delayed', 'delayed_and_closed',
                                   ]
councilMeeting.workflowAdaptations = [ 'pre_validation_keep_reviewer_permissions', ]
councilMeeting.transitionsToConfirm = [ 'Meeting.freeze', 'Meeting.close', 'Meeting.backToCreated', 'Meeting.backToDecided',
                                        'MeetingItem.backToPrevalidated', 'MeetingItem.backToItemFrozen', 'MeetingItem.backToAccepted',
                                        'MeetingItem.backToAcceptedButModified', 'MeetingItem.backToDelayed', 'MeetingItem.backToRefused',
                                        'MeetingItem.backToItemCreated', 'MeetingItem.backToProposed', 'MeetingItem.delay',
                                      ]
councilMeeting.transitionsForPresentingAnItem = [ 'propose', 'validate', 'present' ]
councilMeeting.onMeetingTransitionItemTransitionToTrigger = [
    { 'meeting_transition': 'freeze',
      'item_transition': 'itemfreeze'
    },
    { 'meeting_transition': 'decide',
      'item_transition': 'itemfreeze'
    },
    { 'meeting_transition': 'close',
      'item_transition': 'itemfreeze'
    },
    { 'meeting_transition': 'close',
      'item_transition': 'accept'
    },
    { 'meeting_transition': 'close',
      'item_transition': 'accept_and_close'
    }
]
councilMeeting.itemAutoSentToOtherMCStates = []
councilMeeting.useCopies = True
councilMeeting.selectableCopyGroups = [ 'a-l-e_observers', 'accueil-extra-scolaire_reviewers', 'archeologie-andennaise_observers',
                                        'bibliotheque_reviewers', 'cabinet-du-bourgmestre_reviewers', 'cabinet-costantini_reviewers',
                                        'cabinet-cruspin_reviewers', 'cabinet-havelange_reviewers', 'cabinet-leonard_reviewers',
                                        'cabinet-malisoux_reviewers', 'cabinet-sampaoli_reviewers', 'cabinet-soree_reviewers',
                                        'centre-culturel_reviewers', 'complexe-sportif_reviewers', 'cpas_observers', 'cpas_mailviewers',
                                        'dag-citoyennete-et-loisirs_reviewers', 'dag-solidarites-et-transition_reviewers',
                                        'developpement-territorial_observers',
                                        'direction-generale-r-gossiaux_reviewers', 'dpo_reviewers', 'ecole-industrielle_reviewers',
                                        'enseignement_observers', 'enseignement_reviewers', 'fablab_observers', 'informatique_observers',
                                        'informatique_reviewers', 'le-phare_reviewers', 'musee-de-la-ceramique_reviewers', 'personnel_reviewers',
                                        'planu_reviewers', 'police_reviewers', 'prevention_observers', 'promandenne_reviewers',
                                        'qualite-habitat_observers', 'qualite-habitat_reviewers', 'secretariat_reviewers', 'service-acte_reviewers',
                                        'service-assurances_observers', 'service-carriere_observers', 'service-cellule-logistique-r-gobin_reviewers',
                                        'service-des-travaux_reviewers', 'service-emploi_reviewers', 'service-environnement_reviewers',
                                        'service-festivites_observers', 'service-festivites_reviewers', 'service-finances_observers',
                                        'service-finances_reviewers', 'service-juridique_observers', 'service-juridique-oc_reviewers',
                                        'service-juridique-pt_reviewers', 'service-juridique-vb_reviewers', 'service-patrimoine_observers',
                                        'service-plaine_reviewers', 'service-population_reviewers', 'service-relations-publiques_reviewers',
                                        'service-transition_observers', 'service-urbanisme_reviewers', 'sri_reviewers', 'zonet_observers',
                                        'zonet_reviewers',
                                     ]
councilMeeting.itemCopyGroupsStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                        'pre_accepted', 'itemfrozen', 'presented', 'refused', 'refused_and_closed', 'delayed',
                                        'delayed_and_closed', 'validated',
                                      ]
councilMeeting.meetingTopicStates = ( 'frozen', 'created' )
councilMeeting.decisionTopicStates = ( 'closed', 'decided' )
councilMeeting.meetingAppDefaultView = 'topic_searchmyitems'
councilMeeting.itemsListVisibleColumns = [ 'actions', 'annexes', 'categoryOrProposingGroup', 'creator', 'state' ]
councilMeeting.itemsListVisibleFields = [ 'decision', ]
councilMeeting.itemColumns = [ 'actions', 'annexes', 'creator', 'creationDate', 'state', 'privacy' ]
councilMeeting.maxShownAvailableItems = 300
councilMeeting.maxShownMeetingItems = 300
councilMeeting.maxShownLateItems = 300
councilMeeting.mailItemEvents = [ 'itemDelayed', 'returnedToProposingGroup', 'event_add_pv_annex' ]

councilMeeting.categories = councilCategories
councilMeeting.meetingFileTypes = [ annexe, annexeCahier, annexeDecision,
                                    annexeNoteExecution, annexeDeliberation ]
councilMeeting.podTemplates = councilTemplates
#councilMeeting.toDoListTopics = [<ATTopic at /commune/portal_plonemeeting/meeting-config-college/topics/searchitemstovalidate>, <ATTopic at /commune/portal_plonemeeting/meeting-config-college/topics/searchallitemstoadvice>, <ATTopic at /commune/portal_plonemeeting/meeting-config-college/topics/searchallitemsincopy>]

councilMeeting.itemPowerObserversStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                            'pre_accepted', 'itemfrozen', 'refused', 'refused_and_closed', 'delayed', 'delayed_and_closed',
                                          ]
councilMeeting.useVotes = True
councilMeeting.votesEncoder = ( 'aMeetingManager', )
#councilMeeting.usedVoteValues => ( 'not_yet', 'yes', 'no', 'abstain' )
#councilMeeting.defaultVoteValue = 'not_yet'
#councilMeeting.voteCondition = 'True'

councilMeeting.lastMeetingNumberInParliamentaryTerm = 0
councilMeeting.useSubCategories = False
councilMeeting.selectableAssociatedGroups = [ 'accueil-extra-scolaire_observers', 'archeologie-andennaise_observers', 'bibliotheque_observers',
                                              'cabinet-soree_observers', 'complexe-sportif_observers', 'cpas_observers',
                                              'dag-citoyennete-et-loisirs_observers', 'dag-solidarites-et-transition_observers',
                                              'developpement-territorial_observers',
                                              'direction-generale-r-gossiaux_observers', 'dpo_observers', 'ecole-industrielle_observers',
                                              'enseignement_observers', 'fablab_observers', 'informatique_observers', 'le-phare_observers',
                                              'musee-de-la-ceramique_observers', 'personnel_observers', 'planu_observers', 'prevention_observers',
                                              'qualite-habitat_observers', 'secretariat_observers', 'service-acte_observers',
                                              'service-assurances_observers', 'service-carriere_observers', 'service-cellule-logistique-r-gobin_observers',
                                              'service-des-travaux_observers', 'service-emploi_observers', 'service-environnement_observers',
                                              'service-festivites_observers', 'service-finances_observers', 'service-juridique_observers',
                                              'service-juridique-oc_observers', 'service-juridique-pt_observers', 'service-juridique-vb_observers',
                                              'service-patrimoine_observers', 'service-plaine_observers', 'service-population_observers',
                                              'service-relations-publiques_observers', 'service-transition_observers', 'service-urbanisme_observers',
                                              'zonet_observers',
                                            ]

bourgmestre_mu = MeetingUserDescriptor('claeer',
                                       duty = 'Bourgmestre',
                                       replacementDuty = "Bourgmestre f.f.",
                                       usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Echevin1 = MeetingUserDescriptor('vinsam',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Echevin2 = MeetingUserDescriptor('bencos',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Echevin3 = MeetingUserDescriptor('guyhav',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Echevin4 = MeetingUserDescriptor('fraleo',
                                 gender = 'f',
                                 duty = 'Echevin', 
                                 usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Echevin5 = MeetingUserDescriptor('elimal',
                                 gender = 'f',
                                 duty = 'Echevin',
                                 usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller1 = MeetingUserDescriptor('sancru',
                                    gender = 'f',
                                    duty = "Conseiller",
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller2 = MeetingUserDescriptor('chrbad',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller3 = MeetingUserDescriptor('marmau',
                                    gender = 'f',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller4 = MeetingUserDescriptor('etiser',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller5 = MeetingUserDescriptor('roscas',
                                    gender = 'f',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller6 = MeetingUserDescriptor('phimat',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller7 = MeetingUserDescriptor('phiras',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ],
                                    signatureIsDefault = True)
Conseiller8 = MeetingUserDescriptor('chrmat',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller9 = MeetingUserDescriptor('fratar',
                                    gender = 'f',
                                    duty = 'Conseiller',
                                    usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller10 = MeetingUserDescriptor('flohal',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker',  ])
Conseiller11 = MeetingUserDescriptor('mardie',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller12 = MeetingUserDescriptor('casluo',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller13 = MeetingUserDescriptor('jawtaf',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller14 = MeetingUserDescriptor('kevgoo',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller15 = MeetingUserDescriptor('carlom',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller16 = MeetingUserDescriptor('chrbod',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller17 = MeetingUserDescriptor('mluser',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller18 = MeetingUserDescriptor('natfra',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller19 = MeetingUserDescriptor('gwewil',
                                     gender = 'f',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller20 = MeetingUserDescriptor('damlou',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller21 = MeetingUserDescriptor('hugdou',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller22 = MeetingUserDescriptor('natels',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
Conseiller23 = MeetingUserDescriptor('eddsar',
                                     duty = 'Conseiller',
                                     usages = ['assemblyMember', 'signer', 'voter', 'asker', ])
dgen_mu = MeetingUserDescriptor('dgen',
                                duty = 'Directeur Général',
                                replacementDuty = "Directeur Général f.f.",
                                usages = ['assemblyMember', 'signer', ],
                                signatureIsDefault = True)
dgenadj_mu = MeetingUserDescriptor('dgenadj',
                                duty = 'Directeur général adjoint',
                                replacementDuty = "Directeur général adjoint f.f.",
                                usages = ['signer', ])

councilMeeting.meetingUsers = [ bourgmestre_mu, Echevin1, Echevin2, Echevin3, Echevin4, Echevin5, Conseiller1, Conseiller2,
                                Conseiller3, Conseiller4, Conseiller5, Conseiller6, Conseiller7, Conseiller8, Conseiller9,
                                Conseiller10, Conseiller11, Conseiller12, Conseiller13, Conseiller14, Conseiller15, Conseiller16,
                                Conseiller17, Conseiller18, Conseiller19, Conseiller20, Conseiller21, Conseiller22, Conseiller23,
                                dgen_mu, dgenadj_mu ]
council_meetingUsersTitles = { 'claeer': 'Claude EERDEKENS', 'vinsam': 'Vincent SAMPAOLI', 'bencos': 'Benjamin COSTANTINI',
                                'guyhav': 'Guy HAVELANGE', 'fraleo': 'Françoise LEONARD', 'elimal': 'Elisabeth MALISOUX',
                                'sancru': 'Sandrine CRUSPIN', 'chrbad': 'Christian BADOT', 'marmau': 'Marie-Christine MAUGUIT',
                                'etiser': 'Etienne SERMON', 'roscas': 'Rose SIMON-CASTELLAN', 'phimat': 'Philippe MATTART',
                                'phiras': 'Philippe RASQUIN', 'chrmat': 'Christian MATTART', 'fratar': 'Françoise TARPATAKI',
                                'flohal': 'Florence HALLEUX', 'mardie': 'Martine DIEUDONNE-OLIVIER', 'casluo': 'Cassandra LUONGO',
                                'jawtaf': 'Jawad TAFRATA', 'carlom': 'Caroline LOMBA', 'chrbod': 'Christine BODART',
                                'mluser': 'Marie-Luce SERESSIA', 'natfra': 'Natacha FRANCOIS', 'gwawil': 'Gwendoline WILLIQUET',
                                'damlou': 'Damien LOUIS', 'hugdou': 'Hugues DOUMONT', 'natels': 'Nathalie ELSEN',
                                'eddsar': 'Eddy SARTORI', 'dgen': 'Directeur général', 'dgenadj': 'Directeur général adjoint'
}

council_powerobservers = PloneGroupDescriptor( 'meeting-config-council_powerobservers',
                                               'meeting-config-council_powerobservers',
                                               [] )
#echevin.ploneGroups = [ council_powerobservers, ]

council_restrictedpowerobservers = PloneGroupDescriptor( 'meeting-config-council_restrictedpowerobservers',
                                                         'meeting-config-council_restrictedpowerobservers',
                                                         [] )
#restrictedObserver.ploneGroups = [ council_restrictedpowerobservers, ]


# rapcolaucon
rccMeeting = MeetingConfigDescriptor(
    'rapport-col-au-con', 'Rapport Col. au Con.', 'rapcolaucon' )
rccMeeting.meetingManagers = [ 'manager', 'dgen', 'dgenadj', 'agentinformatique', 'chefinformatique' ]
rccMeeting.shortName = 'rcc'
rccMeeting.enableAnnexToPrint = True
rccMeeting.annexToPrintDefault = True
rccMeeting.usedItemAttributes = [ 'observations', ]
rccMeeting.usedMeetingAttributes = [ 'observations', 'postObservations' ]
rccMeeting.useGroupsAsCategories = False
rccMeeting.itemReferenceFormat = "python: 'Ref. ' + str(here.getItemNumber(relativeTo='meetingConfig'))"
rccMeeting.insertingMethodsOnAddItem = ( { 'insertingMethod': 'on_categories',
                                               'reverse': '0'
                                         },
                                       )
rccMeeting.itemWorkflow = 'meetingitemcollegeandenne_workflow'
rccMeeting.itemConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowConditions'
rccMeeting.itemActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowActions'
rccMeeting.meetingWorkflow = 'meetingcollegeandenne_workflow' 
rccMeeting.meetingConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowConditions'
rccMeeting.meetingActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowActions'
rccMeeting.itemDecidedStates = [ 'accepted', 'accepted_but_modified', 'accepted_but_modified_and_closed', 'accepted_and_closed',
                                 'pre_accepted', 'refused', 'refused_and_closed', 'delayed', 'delayed_and_closed',
                               ]
rccMeeting.workflowAdaptations = [ 'pre_validation_keep_reviewer_permissions', ]
rccMeeting.transitionsToConfirm = [ 'Meeting.freeze', 'Meeting.close', 'MeetingItem.delay' ]
rccMeeting.transitionsForPresentingAnItem = [ 'propose', 'validate', 'present' ]
rccMeeting.onMeetingTransitionItemTransitionToTrigger = [
    { 'meeting_transition': 'freeze',
      'item_transition': 'itemfreeze'
    },
    { 'meeting_transition': 'decide',
      'item_transition': 'itemfreeze',
    },
    { 'meeting_transition': 'close',
      'item_transition': 'itemfreeze'
    },
    { 'meeting_transition': 'close',
      'item_transition': 'accept'
    },
    { 'meeting_transition': 'close',
      'item_transition': 'accept_and_close'
    },
]
rccMeeting.meetingTopicStates = ( 'frozen', 'created' )
rccMeeting.decisionTopicStates = ( 'closed', 'decided' )
rccMeeting.meetingAppDefaultView = 'topic_searchmyitems'
rccMeeting.itemsListVisibleColumns = [ 'state', 'categoryOrProposingGroup', 'actions' ]
rccMeeting.itemColumns = [ 'creator', 'creationDate', 'state', 'annexes', 'actions' ]
rccMeeting.maxShownAvailableItems = 100
rccMeeting.maxShownMeetingItems = 100
rccMeeting.maxShownLateItems = 100

rccMeeting.categories = rapColAuConCategories
rccMeeting.meetingFileTypes = [ annexe, ]
rccMeeting.podTemplates = rapColAuConTemplates

rccMeeting.lastMeetingNumberInParliamentaryTerm = 0
rccMeeting.useSubCategories = False
rccMeeting.selectableAssociatedGroups = []


data = PloneMeetingConfiguration( 'Mes seances',
                                  (collegeMeeting, councilMeeting, rccMeeting ),
                                  groups )
data.unoEnabledPython = sys.executable
data.usedColorSystem = 'state_color'
data.dateFormat = "%-d %mt %Y"
data.extractTextFromFiles = True
data.availableOcrLanguages = ( 'eng', 'fra', 'deu', 'nld' )
data.defaultOcrLanguage = 'fra'
data.publicUrl = 'http://andana.andenne.be:8080'
data.maxShownFound = 40
data.usersOutsideGroups = [ manager, dgen, dgenadj, bourgmestre, echevin,
                            restrictedObserver, roboscan ]

# ------------------------------------------------------------------------------
