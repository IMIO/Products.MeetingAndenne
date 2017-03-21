# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.PloneMeeting.profiles import CategoryDescriptor
from Products.PloneMeeting.profiles import GroupDescriptor
from Products.PloneMeeting.profiles import ItemTemplateDescriptor
from Products.PloneMeeting.profiles import MeetingConfigDescriptor
from Products.PloneMeeting.profiles import MeetingFileTypeDescriptor
from Products.PloneMeeting.profiles import MeetingUserDescriptor
from Products.PloneMeeting.profiles import PloneMeetingConfiguration
from Products.PloneMeeting.profiles import PodTemplateDescriptor
from Products.PloneMeeting.profiles import RecurringItemDescriptor
from Products.PloneMeeting.profiles import UserDescriptor

today = DateTime().strftime('%Y/%m/%d')
# File types -------------------------------------------------------------------
annexe = MeetingFileTypeDescriptor('annexe', 'Annexe', 'attach.png', '')
annexeBudget = MeetingFileTypeDescriptor('annexeBudget', 'Article Budgétaire', 'budget.png', '')
annexeCahier = MeetingFileTypeDescriptor('annexeCahier', 'Cahier des Charges', 'cahier.gif', '')
annexeDecision = MeetingFileTypeDescriptor('annexeDecision', 'Annexe à la décision', 'attach.png', '', 'item_decision')
annexeAvis = MeetingFileTypeDescriptor('annexeAvis', 'Annexe à un avis',
                                       'attach.png', '', 'advice')
annexeAvisLegal = MeetingFileTypeDescriptor('annexeAvisLegal', 'Extrait article de loi',
                                            'legalAdvice.png', '', 'advice')

# Categories -------------------------------------------------------------------
categories = [
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
CategoryDescriptor('52-sante-publique', '52. Santé publique'),
CategoryDescriptor('53-securite-publique', '53. Sécurité publique'),
CategoryDescriptor('54-sports', '54. Sports'),
CategoryDescriptor('55-telecommunications', '55. Télécommunications'),
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
]

# Pod templates ----------------------------------------------------------------

itemNoteTemplate = PodTemplateDescriptor('ne', "Note d'execution")
itemNoteTemplate.podTemplate = 'MeetingItemAndenneexecution3.odt'
itemNoteTemplate.podCondition = 'python:here.meta_type=="MeetingItem" and here.queryState() in ("accepted", "accepted_but_modified","delayed","pre_accepted","refused","accepted_and_closed","accepted_but_modified_and_closed","refused_and_closed","delayed_and_closed")'

decisionsTemplate = PodTemplateDescriptor('pv', 'P.V.')
decisionsTemplate.podTemplate = 'Meetingproposednew3.odt'
decisionsTemplate.podCondition = 'python:(here.meta_type=="Meeting") and here.queryState() in ["decided", "closed","archived"]'

agendaTemplate = PodTemplateDescriptor('oj', 'O.J.')
agendaTemplate.podTemplate = 'meetingandennenew4.odt'
agendaTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'

agendalateTemplate = PodTemplateDescriptor('ojc', 'O.J. Comp.')
agendalateTemplate.podTemplate = 'meetingandennelatenew3.odt'
agendalateTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'

itemDeliberationTemplate = PodTemplateDescriptor('deliberation', 'délibération')
itemDeliberationTemplate.podTemplate = 'MeetingItemAndenneproposednew4.odt'
itemDeliberationTemplate.podCondition = 'python:here.meta_type=="MeetingItem" and here.queryState() in ("accepted", "accepted_but_modified","delayed","pre_accepted","refused","accepted","accepted_and_closed","accepted_but_modified_and_closed","refused_and_closed","delayed_and_closed")'

itemProjectTemplate = PodTemplateDescriptor('proposition', 'Proposition au collège ')
itemProjectTemplate.podTemplate = 'MeetingItemAndennenew3.odt'
itemProjectTemplate.podCondition = 'python:here.meta_type=="MeetingItem"'

agendaPersTemplate = PodTemplateDescriptor('ojp', 'O.J. Personnel')
agendaPersTemplate.podTemplate = 'meetingandennepersonnelnew2.odt'
agendaPersTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'

agendaPersLateTemplate = PodTemplateDescriptor('ojpc', 'O.J. Comp. Personnel')
agendaPersLateTemplate.podTemplate = 'meetingandennelatepersonnelnew2.odt'
agendaPersLateTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'

agendaCpasTemplate = PodTemplateDescriptor('ojcpas', 'O.J. CPAS')
agendaCpasTemplate.podTemplate = 'meetingandennecpasnew2.odt'
agendaCpasTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'

agendaCpasLateTemplate = PodTemplateDescriptor('ojcpasc', 'O.J. Comp. CPAS')
agendaCpasLateTemplate.podTemplate = 'meetingandennelatecpasnew2 .odt'
agendaCpasLateTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'

agendaListeTemplate = PodTemplateDescriptor('liste', 'Liste des points')
agendaListeTemplate.podTemplate = 'meetingandennenewlist.odt'
agendaListeTemplate.podCondition = 'python:(here.meta_type=="Meeting") and (here.portal_membership.getAuthenticatedMember().has_role("MeetingManager") or here.portal_membership.getAuthenticatedMember().has_role("MeetingPowerObserver"))'




collegeTemplates = [itemNoteTemplate, decisionsTemplate,
                    agendaTemplate, agendalateTemplate,
                    itemDeliberationTemplate, itemProjectTemplate,
                    agendaPersTemplate, agendaPersLateTemplate, agendaCpasTemplate,agendaCpasLateTemplate,agendaListeTemplate]


# Users and groups -------------------------------------------------------------
adrlar= UserDescriptor ('adrlar', [],email='adrien.laruelle@ac.andenne.be', fullname='Adrien Laruelle')
ale= UserDescriptor ('ale', [],email='ale@andenne.be', fullname='A.L.E.')
alebok= UserDescriptor ('alebok', [],email='Alexandre.Bokor@ac.andenne.be', fullname='Alexandre Bokor')
aledep= UserDescriptor ('aledep', [],email='andenne2@andenne.be', fullname='Alexandre Depaye')
alithi= UserDescriptor ('alithi', [],email='aline.thiry@ac.andenne.be', fullname='Aline Thiry')
andbea= UserDescriptor ('andbea', [],email='andre.beaujean@ac.andenne.be', fullname='André Beaujean')
andlal= UserDescriptor ('andlal', [],email='Andree-Marie.Lallemend@ac.andenne.be', fullname='André-Marie Lallemend')
angmon= UserDescriptor ('angmon', [],email='angelique.monetat@ac.andenne.be', fullname='Angélique Monetat')
aniduf= UserDescriptor ('aniduf', [],email='anita.dufour@ac.andenne.be', fullname='Anita Dufour')
anncol= UserDescriptor ('anncol', [],email='anne-sophie.collet@andenne.be', fullname='Anne-Sophie Collet')
anndes= UserDescriptor ('anndes', [],email='annick.destree@ac.andenne.be', fullname='Annick Destrée')
anngof= UserDescriptor ('anngof', [],email='anne.goffin@ac.andenne.be', fullname='Anne Goffin')
annipp= UserDescriptor ('annipp', [],email='Annick.Ippersiel@ac.andenne.be', fullname='Annick Ippersiel')
annlem= UserDescriptor ('annlem', [],email='anne-francoise.lemaitre@ac.andenne.be', fullname='Anne-Françoise Lemaitre')
annmel= UserDescriptor ('annmel', [],email='anne.mella@ac.andenne.be', fullname='Anne Mella')
arnada= UserDescriptor ('arnada', [],email='arnaud.adam@ac.andenne.be', fullname='Arnaud Adam')
audbio= UserDescriptor ('audbio', [],email='audrey.bion@ac.andenne.be', fullname='Audrey Bion')
aurbau= UserDescriptor ('aurbau', [],email='aurore.bauvir@ac.andenne.be', fullname='Aurore Bauvir')
aurgod= UserDescriptor ('aurgod', [],email='aurelie.godinas@ac.andenne.be', fullname='Aurélie Godinas')
aurkem= UserDescriptor ('aurkem', [],email='Aurelie.Kempeneers@ac.andenne.be', fullname='Aurélie Kempeneers')
axegas= UserDescriptor ('axegas', [],email='axel.gaspard@ac.andenne.be', fullname='Axel Gaspard')
bazfal= UserDescriptor ('bazfal', [],email='bazilette.falonne@ac.andenne.be', fullname='Bazilette Falonne')
bencos= UserDescriptor ('bencos', [],email='benjamin.costantini@ac.andenne.be', fullname='Benjamin Costantini')
benlal= UserDescriptor ('benlal', [],email='amaury.braeckman@ac.andenne.be', fullname='Amaury Braeckman')
benrou= UserDescriptor ('benrou', [],email='benoit.rousseau@ac.andenne.be', fullname='Benoit Rousseau')
britim= UserDescriptor ('britim', [],email='brigitte.timsonnet@ac.andenne.be', fullname='Brigitte Timsonnet')
cardor= UserDescriptor ('cardor', [],email='carine.dormal@ac.andenne.be', fullname='Carine Dormal')
carvuy= UserDescriptor ('carvuy', [],email='carvuy@ac.andenne.be', fullname='Carine Vuylsteke')
catlam= UserDescriptor ('catlam', [],email='catherine.lambert@ac.andenne.be', fullname='Catherine Lambert')
cattim= UserDescriptor ('cattim', [],email='Catherine.Timsonet@ac.andenne.be', fullname='Catherine Timsonet')
ceccro= UserDescriptor ('ceccro', [],email='Cecile.Crossart@ac.andenne.be', fullname='Cecile Crossart')
celpir= UserDescriptor ('celpir', [],email='celine.pirard@ac.andenne.be', fullname='Céline Pirard')
chagil= UserDescriptor ('chagil', [],email='chantal.gillart@publilink.be', fullname='Chantal Gillart')
chamor= UserDescriptor ('chamor', [],email='Chamor@ac.andenne.be', fullname='Chantal Moreau')
chawin= UserDescriptor ('chawin', [],email='charly.windal@ac.andenne.be', fullname='Charly Windal')
chrbon= UserDescriptor ('chrbon', [],email='christel.bonmariage@ac.andenne.be', fullname='Christel Bonmariage')
chrbox= UserDescriptor ('chrbox', [],email='christine.boxho@ac.andenne.be', fullname='Christine Boxho')
chrcol= UserDescriptor ('chrcol', [],email='Christiane.Colette@ac.andenne.be', fullname='Chritiane Colette')
chrdie= UserDescriptor ('chrdie', [],email='christine.diet@ac.andenne.be', fullname='Christine Diet')
chrhus= UserDescriptor ('chrhus', [],email='christian.husson@andenne.be', fullname='Christian.husson')
chrmal= UserDescriptor ('chrmal', [],email='christian.malisoux@ac.andenne.be', fullname='Christian Malisoux')
chrpir= UserDescriptor ('chrpir', [],email='andenne3@andenne.be', fullname='Christophe Pirson')
claeer= UserDescriptor ('claeer', [],email='claude.eerdekens@ac.andenne.be', fullname='Claude Eerdekens')
clamaq= UserDescriptor ('clamaq', [],email='claude.maquigny@andenne.be', fullname='Claude Maquigny')
claspr= UserDescriptor ('claspr', [],email='claudia.sprimont@ac.andenne.be', fullname='Claudia Sprimont')
classement= UserDescriptor ('classement', [],email='classement@ac.andenne.be', fullname='Classement')
college= UserDescriptor ('college', [],email='college@ac.andenne.be', fullname='Collège Communal')
corcoz= UserDescriptor ('corcoz', [],email='eic@andenne.be', fullname='Corinne Cozier')
corkir= UserDescriptor ('corkir', [],email='coryse.kiriluk@ac.andenne.be', fullname='Coryse Kiriluk')
corman= UserDescriptor ('corman', [],email='coralie.mengal@andene.be', fullname='Coralie Mengal')
corwya= UserDescriptor ('corwya', [],email='Corinne.Wyard@ac.andenne.be', fullname='Corinne Wyard')
czarches= UserDescriptor ('czarches', [],email='stephane.carpentier@ac.andenne.be', fullname='C.Z. ZP des Arches')
didabr= UserDescriptor ('didabr', [],email='mieuxvivre@ac.andenne.be', fullname='Didier Abraham')
didgos= UserDescriptor ('didgos', [],email='didier.gosset@ac.andenne.be', fullname='Didier Gosset')
dimpar= UserDescriptor ('dimpar', [],email='dimitri.paris@andenne.be', fullname='Dimitri Paris')
domlef= UserDescriptor ('domlef', [],email='Dominique.Lefevre@ac.andenne.be', fullname='Dominique Lefevre')
echevins= UserDescriptor ('echevins', [],email='echevins@ac.andenne.be', fullname='Echevins')
eddhan= UserDescriptor ('eddhan', [],email='eddy.hanoul@ac.andenne.be', fullname='Eddy Hanoul')
eic= UserDescriptor ('eic', [],email='eic@andenne.be', fullname='Ecole Industrielle')
elimal= UserDescriptor ('elimal', [],email='elisabeth.malisoux@ac.andenne.be', fullname='Elisabeth Malisoux')
emimac= UserDescriptor ('emimac', [],email='emilie.macaux@cs.andenne.be', fullname='Emilie macaux')
eridon= UserDescriptor ('eridon', [],email='Eric.Donnay@ac.andenne.be', fullname='Eric Donnay')
erimor= UserDescriptor ('erimor', [],email='eric.moreau@ac.andenne.be', fullname='Eric Moreau')
eriper= UserDescriptor ('eriper', [],email='Eric.Perwez@ac.andenne.be', fullname='Eric Perwez')
eripir= UserDescriptor ('eripir', [],email='virginie.demarche@ac.andenne.be', fullname='Eric Pirard')
eritie= UserDescriptor ('eritie', [],email='eric.etienne@ac.andenne.be', fullname='Eric Etienne')
fabdel= UserDescriptor ('fabdel', [],email='severine.roquet@ac.andenne.be', fullname='Severine Roquet')
fabmar= UserDescriptor ('fabmar', [],email='fabio.marcuzzi@ac.andenne.be', fullname='Fabio Marcuzzi')
fabmau= UserDescriptor ('fabmau', [],email='fabienne.mauguit@ac.andenne.be', fullname='Fabienne Mauguit')
fabnoe= UserDescriptor ('fabnoe', [],email='eic@andenne.be', fullname='Fabien Noé')
fabsen= UserDescriptor ('fabsen', [],email='Fabien.Senterre@ac.andenne.be', fullname='Fabien Senterre')
fannic= UserDescriptor ('fannic', [],email='fanny.nicolas@ac.andenne.be', fullname='Fanny Nicolas')
fiosco= UserDescriptor ('fiosco', [],email='fiona.scott@ac.andenne.be', fullname='Fiona Scott')
flolou= UserDescriptor ('flolou', [],email='floriane.louis@ac.andenne.be', fullname='Floriane Louis')
fraboc= UserDescriptor ('fraboc', [],email='francois.boclinville@ac.andenne.be', fullname='François Boclinville')
fracol= UserDescriptor ('fracol', [],email='francoise.collard@ac.andenne.be', fullname='Françoise Collard')
fraleo= UserDescriptor ('fraleo', [],email='francoise.leonard@ac.andenne.be', fullname='Françoise Léonard')
fralux= UserDescriptor ('fralux', [],email='fx.lux@andenne.be', fullname='François-Xavier Lux')
framou= UserDescriptor ('framou', [],email='francoise.moureau@ac.andenne.be', fullname='Françoise Moureau')
frasma= UserDescriptor ('frasma', [],email='Francois.smal@ac.andenne.be', fullname='François Smal')
fraver= UserDescriptor ('fraver', [],email='fraver@ac.andenne.be', fullname='Francis Verborg')
frawil= UserDescriptor ('frawil', [],email='Francine.Wilemme@ac.andenne.be', fullname='Francine Wilemme')
frebel= UserDescriptor ('frebel', [],email='Frederic.Belche@andenne.be', fullname='Frédéric Belche')
frebou= UserDescriptor ('frebou', [],email='andenne2@andenne.be', fullname='Fréderic Bouvier')
gaecur= UserDescriptor ('gaecur', [],email='gaelle.curvers@ac.andenne.be', fullname='Gaëlle Curvers')
genanc= UserDescriptor ('genanc', [],email='genevieve.anciaux@ac.andenne.be', fullname='Genevieve Anciaux')
gerdef= UserDescriptor ('gerdef', [],email='gerard.defrance@andenne.be', fullname='Gerard de France')
ginhen= UserDescriptor ('ginhen', [],email='prosoc.andenne@sec.cfwb.be', fullname='Virginie Henriet')
guilej= UserDescriptor ('guilej', [],email='guillaume.lejeune@ac.andenne.be', fullname='Guillaume Lejeune')
guyhav= UserDescriptor ('guyhav', [],email='guy.havelange@ac.andenne.be', fullname='Guy Havelange')
hasouc= UserDescriptor ('hasouc', [],email='hassan.ouchan@andenne.be', fullname='Hassan Ouchan')
helmey= UserDescriptor ('helmey', [],email='Helene.Meyfroidt@ac.andenne.be', fullname='Hélène Meyfroidt')
helrou= UserDescriptor ('helrou', [],email='heloise.rouard@andenne.be', fullname='Héloise Rouard')
houmag= UserDescriptor ('houmag', [],email='houria.maghouti@ac.andenne.be', fullname='Houria Maghouti')
ingiur= UserDescriptor ('ingiur', [],email='ingrid.iuretig@ac.andenne.be', fullname='Ingrid Iuretig')
isades= UserDescriptor ('isades', [],email='Isabelle.destree@ac.andenne.be', fullname='Isabelle Destrée')
ismbou= UserDescriptor ('ismbou', [],email='ismail.boukhari@ac.andenne.be', fullname='Ismail boukhari')
jadbri= UserDescriptor ('jadbri', [],email='jade.brichard@ac.andenne.be', fullname='Jade Brichard')
jeadel= UserDescriptor ('jeadel', [],email='andenne3@ac.andenne.be', fullname='Jeanne Delaite')
jeamaq= UserDescriptor ('jeamaq', [],email='Jean-Marie.Maquigny@ac.andenne.be', fullname='Jean-Marie Maquigny')
jeamat= UserDescriptor ('jeamat', [],email='jean-marie.mattart@ac.andenne.be', fullname='Jean-Marie Mattart')
jeawar= UserDescriptor ('jeawar', [],email='Jean-Paul.Warzee@ac.andenne.be', fullname='Jean-Paul Warzée')
jerdup= UserDescriptor ('jerdup', [],email='jeremie.dupont@ac.andenne.be', fullname='Jérémie Dupont')
jerpir= UserDescriptor ('jerpir', [],email='jerome.pirsoul@ac.andenne.be', fullname='Jerome Pirsoul')
joelig= UserDescriptor ('joelig', [],email='joelle.ligot@cs.andenne.be', fullname='Joelle Ligot')
joewar= UserDescriptor ('joewar', [],email='joelle.warzee@ac.andenne.be', fullname='Joelle Warzee')
julchi= UserDescriptor ('julchi', [],email='julie.chiaradia@cs.andenne.be', fullname='Julie Chiaradia')
juldel= UserDescriptor ('juldel', [],email='Julie.Delhaise@ac.andenne.be', fullname='Julie Delhaise')
juldre= UserDescriptor ('juldre', [],email='julien.dresse@ac.andenne.be', fullname='Julien Dresse')
kambel= UserDescriptor ('kambel', [],email='kamilia.belhachmi@ac.andenne.be', fullname='Kamilia Belhachmi')
karnaj= UserDescriptor ('karnaj', [],email='karima.naji@ac.andenne.be', fullname='Karima Naji')
laeste= UserDescriptor ('laeste', [],email='Laetitia.Steylemans@ac.andenne.be', fullname='Laetitia Steylemans')
laudel= UserDescriptor ('laudel', [],email='laurent.delbrouck@ac.andenne.be', fullname='Laurent Delbrouck')
lauhan= UserDescriptor ('lauhan', [],email='laurence.hanneuse@ac.andenne.be', fullname='Laurence Hanneuse')
lauhoc= UserDescriptor ('lauhoc', [],email='laurence.hoche@andenne.be', fullname='Laurence Hoche')
lenvol= UserDescriptor ('lenvol', [],email='lenvol@andenne.be', fullname="L'envol")
leohau= UserDescriptor ('leohau', [],email='leon.j.hauregard@ceramandenne.be', fullname='Léon Hauregard')
logcas= UserDescriptor ('logcas', [],email='logan.casimir@ac.andenne.be', fullname='Logan Casimir')
louanc= UserDescriptor ('louanc', [],email='louis.anciaux@ac.andenne.be', fullname='Louis Anciaux')
lusdon= UserDescriptor ('lusdon', [],email='lusine.yeg@ac.andenne.be', fullname='Lusine YEGHIAZARYAN')
lydmot= UserDescriptor ('lydmot', [],email='Lydia.Motte@ac.andenne.be', fullname='Lydia Motte')
marant12= UserDescriptor ('marant12', [],email='marie.anthone@ac.andenne.be', fullname='Marie Anthone')
marauq= UserDescriptor ('marauq', [],email='marie-rose.auquier@andenne.be', fullname='Marie-Rose Auquier')
marbeg= UserDescriptor ('marbeg', [],email='Maryline.Beguin@ac.andenne.be', fullname='Maryline Beguin')
marbel= UserDescriptor ('marbel', [],email='Marie-anne.Belleflamme@ac.andenne.be', fullname='Marie-Anne Belleflamme')
marcar= UserDescriptor ('marcar', [],email='marylene.carrier@ac.andenne.be', fullname='Marylène Carrier')
marcla= UserDescriptor ('marcla', [],email='marc.clajot@ac.andenne.be', fullname='Marc Clajot')
mardeg= UserDescriptor ('mardeg', [],email='Marc.degreef@ac.andenne.be', fullname='Marc Degreef')
marjam= UserDescriptor ('marjam', [],email='marie.jamart@ac.andenne.be', fullname='Marie Jamart')
marmag= UserDescriptor ('marmag', [],email='marc.magnier@ac.andenne.be', fullname='Marc Magnier')
marmat= UserDescriptor ('marmat', [],email='jean-marie.mathieu@cpas-andenne.be', fullname='Jean-Marie Mathieu')
marmoi= UserDescriptor ('marmoi', [],email='biblio@andenne.be', fullname='Marc moisse')
marorb= UserDescriptor ('marorb', [],email='marie.orban@ac.andenne.be', fullname='Marie Orban')
marron= UserDescriptor ('marron', [],email='marc.ronveaux@ac.andenne.be', fullname='Marc Ronveaux')
marrou= UserDescriptor ('marrou', [],email='Mariette.roup@ac.andenne.be', fullname='Mariette roup')
marser= UserDescriptor ('marser', [],email='Marianne.Servais@ac.andenne.be', fullname='Marianne Servais')
martho= UserDescriptor ('martho', [],email='marie-christine.thola@ac.andenne.be', fullname='Marie-Christine Thola')
matdan= UserDescriptor ('matdan', [],email='mathilde.danze@ac.andenne.be', fullname='Mathilde Danze')
meldeg= UserDescriptor ('meldeg', [],email='melanie.degroote@ac.andenne.be', fullname='Mélanie Degroote')
micdec= UserDescriptor ('micdec', [],email='michel.dechamps@ac.andenne.be', fullname='Michel Dechamps')
micmuk= UserDescriptor ('micmuk', [],email='Micheline.mukazayire@ac.andenne.be', fullname='Micheline MUKAZAYIRE')
micwil= UserDescriptor ('micwil', [],email='Michel.Willem@ac.andenne.be', fullname='Michèle Willem')
muscer= UserDescriptor ('muscer', [],email='musee.ceramique@andenne.be', fullname='Musée de la Céramque')
nandol= UserDescriptor ('nandol', [],email='nancy.dolce@ac.andenne.be', fullname='Nancy Dolce')
natfra= UserDescriptor ('natfra', [],email='natacha.francois@ac.andenne.be', fullname='Natacha François')
natleb= UserDescriptor ('natleb', [],email='nathalie.lebrun@ac.andenne.be', fullname='Nathalie Lebrun')
natlef= UserDescriptor ('natlef', [],email='nathalie.lefrant@andenne.be', fullname='Nathalie Lefrant')
natrut= UserDescriptor ('natrut', [],email='nathalie.ruth@ac.andenne.be', fullname='Nathalie Ruth')
nicdel= UserDescriptor ('nicdel', [],email='nicole.delforge@cs.andenne.be', fullname='Nicole Delforge')
nicpar= UserDescriptor ('nicpar', [],email='nicole.parisel@andenne.be', fullname='Nicole Parisel')
noedef= UserDescriptor ('noedef', [],email='noella.defer@ac.andenne.be', fullname='Noëlla Defer')
noelej= UserDescriptor ('noelej', [],email='Noella.Lejeune@ac.andenne.be', fullname='Noella Lejeune')
oansto= UserDescriptor ('oansto', [],email='oana.stoica@ac.andenne.be', fullname='Oana Stoica')
olicam= UserDescriptor ('olicam', [],email='olivier.campagne@ac.andenne.be', fullname='Olivier Campagne')
oxaale= UserDescriptor ('oxaale', [],email='oxana.alexeeva@cs.andenne.be', fullname='Oxana Alexeeva')
paoven= UserDescriptor ('paoven', [],email='paola.venica@cs.andenne.be', fullname='Paola Venica')
pashen= UserDescriptor ('pashen', [],email='pascale.hennaux@ac.andenne.be', fullname='Pascale Hennaux')
pasmon= UserDescriptor ('pasmon', [],email='Pascal.Monjoie@ac.andenne.be', fullname='Pascal Monjoie')
paster= UserDescriptor ('paster', [],email='Pascal.Terwagne@ac.andenne.be', fullname='Pascal Terwagne')
pasvan= UserDescriptor ('pasvan', [],email='pascale.vanmechelen@ac.andenne.be', fullname='Pascale Vanmechelen')
patarn= UserDescriptor ('patarn', [],email='Patricia.Arnold@ac.andenne.be', fullname='Patricia Arnold')
patgor= UserDescriptor ('patgor', [],email='patrik.goreta@ac.andenne.be', fullname='Patrik Goreta')
pattho= UserDescriptor ('pattho', [],email='patrick-thomas@andenne.be', fullname='Patrick Thomas')
pauvan= UserDescriptor ('pauvan', [],email='paulette.vangangel@andenne.be', fullname='Paulette Vangangel')
pavcor= UserDescriptor ('pavcor', [],email='pavlos.corexenos@ac.andenne.be', fullname='Pavlos Corexenos')
phicre= UserDescriptor ('phicre', [],email='Philippe.Crefcoeur@ac.andenne.be', fullname='Philippe Crefcoeur')
phipir= UserDescriptor ('phipir', [],email='sageiss@ac.andenne.be', fullname='Philippe Pironet')
phiros= UserDescriptor ('phiros', [],email='Philippe.Rose@ac.andenne.be', fullname='Philippe Rose')
piefon= UserDescriptor ('piefon', [],email='pierre.fontaine@ac.andenne.be', fullname='Pierre Fontaine')
piemin= UserDescriptor ('piemin', [],email='pierre.minnaert@andenne.be', fullname='Pierre Minnaert')
pievan= UserDescriptor ('pievan', [],email='pierre.vanpaeschen@ac.andenne.be', fullname='Pierre Vanpaeschen')
promandenne= UserDescriptor ('promandenne', [],email='info@promandenne.be', fullname='Promandenne')
ritlam= UserDescriptor ('ritlam', [],email='Rita.Lambert@ac.andenne.be', fullname='Rita Lambert')
robgob= UserDescriptor ('robgob', [],email='robert.gobin@ac.andenne.be', fullname='Robert Gobin')
robhoe= UserDescriptor ('robhoe', [],email='robert.hoeymakers@andenne.be', fullname='Robert Hoeymakers')
roboscan= UserDescriptor ('roboscan', [],email='roboscan@ac.andenne.be', fullname='Robotscanner')
roldan= UserDescriptor ('roldan', [],email='roland.dantine@ac.andenne.be', fullname='Roland Dantine')
roldes= UserDescriptor ('roldes', [],email='Rolande.Despagne@ac.andenne.be', fullname='Rolande Despagne')
rongos= UserDescriptor ('rongos', [],email='Ronald.Gossiaux@ac.andenne.be', fullname='Ronald Gossiaux')
rudnsi= UserDescriptor ('rudnsi', [],email='rudy.n@andenne.be', fullname='Rudy Nsingi')
sabwer= UserDescriptor ('sabwer', [],email='sabine.wernerus@ac.andenne.be', fullname='Sabine Wernerus')
sancru= UserDescriptor ('sancru', [],email='sandrine.cruspin@ac.andenne.be', fullname='Sandrine Cruspin')
sangri= UserDescriptor ('sangri', [],email='Sandrine.Gris@ac.andenne.be', fullname='Sandrine Gris')
sanpar= UserDescriptor ('sanpar', [],email='sandrine.parisseaux@ac.andenne.be', fullname='Sandrine Parisseaux')
sanric= UserDescriptor ('sanric', [],email='sandrine.ricaille@ac.andenne.be', fullname='Sandrine Ricaille')
sebron= UserDescriptor ('sebron', [],email='sebastien.ronveaux@ac.andenne.be', fullname='Sébastien Ronveaux')
simgre= UserDescriptor ('simgre', [],email='simon.gregoire@ac.andenne.be', fullname='Simon Gregoire')
simlam= UserDescriptor ('simlam', [],email='simon.lambrecht@ac.andenne.be', fullname='Simon Lambrecht')
simler= UserDescriptor ('simler', [],email='simon.leroy@andenne.be', fullname='Simon Leroy')
sopben= UserDescriptor ('sopben', [],email='sophie.benetti@cs.andenne.be', fullname='Sophie Benetti')
sopfra= UserDescriptor ('sopfra', [],email='Sophie.Fraikin@ac.andenne.be', fullname='Sophie Fraikin')
sophan= UserDescriptor ('sophan', [],email='sophie.hannot@cs.andenne.be', fullname='Sophie Hannot')
stafin= UserDescriptor ('stafin', [],email='stafin@ac.andenne.be', fullname='Stagiaire Finances')
stajur= UserDescriptor ('stajur', [],email='stajur@ac.andenne.be', fullname='Stagiaire Juridique')
stasec= UserDescriptor ('stasec', [],email='stasec@ac.andenne.be', fullname='Stagiaire Secrétariat')
stebad= UserDescriptor ('stebad', [],email='stephanie.badot@ac.andenne.be', fullname='Stéphanie Badot')
stechi= UserDescriptor ('stechi', [],email='stephanie.chiaradia@ac.andenne.be', fullname='Stéphanie Chiaradia')
stecol= UserDescriptor ('stecol', [],email='stephane.collignon@cs.andenne.be', fullname='Stephane')
stedew= UserDescriptor ('stedew', [],email='stephanie.dewez@ac.andenne.be', fullname='Stéphanie Dewez')
stepre= UserDescriptor ('stepre', [],email='stephanie.preudhomme@cs.andenne.be', fullname="Stéphnaie Preud'homme")
syldom= UserDescriptor ('syldom', [],email='sylvie.domine@ac.andenne.be', fullname='Sylvie Dominé')
tatcha= UserDescriptor ('tatcha', [],email='tatiana.charlier@andenne.be', fullname='Tatiana Charlier')
tinmal= UserDescriptor ('tinmal', [],email='christine.malherbe@ac.andenne.be', fullname='Christine Malherbe')
userC1= UserDescriptor ('userC1', [],email='userC1@ac.andenne.be', fullname='userC1')
userP1= UserDescriptor ('userP1', [],email='userP1@ac.andenne.be', fullname='userP1')
usertest= UserDescriptor ('usertest', [],email='fabio.marcuzzi@ac.andenne.be', fullname='usetest')
usertest2= UserDescriptor ('usertest2', [],email='fabio.marcuzzi@andenne.be', fullname='usertest')
valdeg= UserDescriptor ('valdeg', [],email='valentine.degrave@ac.andenne.be', fullname='Valentine De Grave')
valduc= UserDescriptor ('valduc', [],email='Valerie.Duchesne@ac.andenne.be', fullname='Valérie Duchesne')
valevr= UserDescriptor ('valevr', [],email='valentine.evrard@ac.andenne.be', fullname='Valentine Evrard')
valnie= UserDescriptor ('valnie', [],email='valerie.nieus@andenne.be', fullname='Valerie Nieus')
verper= UserDescriptor ('verper', [],email='veronique.perpinien@ac.andenne.be', fullname='Veronique Perpinien')
vinbou= UserDescriptor ('vinbou', [],email='Vincent.bouret@ac.andenne.be', fullname='Vincent Bouret')
vinsam= UserDescriptor ('vinsam', [],email='Vincent.Sampaoli@ac.andenne.be', fullname='Vincent Sampaoli')
virdem= UserDescriptor ('virdem', [],email='virginie.demarche@ac.andenne.be', fullname='Virginie Demarche')
virhen= UserDescriptor ('virhen', [],email='virginie.hentiens@ac.andenne.be', fullname='Virginie Hentiens')
vivmat= UserDescriptor ('vivmat', [],email='viviane.matagne@ac.andenne.be', fullname='Viviane Matagne')
xaveer= UserDescriptor ('xaveer', [],email='xavier.eerdekens@cs.andenne.be', fullname='Xavier Eerdekens')
xavwil= UserDescriptor ('xavwil', [],email='xavier.willot@ac.andenne.be', fullname='Xavier Willot')
yahben= UserDescriptor ('yahben', [],email='yahya.benhaddou@andenne.be', fullname='Yahya Benhaddou')
yandeg= UserDescriptor ('yandeg', [],email='andenne1@andenne.be', fullname='Yannick Degée')
yassca= UserDescriptor ('yassca', [],email='Yasmine.Scantamburlo@ac.andenne.be', fullname='Yasmine Scantamburlo')
yastuz= UserDescriptor ('yastuz', [],email='yasemin.tuzkan@ac.andenne.be', fullname='Yasémin Tuzkan')
yvagem= UserDescriptor ('yvagem', [],email='Yvan.Gemine@ac.andenne.be', fullname='Yvan Gemine')
yvesor= UserDescriptor ('yvesor', [],email='yves.soree@ac.andenne.be', fullname='Yves Soree')
zonet= UserDescriptor ('zonet', [],email='zonet@andenne.be', fullname='Zone T')

emetteuravisPers = UserDescriptor('emetteuravisPers', [], email="test@test.be", fullname="Emetteur avis Personnel")


groups = [
GroupDescriptor('a-l-e', 'A.L.E.', 'ALE'),
GroupDescriptor('accueil-extra-scolaire', 'accueil extra scolaire', 'aec'),
GroupDescriptor('adl', 'Adl', 'ADL'),
GroupDescriptor('cabinet-soree', 'Bibliotheca ANDANA', 'cab_Soree'),
GroupDescriptor('bibliotheque', 'Bibliothèque', 'Biblio'),
GroupDescriptor('cabinet-costantini', 'Cabinet Costantini', 'Cab_cos'),
GroupDescriptor('cabinet-cruspin', 'Cabinet Cruspin', 'cab_cruspin'),
GroupDescriptor('cabinet-dechamps', 'Cabinet Dechamps', 'Cab_dechamps'),
GroupDescriptor('cabinet-du-bourgmestre', 'Cabinet du Bourgmestre', 'Cab_bg'),
GroupDescriptor('cabinet-havelange', 'Cabinet Havelange', 'cab_Havelange'),
GroupDescriptor('cabinet-leonard-1', 'Cabinet Leonard', 'cab_leo'),
GroupDescriptor('cabinet-malisoux', 'Cabinet Malisoux', 'Cab_malisoux'),
GroupDescriptor('cabinet-sampaoli', 'Cabinet Sampaoli', 'Cab_sampaoli'),
GroupDescriptor('comite-de-direction', 'Comité de Direction', 'comdir'),
GroupDescriptor('cpas', 'Cpas', 'cpas'),
GroupDescriptor('directeur-s.c.l-rongos', 'Directeur S.C.L (rongos)', 'dirscl'),
GroupDescriptor('service-des-travaux', 'Direction des services techniques', 'TRAV'),
GroupDescriptor('echevins', 'Echevins', 'echevins'),
GroupDescriptor('ecole-industrielle', 'Ecole industrielle', 'EIC'),
GroupDescriptor('enseignement', 'Enseignement', 'Enseignement'),
GroupDescriptor('cabinet-verborg', 'F. Verborg - Président du Conseil', 'Cab_bg_verborg'),
GroupDescriptor('musee-de-la-ceramique', 'Musée de la Céramique', 'Musee'),
GroupDescriptor('police', 'police', 'Police'),
GroupDescriptor('promandenne', 'Promandenne', 'promandenne'),
GroupDescriptor('qualite-habitat', 'Qualité habitat', 'qualitehabitat'),
GroupDescriptor('complexe-sportif', 'Régie des Sports', 'Complexe'),
GroupDescriptor('zonet', 'Sageiss', 'ZoneT'),
GroupDescriptor('secretariat', 'Secretariat général', 'Secretariat'),
GroupDescriptor('service-assurances ', 'Service assurances ', 'servassurance'),
GroupDescriptor('service-carriere', 'Service Carrière', 'carriere'),
GroupDescriptor('service-cellule-logistique-r-gobin', 'Service cellule logistique (R. Gobin)', 'cellog'),
GroupDescriptor('service-culture', 'Service culture', 'Culture'),
GroupDescriptor('service-acte', 'Service de cohésion sociale', 'Acte'),
GroupDescriptor('personnel', 'Service du personnel', 'Personnel'),
GroupDescriptor('service-emploi', 'Service emploi', 'Emploi'),
GroupDescriptor('service-environnement', 'Service environnement', 'Environnement'),
GroupDescriptor('service-festivites', 'Service festivites', 'Festivites'),
GroupDescriptor('service-finances', 'Service Finances', 'Finances'),
GroupDescriptor('informatique', 'Service informatique', 'Informatique'),
GroupDescriptor('service-juridique', 'Service juridique', 'SJ'),
GroupDescriptor('service-juridique-oc', 'Service juridique (OC)', 'SJOC'),
GroupDescriptor('service-juridique-pt', 'Service juridique (PT)', 'SJPT'),
GroupDescriptor('service-juridique-vb', 'Service juridique (VB)', 'SJVB'),
GroupDescriptor('service-patrimoine', 'Service patrimoine', 'Patrimoine'),
GroupDescriptor('service-plaine', 'Service Plaine', 'plaine'),
GroupDescriptor('service-population', 'Service population', 'Population'),
GroupDescriptor('service-relations-publiques', 'Service Relations Publiques', 'Relpub'),
GroupDescriptor('service-tourisme', 'Service tourisme', 'Tourisme'),
GroupDescriptor('service-urbanisme', 'Service Urbanisme', 'Urbanisme'),
GroupDescriptor('prevention', 'SIPP', 'SIPP'),
GroupDescriptor('sri', 'SRI', 'SRI'),
GroupDescriptor('copy_of_zonet', 'Yasémin Tuzkan (Cabinet BG)', 'yastuz'),
]

# MeetingManager
groups[32].creators.append(adrlar)
groups[32].observers.append(adrlar)
groups[0].observers.append(ale)
groups[0].advisers.append(ale)
groups[32].observers.append(alebok)
groups[37].creators.append(andbea)
groups[37].observers.append(andbea)
groups[32].observers.append(angmon)
groups[31].creators.append(angmon)
groups[7].reviewers.append(angmon)
groups[32].reviewers.append(angmon)
groups[17].advisers.append(angmon)
groups[5].advisers.append(angmon)
groups[5].observers.append(angmon)
groups[31].reviewers.append(angmon)
groups[32].pvwriters.append(angmon)
groups[31].observers.append(angmon)
groups[32].creators.append(angmon)
groups[5].reviewers.append(angmon)
groups[32].advisers.append(angmon)
groups[31].advisers.append(angmon)
groups[7].advisers.append(angmon)
groups[45].advisers.append(anndes)
groups[45].creators.append(anndes)
groups[45].reviewers.append(anndes)
groups[45].observers.append(anndes)
groups[48].creators.append(anngof)
groups[48].observers.append(anngof)
groups[20].observers.append(annipp)
groups[20].advisers.append(annipp)
groups[17].advisers.append(annipp)
groups[10].advisers.append(annipp)
groups[33].observers.append(annipp)
groups[10].reviewers.append(annipp)
groups[10].observers.append(annipp)
groups[20].reviewers.append(annipp)
groups[33].creators.append(annipp)
groups[27].observers.append(annlem)
groups[27].reviewers.append(annlem)
groups[27].creators.append(annlem)
groups[42].creators.append(annlem)
groups[14].creators.append(annlem)
groups[42].observers.append(annlem)
groups[14].observers.append(annlem)
groups[26].observers.append(annmel)
groups[26].advisers.append(annmel)
groups[26].creators.append(annmel)
groups[37].observers.append(arnada)
groups[37].creators.append(audbio)
groups[37].observers.append(audbio)
groups[24].observers.append(aurbau)
groups[24].advisers.append(aurbau)
groups[24].creators.append(aurbau)
groups[26].observers.append(aurgod)
groups[26].creators.append(aurgod)
groups[5].reviewers.append(bencos)
groups[31].advisers.append(bencos)
groups[5].observers.append(bencos)
groups[5].advisers.append(bencos)
groups[31].observers.append(bencos)
groups[17].advisers.append(bencos)
groups[33].advisers.append(benlal)
groups[33].creators.append(benlal)
groups[33].observers.append(benlal)
groups[48].creators.append(benrou)
groups[48].observers.append(benrou)
groups[17].advisers.append(britim)
groups[12].reviewers.append(britim)
groups[12].observers.append(britim)
groups[12].advisers.append(britim)
groups[45].creators.append(cardor)
groups[44].advisers.append(carvuy)
groups[36].creators.append(carvuy)
groups[44].creators.append(carvuy)
groups[47].creators.append(carvuy)
groups[47].advisers.append(carvuy)
groups[17].advisers.append(carvuy)
groups[44].observers.append(carvuy)
groups[44].reviewers.append(carvuy)
groups[11].advisers.append(carvuy)
groups[47].observers.append(carvuy)
groups[36].advisers.append(carvuy)
groups[36].observers.append(carvuy)
groups[17].advisers.append(catlam)
groups[6].reviewers.append(catlam)
groups[6].observers.append(catlam)
groups[6].advisers.append(catlam)
groups[46].creators.append(ceccro)
groups[46].observers.append(ceccro)
groups[32].observers.append(celpir)
groups[6].creators.append(celpir)
groups[6].advisers.append(celpir)
groups[17].advisers.append(celpir)
groups[6].reviewers.append(celpir)
groups[32].advisers.append(celpir)
groups[6].observers.append(celpir)
groups[14].creators.append(chagil)
groups[14].observers.append(chagil)
groups[27].observers.append(chamor)
groups[27].reviewers.append(chamor)
groups[27].creators.append(chamor)
groups[48].creators.append(chrbox)
groups[48].observers.append(chrbox)
groups[37].creators.append(chrdie)
groups[38].reviewers.append(chrmal)
groups[38].advisers.append(chrmal)
groups[38].creators.append(chrmal)
groups[38].observers.append(chrmal)
groups[19].creators.append(chrpir)
groups[19].observers.append(chrpir)
groups[17].advisers.append(claeer)
groups[8].observers.append(claeer)
groups[8].advisers.append(claeer)
groups[6].creators.append(claspr)
groups[6].advisers.append(claspr)
groups[17].advisers.append(claspr)
groups[6].reviewers.append(claspr)
groups[6].observers.append(claspr)
groups[18].advisers.append(corcoz)
groups[18].creators.append(corcoz)
groups[18].observers.append(corcoz)
groups[24].reviewers.append(corkir)
groups[24].observers.append(corkir)
groups[24].advisers.append(corkir)
groups[24].creators.append(corkir)
groups[18].advisers.append(corman)
groups[18].creators.append(corman)
groups[18].observers.append(corman)
groups[32].observers.append(corwya)
groups[26].observers.append(corwya)
groups[32].reviewers.append(corwya)
groups[26].reviewers.append(corwya)
groups[32].creators.append(corwya)
groups[32].advisers.append(corwya)
groups[22].reviewers.append(czarches)
groups[22].creators.append(czarches)
groups[22].observers.append(czarches)
groups[22].pvwriters.append(czarches)
groups[22].advisers.append(czarches)
groups[35].observers.append(didabr)
groups[35].creators.append(didabr)
groups[37].reviewers.append(didgos)
groups[37].creators.append(didgos)
groups[14].creators.append(didgos)
groups[37].observers.append(didgos)
groups[14].observers.append(didgos)
groups[50].creators.append(dimpar)
groups[50].observers.append(dimpar)
groups[50].advisers.append(dimpar)
groups[41].creators.append(domlef)
groups[41].observers.append(domlef)
groups[33].creators.append(domlef)
groups[33].observers.append(domlef)
groups[17].observers.append(echevins)
groups[17].advisers.append(echevins)
groups[19].reviewers.append(eddhan)
groups[19].pvwriters.append(eddhan)
groups[19].advisers.append(eddhan)
groups[19].creators.append(eddhan)
groups[19].observers.append(eddhan)
groups[18].observers.append(eic)
groups[11].creators.append(elimal)
groups[36].creators.append(elimal)
groups[11].observers.append(elimal)
groups[17].advisers.append(elimal)
groups[11].reviewers.append(elimal)
groups[36].observers.append(elimal)
groups[16].observers.append(eridon)
groups[16].creators.append(eridon)
groups[45].creators.append(eriper)
groups[16].creators.append(eripir)
groups[16].reviewers.append(eripir)
groups[16].advisers.append(eripir)
groups[16].observers.append(eripir)
groups[40].creators.append(fabdel)
groups[40].observers.append(fabdel)
groups[42].observers.append(fabdel)
groups[42].creators.append(fabdel)
groups[39].observers.append(fabdel)
groups[41].creators.append(fabdel)
groups[41].observers.append(fabdel)
groups[39].advisers.append(fabdel)
groups[38].observers.append(fabmar)
groups[38].reviewers.append(fabmar)
groups[38].advisers.append(fabmar)
groups[42].creators.append(fabmar)
groups[38].creators.append(fabmar)
groups[48].creators.append(fabmau)
groups[48].observers.append(fabmau)
groups[38].observers.append(fabnoe)
groups[18].observers.append(fabnoe)
groups[18].creators.append(fabnoe)
groups[19].pvwriters.append(fabnoe)
groups[38].creators.append(fabnoe)
groups[18].advisers.append(fabnoe)
groups[19].creators.append(fabnoe)
groups[19].observers.append(fabnoe)
groups[37].advisers.append(fabsen)
groups[37].reviewers.append(fabsen)
groups[37].creators.append(fabsen)
groups[37].observers.append(fabsen)
groups[37].pvwriters.append(fabsen)
groups[26].observers.append(fannic)
groups[27].observers.append(fannic)
groups[32].reviewers.append(fannic)
groups[26].advisers.append(fannic)
groups[26].reviewers.append(fannic)
groups[27].reviewers.append(fannic)
groups[27].creators.append(fannic)
groups[14].creators.append(fannic)
groups[32].creators.append(fannic)
groups[32].advisers.append(fannic)
groups[26].creators.append(fannic)
groups[14].observers.append(fannic)
groups[47].observers.append(flolou)
groups[36].creators.append(flolou)
groups[47].creators.append(flolou)
groups[47].advisers.append(flolou)
groups[36].advisers.append(flolou)
groups[36].observers.append(flolou)
groups[16].observers.append(fraboc)
groups[16].creators.append(fraboc)
groups[17].advisers.append(fraleo)
groups[10].advisers.append(fraleo)
groups[10].reviewers.append(fraleo)
groups[10].observers.append(fraleo)
groups[10].creators.append(fraleo)
groups[44].advisers.append(framou)
groups[36].creators.append(framou)
groups[44].creators.append(framou)
groups[47].creators.append(framou)
groups[47].advisers.append(framou)
groups[17].advisers.append(framou)
groups[44].observers.append(framou)
groups[44].reviewers.append(framou)
groups[11].advisers.append(framou)
groups[47].observers.append(framou)
groups[36].advisers.append(framou)
groups[11].reviewers.append(framou)
groups[11].creators.append(framou)
groups[36].observers.append(framou)
groups[16].observers.append(frasma)
groups[16].creators.append(frasma)
groups[20].observers.append(fraver)
groups[20].reviewers.append(fraver)
groups[20].advisers.append(fraver)
groups[29].observers.append(frawil)
groups[7].reviewers.append(frawil)
groups[29].creators.append(frawil)
groups[17].advisers.append(frawil)
groups[35].creators.append(frawil)
groups[29].reviewers.append(frawil)
groups[35].observers.append(frawil)
groups[35].advisers.append(frawil)
groups[35].reviewers.append(frawil)
groups[7].observers.append(frawil)
groups[7].advisers.append(frawil)
groups[49].creators.append(frebel)
groups[49].observers.append(frebel)
groups[49].advisers.append(frebel)
groups[19].creators.append(frebou)
groups[19].observers.append(frebou)
groups[47].observers.append(gaecur)
groups[36].creators.append(gaecur)
groups[36].observers.append(gaecur)
groups[47].creators.append(gaecur)
groups[26].observers.append(genanc)
groups[26].creators.append(genanc)
groups[18].pvwriters.append(ginhen)
groups[18].observers.append(ginhen)
groups[18].creators.append(ginhen)
groups[18].reviewers.append(ginhen)
groups[18].advisers.append(ginhen)
groups[17].advisers.append(guyhav)
groups[16].advisers.append(guyhav)
groups[35].observers.append(guyhav)
groups[35].advisers.append(guyhav)
groups[16].observers.append(guyhav)
groups[32].creators.append(hasouc)
groups[32].observers.append(hasouc)
groups[47].observers.append(houmag)
groups[36].creators.append(houmag)
groups[47].creators.append(houmag)
groups[47].advisers.append(houmag)
groups[36].advisers.append(houmag)
groups[36].observers.append(houmag)
groups[29].observers.append(ingiur)
groups[16].observers.append(ingiur)
groups[16].reviewers.append(ingiur)
groups[16].creators.append(ingiur)
groups[7].reviewers.append(ingiur)
groups[29].creators.append(ingiur)
groups[35].creators.append(ingiur)
groups[17].advisers.append(ingiur)
groups[9].advisers.append(ingiur)
groups[29].reviewers.append(ingiur)
groups[35].observers.append(ingiur)
groups[9].reviewers.append(ingiur)
groups[35].advisers.append(ingiur)
groups[9].observers.append(ingiur)
groups[35].reviewers.append(ingiur)
groups[7].observers.append(ingiur)
groups[7].advisers.append(ingiur)
groups[17].advisers.append(isades)
groups[8].creators.append(isades)
groups[8].observers.append(isades)
groups[8].advisers.append(isades)
groups[37].creators.append(ismbou)
groups[37].observers.append(ismbou)
groups[37].advisers.append(ismbou)
groups[26].observers.append(jadbri)
groups[26].creators.append(jadbri)
groups[19].creators.append(jeadel)
groups[19].observers.append(jeadel)
groups[48].advisers.append(jeamaq)
groups[48].pvwriters.append(jeamaq)
groups[48].reviewers.append(jeamaq)
groups[48].creators.append(jeamaq)
groups[48].observers.append(jeamaq)
groups[43].observers.append(jeawar)
groups[41].creators.append(jeawar)
groups[41].observers.append(jeawar)
groups[16].observers.append(jerdup)
groups[16].creators.append(jerdup)
groups[27].observers.append(jerpir)
groups[14].creators.append(jerpir)
groups[27].reviewers.append(jerpir)
groups[27].creators.append(jerpir)
groups[42].creators.append(jerpir)
groups[14].reviewers.append(jerpir)
groups[14].observers.append(jerpir)
groups[25].advisers.append(julchi)
groups[25].creators.append(julchi)
groups[25].observers.append(julchi)
groups[27].observers.append(juldel)
groups[27].reviewers.append(juldel)
groups[27].creators.append(juldel)
groups[42].creators.append(juldel)
groups[14].creators.append(juldel)
groups[42].observers.append(juldel)
groups[14].observers.append(juldel)
groups[37].creators.append(juldre)
groups[37].observers.append(juldre)
groups[45].creators.append(kambel)
groups[47].observers.append(karnaj)
groups[36].creators.append(karnaj)
groups[47].creators.append(karnaj)
groups[47].advisers.append(karnaj)
groups[36].advisers.append(karnaj)
groups[36].observers.append(karnaj)
groups[33].advisers.append(laeste)
groups[33].creators.append(laeste)
groups[33].observers.append(laeste)
groups[16].observers.append(laudel)
groups[16].creators.append(laudel)
groups[32].creators.append(lauhan)
groups[32].observers.append(lauhan)
groups[1].creators.append(lauhoc)
groups[1].observers.append(lauhoc)
groups[1].pvwriters.append(lauhoc)
groups[1].advisers.append(lauhoc)
groups[1].reviewers.append(lauhoc)
groups[16].observers.append(logcas)
groups[16].creators.append(logcas)
groups[16].advisers.append(louanc)
groups[16].observers.append(louanc)
groups[16].reviewers.append(louanc)
groups[16].creators.append(louanc)
groups[16].observers.append(lusdon)
groups[16].creators.append(lusdon)
groups[37].creators.append(lydmot)
groups[37].observers.append(lydmot)
groups[4].creators.append(marant12)
groups[4].observers.append(marant12)
groups[32].creators.append(marauq)
groups[32].observers.append(marauq)
groups[37].creators.append(marbeg)
groups[37].observers.append(marbeg)
groups[1].reviewers.append(marbel)
groups[1].creators.append(marbel)
groups[1].observers.append(marbel)
groups[32].creators.append(marcar)
groups[32].observers.append(marcar)
groups[48].creators.append(marcla)
groups[48].observers.append(marcla)
groups[29].observers.append(mardeg)
groups[35].pvwriters.append(mardeg)
groups[29].creators.append(mardeg)
groups[35].creators.append(mardeg)
groups[29].reviewers.append(mardeg)
groups[35].observers.append(mardeg)
groups[35].advisers.append(mardeg)
groups[35].reviewers.append(mardeg)
groups[46].creators.append(marjam)
groups[46].observers.append(marjam)
groups[47].creators.append(marjam)
groups[47].advisers.append(marjam)
groups[36].creators.append(marjam)
groups[46].reviewers.append(marjam)
groups[36].pvwriters.append(marjam)
groups[47].pvwriters.append(marjam)
groups[46].pvwriters.append(marjam)
groups[47].observers.append(marjam)
groups[36].reviewers.append(marjam)
groups[36].advisers.append(marjam)
groups[36].observers.append(marjam)
groups[47].reviewers.append(marjam)
groups[46].advisers.append(marjam)
groups[46].creators.append(marmag)
groups[46].observers.append(marmag)
groups[46].reviewers.append(marmag)
groups[14].creators.append(marmat)
groups[14].observers.append(marmat)
groups[34].creators.append(marser)
groups[34].observers.append(marser)
groups[34].advisers.append(marser)
groups[47].observers.append(matdan)
groups[36].creators.append(matdan)
groups[47].creators.append(matdan)
groups[36].pvwriters.append(matdan)
groups[47].pvwriters.append(matdan)
groups[36].observers.append(matdan)
groups[42].observers.append(micdec)
groups[1].observers.append(micdec)
groups[17].advisers.append(micdec)
groups[28].observers.append(micdec)
groups[16].observers.append(micdec)
groups[35].observers.append(micdec)
groups[26].observers.append(micdec)
groups[7].creators.append(micdec)
groups[21].observers.append(micdec)
groups[24].observers.append(micdec)
groups[41].observers.append(micdec)
groups[6].observers.append(micdec)
groups[7].advisers.append(micdec)
groups[47].observers.append(micdec)
groups[32].observers.append(micdec)
groups[30].observers.append(micdec)
groups[7].reviewers.append(micdec)
groups[46].observers.append(micdec)
groups[31].observers.append(micdec)
groups[12].observers.append(micdec)
groups[33].observers.append(micdec)
groups[45].observers.append(micdec)
groups[50].observers.append(micdec)
groups[3].observers.append(micdec)
groups[10].observers.append(micdec)
groups[8].observers.append(micdec)
groups[34].observers.append(micdec)
groups[4].observers.append(micdec)
groups[29].observers.append(micdec)
groups[11].observers.append(micdec)
groups[7].observers.append(micdec)
groups[40].observers.append(micdec)
groups[49].observers.append(micdec)
groups[17].observers.append(micdec)
groups[15].observers.append(micdec)
groups[44].observers.append(micdec)
groups[37].observers.append(micdec)
groups[9].observers.append(micdec)
groups[20].observers.append(micdec)
groups[0].observers.append(micdec)
groups[27].observers.append(micdec)
groups[38].observers.append(micdec)
groups[18].observers.append(micdec)
groups[23].observers.append(micdec)
groups[5].observers.append(micdec)
groups[22].observers.append(micdec)
groups[43].observers.append(micdec)
groups[39].observers.append(micdec)
groups[48].observers.append(micdec)
groups[2].observers.append(micdec)
groups[36].observers.append(micdec)
groups[25].observers.append(micdec)
groups[19].observers.append(micdec)
groups[14].observers.append(micdec)
groups[45].creators.append(micwil)
groups[21].observers.append(muscer)
groups[40].creators.append(nandol)
groups[40].observers.append(nandol)
groups[42].observers.append(nandol)
groups[42].creators.append(nandol)
groups[39].observers.append(nandol)
groups[41].creators.append(nandol)
groups[41].observers.append(nandol)
groups[39].advisers.append(nandol)
groups[44].advisers.append(natfra)
groups[36].creators.append(natfra)
groups[44].creators.append(natfra)
groups[27].observers.append(natfra)
groups[47].creators.append(natfra)
groups[32].reviewers.append(natfra)
groups[17].advisers.append(natfra)
groups[44].observers.append(natfra)
groups[27].reviewers.append(natfra)
groups[44].reviewers.append(natfra)
groups[27].creators.append(natfra)
groups[32].creators.append(natfra)
groups[11].advisers.append(natfra)
groups[47].observers.append(natfra)
groups[36].advisers.append(natfra)
groups[11].reviewers.append(natfra)
groups[36].observers.append(natfra)
groups[32].observers.append(natfra)
groups[19].creators.append(natlef)
groups[19].observers.append(natlef)
groups[19].advisers.append(natlef)
groups[16].creators.append(natrut)
groups[16].reviewers.append(natrut)
groups[40].reviewers.append(natrut)
groups[16].pvwriters.append(natrut)
groups[16].advisers.append(natrut)
groups[16].observers.append(natrut)
groups[1].reviewers.append(nicpar)
groups[1].creators.append(nicpar)
groups[1].observers.append(nicpar)
groups[37].creators.append(noelej)
groups[37].observers.append(noelej)
groups[37].creators.append(oansto)
groups[37].observers.append(oansto)
groups[37].reviewers.append(oansto)
groups[41].pvwriters.append(olicam)
groups[40].creators.append(olicam)
groups[14].reviewers.append(olicam)
groups[40].reviewers.append(olicam)
groups[40].observers.append(olicam)
groups[41].reviewers.append(olicam)
groups[40].pvwriters.append(olicam)
groups[39].observers.append(olicam)
groups[14].creators.append(olicam)
groups[41].observers.append(olicam)
groups[39].advisers.append(olicam)
groups[14].observers.append(olicam)
groups[25].advisers.append(oxaale)
groups[25].creators.append(oxaale)
groups[25].observers.append(oxaale)
groups[26].observers.append(pashen)
groups[26].creators.append(pashen)
groups[45].advisers.append(pasmon)
groups[45].reviewers.append(pasmon)
groups[45].creators.append(pasmon)
groups[45].pvwriters.append(pasmon)
groups[45].observers.append(pasmon)
groups[41].pvwriters.append(paster)
groups[41].reviewers.append(paster)
groups[41].creators.append(paster)
groups[39].observers.append(paster)
groups[41].observers.append(paster)
groups[39].advisers.append(paster)
groups[16].advisers.append(patarn)
groups[16].observers.append(patarn)
groups[16].reviewers.append(patarn)
groups[16].creators.append(patarn)
groups[32].creators.append(pattho)
groups[32].observers.append(pattho)
groups[4].creators.append(pauvan)
groups[4].observers.append(pauvan)
groups[48].advisers.append(pavcor)
groups[48].reviewers.append(pavcor)
groups[48].creators.append(pavcor)
groups[48].observers.append(pavcor)
groups[26].observers.append(phipir)
groups[26].advisers.append(phipir)
groups[26].creators.append(phipir)
groups[32].creators.append(piefon)
groups[32].observers.append(piefon)
groups[50].creators.append(piemin)
groups[50].observers.append(piemin)
groups[50].reviewers.append(piemin)
groups[50].advisers.append(piemin)
groups[26].observers.append(pievan)
groups[26].creators.append(pievan)
groups[23].creators.append(promandenne)
groups[23].observers.append(promandenne)
groups[23].advisers.append(promandenne)
groups[23].pvwriters.append(promandenne)
groups[30].creators.append(robgob)
groups[30].observers.append(robgob)
groups[30].reviewers.append(robgob)
groups[30].advisers.append(robgob)
groups[22].advisers.append(roldan)
groups[22].creators.append(roldan)
groups[22].observers.append(roldan)
groups[33].advisers.append(roldes)
groups[33].creators.append(roldes)
groups[33].observers.append(roldes)
groups[15].creators.append(rongos)
groups[14].creators.append(rongos)
groups[4].reviewers.append(rongos)
groups[32].reviewers.append(rongos)
groups[27].creators.append(rongos)
groups[4].creators.append(rongos)
groups[24].observers.append(rongos)
groups[6].observers.append(rongos)
groups[32].observers.append(rongos)
groups[38].creators.append(rongos)
groups[6].reviewers.append(rongos)
groups[15].advisers.append(rongos)
groups[34].reviewers.append(rongos)
groups[38].reviewers.append(rongos)
groups[26].reviewers.append(rongos)
groups[15].reviewers.append(rongos)
groups[15].observers.append(rongos)
groups[24].reviewers.append(rongos)
groups[6].creators.append(rongos)
groups[15].pvwriters.append(rongos)
groups[27].reviewers.append(rongos)
groups[14].reviewers.append(rongos)
groups[24].creators.append(rongos)
groups[32].creators.append(rongos)
groups[26].creators.append(rongos)
groups[27].advisers.append(rongos)
groups[14].observers.append(rongos)
groups[32].observers.append(rudnsi)
groups[6].creators.append(sancru)
groups[6].advisers.append(sancru)
groups[17].advisers.append(sancru)
groups[6].reviewers.append(sancru)
groups[6].observers.append(sancru)
groups[37].creators.append(sanpar)
groups[37].observers.append(sanpar)
groups[37].advisers.append(sanpar)
groups[32].creators.append(sanric)
groups[32].observers.append(sanric)
groups[38].observers.append(sebron)
groups[38].reviewers.append(sebron)
groups[38].advisers.append(sebron)
groups[42].creators.append(sebron)
groups[38].creators.append(sebron)
groups[16].observers.append(simgre)
groups[16].creators.append(simgre)
groups[16].observers.append(simler)
groups[16].creators.append(simler)
groups[25].advisers.append(sophan)
groups[25].creators.append(sophan)
groups[25].observers.append(sophan)
groups[37].creators.append(stafin)
groups[37].observers.append(stafin)
groups[37].advisers.append(stafin)
groups[40].creators.append(stajur)
groups[39].creators.append(stajur)
groups[40].observers.append(stajur)
groups[42].observers.append(stajur)
groups[42].creators.append(stajur)
groups[39].observers.append(stajur)
groups[41].creators.append(stajur)
groups[41].observers.append(stajur)
groups[27].observers.append(stasec)
groups[27].creators.append(stasec)
groups[48].creators.append(stebad)
groups[48].observers.append(stebad)
groups[37].creators.append(stechi)
groups[37].observers.append(stechi)
groups[37].advisers.append(stechi)
groups[37].reviewers.append(stechi)
groups[24].pvwriters.append(syldom)
groups[14].creators.append(syldom)
groups[4].pvwriters.append(syldom)
groups[42].pvwriters.append(syldom)
groups[47].pvwriters.append(syldom)
groups[33].advisers.append(syldom)
groups[32].pvwriters.append(syldom)
groups[33].reviewers.append(syldom)
groups[43].pvwriters.append(syldom)
groups[26].pvwriters.append(syldom)
groups[7].pvwriters.append(syldom)
groups[37].pvwriters.append(syldom)
groups[8].pvwriters.append(syldom)
groups[12].pvwriters.append(syldom)
groups[49].pvwriters.append(syldom)
groups[29].pvwriters.append(syldom)
groups[49].reviewers.append(syldom)
groups[0].pvwriters.append(syldom)
groups[16].pvwriters.append(syldom)
groups[36].pvwriters.append(syldom)
groups[33].observers.append(syldom)
groups[20].pvwriters.append(syldom)
groups[19].pvwriters.append(syldom)
groups[40].pvwriters.append(syldom)
groups[3].pvwriters.append(syldom)
groups[22].pvwriters.append(syldom)
groups[50].pvwriters.append(syldom)
groups[33].pvwriters.append(syldom)
groups[33].creators.append(syldom)
groups[38].pvwriters.append(syldom)
groups[39].pvwriters.append(syldom)
groups[2].pvwriters.append(syldom)
groups[49].observers.append(syldom)
groups[11].pvwriters.append(syldom)
groups[48].pvwriters.append(syldom)
groups[6].pvwriters.append(syldom)
groups[1].pvwriters.append(syldom)
groups[27].pvwriters.append(syldom)
groups[30].pvwriters.append(syldom)
groups[44].pvwriters.append(syldom)
groups[41].pvwriters.append(syldom)
groups[34].pvwriters.append(syldom)
groups[25].pvwriters.append(syldom)
groups[46].pvwriters.append(syldom)
groups[18].pvwriters.append(syldom)
groups[31].pvwriters.append(syldom)
groups[35].pvwriters.append(syldom)
groups[21].pvwriters.append(syldom)
groups[17].pvwriters.append(syldom)
groups[9].pvwriters.append(syldom)
groups[14].reviewers.append(syldom)
groups[23].pvwriters.append(syldom)
groups[45].pvwriters.append(syldom)
groups[14].observers.append(syldom)
groups[4].advisers.append(tatcha)
groups[4].reviewers.append(tatcha)
groups[4].pvwriters.append(tatcha)
groups[4].creators.append(tatcha)
groups[4].observers.append(tatcha)
groups[16].advisers.append(tinmal)
groups[16].observers.append(tinmal)
groups[16].creators.append(tinmal)
groups[16].reviewers.append(tinmal)
groups[35].observers.append(userC1)
groups[35].advisers.append(userC1)
groups[35].creators.append(userC1)
groups[35].reviewers.append(userC1)
groups[33].observers.append(userP1)
groups[33].advisers.append(userP1)
groups[33].reviewers.append(userP1)
groups[33].pvwriters.append(userP1)
groups[33].creators.append(userP1)
groups[32].creators.append(usertest)
groups[32].observers.append(usertest)
groups[32].pvwriters.append(usertest)
groups[32].reviewers.append(usertest)
groups[38].observers.append(usertest2)
groups[38].reviewers.append(usertest2)
groups[38].advisers.append(usertest2)
groups[38].creators.append(usertest2)
groups[38].pvwriters.append(usertest2)
groups[47].observers.append(valdeg)
groups[36].creators.append(valdeg)
groups[47].creators.append(valdeg)
groups[47].advisers.append(valdeg)
groups[36].advisers.append(valdeg)
groups[36].observers.append(valdeg)
groups[37].advisers.append(valduc)
groups[37].reviewers.append(valduc)
groups[37].creators.append(valduc)
groups[37].observers.append(valduc)
groups[37].pvwriters.append(valduc)
groups[47].observers.append(valevr)
groups[36].creators.append(valevr)
groups[36].reviewers.append(valevr)
groups[47].advisers.append(valevr)
groups[47].creators.append(valevr)
groups[36].pvwriters.append(valevr)
groups[47].pvwriters.append(valevr)
groups[36].advisers.append(valevr)
groups[36].observers.append(valevr)
groups[47].reviewers.append(valevr)
groups[34].creators.append(verper)
groups[34].observers.append(verper)
groups[34].advisers.append(verper)
groups[34].pvwriters.append(verper)
groups[38].observers.append(vinbou)
groups[42].reviewers.append(vinbou)
groups[42].creators.append(vinbou)
groups[39].observers.append(vinbou)
groups[14].creators.append(vinbou)
groups[42].observers.append(vinbou)
groups[39].advisers.append(vinbou)
groups[14].observers.append(vinbou)
groups[17].advisers.append(vinsam)
groups[12].reviewers.append(vinsam)
groups[12].observers.append(vinsam)
groups[12].advisers.append(vinsam)
groups[27].observers.append(virdem)
groups[16].creators.append(virdem)
groups[16].reviewers.append(virdem)
groups[16].pvwriters.append(virdem)
groups[27].reviewers.append(virdem)
groups[27].creators.append(virdem)
groups[16].advisers.append(virdem)
groups[14].creators.append(virdem)
groups[14].reviewers.append(virdem)
groups[16].observers.append(virdem)
groups[27].advisers.append(virdem)
groups[14].observers.append(virdem)
groups[37].creators.append(virhen)
groups[37].observers.append(virhen)
groups[37].advisers.append(virhen)
groups[45].creators.append(vivmat)
groups[25].advisers.append(xaveer)
groups[25].reviewers.append(xaveer)
groups[25].creators.append(xaveer)
groups[25].observers.append(xaveer)
groups[38].advisers.append(xavwil)
groups[38].creators.append(xavwil)
groups[38].observers.append(xavwil)
groups[32].creators.append(yahben)
groups[32].observers.append(yahben)
groups[19].creators.append(yandeg)
groups[19].observers.append(yandeg)
groups[46].creators.append(yassca)
groups[46].observers.append(yassca)
groups[8].reviewers.append(yastuz)
groups[8].observers.append(yastuz)
groups[27].observers.append(yvagem)
groups[14].reviewers.append(yvagem)
groups[27].reviewers.append(yvagem)
groups[27].creators.append(yvagem)
groups[14].creators.append(yvagem)
groups[27].advisers.append(yvagem)
groups[14].observers.append(yvagem)
groups[3].creators.append(yvesor)
groups[3].observers.append(yvesor)
groups[3].advisers.append(yvesor)
groups[3].pvwriters.append(yvesor)
groups[26].observers.append(zonet)
groups[26].advisers.append(zonet)
groups[26].creators.append(zonet)




# Meeting configurations -------------------------------------------------------
# college
collegeMeeting = MeetingConfigDescriptor(
    'meeting-config-college', 'College Communal',
    'College communal', isDefault=True)
collegeMeeting.meetingManagers = ['rongos','yvagem','fabmar','juldel','annlem','virdem' ]
#collegeMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
#                          'Charles Exemple - 1er Echevin,\n' \
#                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
#                          'Jacqueline Exemple, Responsable du CPAS'
#collegeMeeting.signatures = 'Le Secrétaire communal\nPierre Dupont\nLe Bourgmestre\nCharles Exemple'
#collegeMeeting.certifiedSignatures = [
#    {'signatureNumber': '1',
#     'name': u'Mr Vraiment Présent',
#     'function': u'Le Secrétaire communal',
#     'date_from': '',
#     'date_to': '',
#     },
#    {'signatureNumber': '2',
#     'name': u'Mr Charles Exemple',
#     'function': u'Le Bourgmestre',
#     'date_from': '',
#     'date_to': '',
#"     },
#]
collegeMeeting.places = """Hotel de Ville\r
Centre administratif\r"""
collegeMeeting.budgetDefault='<p>1) Montant de la dépense : <b> XXX  EUR TVAC</b> <br />2) Article Budgétaire  : <b>XXXX/XXX-XX </b><br />3) Libellé de cet article :<b> XXX</b><br />4) Crédit initial :<b> XXX EUR</b><br />5) Crédit disponible :<b> XXX EUR</b><br />6) Infos prises le<b> XXX</b> auprès de<b> XXX </b><br />7) Observations : <b>NEANT </b> <br /><br /><font color="red">&laquo; ATTENTION : depuis le 1er septembre 2013, tout projet de décision ayant une incidence financière ou budgétaire supérieure à <b>22.000,00 euros</b> doit obligatoirement être accompagné d&rsquo;un avis de légalité écrit, préalable et motivé du Directeur financier.  L&rsquo;avis fait partie intégrante de la décision; il doit en être fait état dans la présentation du point (proposition de décision), ainsi que dans la délibération (reproduction in extenso) lorsqu&rsquo;une délibération est établie. (Article L 1124-40 &sect; 1er-3&deg; CDLD). &raquo;</font></p>'
collegeMeeting.categories = categories
collegeMeeting.enableAnnexToPrint=True
collegeMeeting.annexToPrintDefault=True
collegeMeeting.annexDecisionToPrintDefault=True
collegeMeeting.annexAdviceToPrintDefault=False
collegeMeeting.initItemDecisionIfEmptyOnDecide=False
collegeMeeting.shortName = 'College'
collegeMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier,
                                   annexeDecision, annexeAvis, annexeAvisLegal]
collegeMeeting.usedItemAttributes = ['budgetInfos',
 				     'associatedGroups',
                                     'observations',
                                     'itemsSignatories',
                                     'sendToAuthority',
                                      ]
collegeMeeting.usedMeetingAttributes = ['startDate', 'endDate', 'signatories', 'attendees','excused','absents','place', 'observations','postobservations', ]
collegeMeeting.recordMeetingHistoryStates = []
collegeMeeting.itemsListVisibleColumns = ['proposingGroupAcronym',
                                          'state',
                                          'proposingGroup',
                                          'annexes',
					  'creator',
                                          'category'
                                          'advices',
                                          'actions', ]
collegeMeeting.itemColumns = ['creator',
			      'creationDate',
                              'state',
                              'proposingGroup',
                              'annexes',
                              'annexesDecision',
                              'advices',
                              'actions',
                              'meeting', ]
collegeMeeting.meetingColumns=['creator',
			      'creationDate',
                              'state',
                              'actions',]

collegeMeeting.xhtmlTransformFields = ('MeetingItem.description',
                                       'MeetingItem.pv',
					'MeetingItem.textpv',
					'MeetingItem.projetpv',
                                       'MeetingItem.decision',
                                       'MeetingItem.observations',
                                       'Meeting.observations',
                                       'Meeting.postobservations', )
collegeMeeting.maxShownAvailableItems=300
collegeMeeting.maxShownMeetingItems=300
collegeMeeting.maxShownLateItems=300
collegeMeeting.enableGotoPage=False
collegeMeeting.enableGotoItem=True
collegeMeeting.openAnnexesInSeparateWindows=False
collegeMeeting.mailItemEvents=['itemDelayed','adviceToGive','annexAdded',]
collegeMeeting.xhtmlTransformTypes = ('removeBlanks',)
collegeMeeting.useGroupsAsCategories=False
collegeMeeting.toDiscussSetOnItemInsert=True
collegeMeeting.toDiscussDefault=True
collegeMeeting.toDiscussLateDefault=True
collegeMeeting.toDiscussShownForLateItems=True
collegeMeeting.itemReferenceFormat=''
collegeMeeting.itemWorkflow = 'meetingitemcollegeandenne_workflow'
collegeMeeting.meetingWorkflow = 'meetingcollege_workflow' 
collegeMeeting.itemConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowConditions'
collegeMeeting.itemActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCollegeAndenneWorkflowActions'
collegeMeeting.meetingConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowConditions'
collegeMeeting.meetingActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCollegeAndenneWorkflowActions'
collegeMeeting.transitionsToConfirm = ['MeetingItem.delay','MeetingItem.backToPtoposed','MeetingItem.backToItemCreated' ]
collegeMeeting.meetingPresentItemWhenNoCurrentMeetingStates='created'
collegeMeeting.meetingTopicStates = ('created', 'frozen')
collegeMeeting.decisionTopicStates = ('decided', 'closed','archived')
collegeMeeting.enforceAdviceMandatoriness = False
collegeMeeting.insertingMethodsOnAddItem = ({'insertingMethod': 'on_categories',
                                             'reverse': '0'}, )
collegeMeeting.recordItemHistoryStates = []
collegeMeeting.maxShownMeetings = 5
collegeMeeting.maxDaysDecisions = 60
collegeMeeting.meetingAppDefaultView = 'topic_searchmyitems'
collegeMeeting.useAdvices = True
collegeMeeting.itemAdviceStates = ('itemcreated','proposed','validated','prevalidated','presented','itemfrozen',)
collegeMeeting.itemAdviceEditStates = ('itemcreated','proposed','validated','prevalidated','presented','itemfrozen',)
collegeMeeting.itemAdviceViewStates = ('itemcreated',
                                       'proposed'
                                       'prevalidated'
                                       'validated',
                                       'presented',
                                       'itemfrozen',
                                       'accepted',
                                       'refused',
				       'accepted_and_closed',
				       'refused_and_closed',
				       'delayed_and_closed',
				       'accepted_but_modified_and_closed',
                                       'accepted_but_modified',
                                       'delayed',
                                       'pre_accepted',)
collegeMeeting.usedAdviceTypes = ['positive', 'positive_with_remarks', 'negative', 'nil', ]
collegeMeeting.enableAdviceInvalidation = False
collegeMeeting.enforceAdviceMandatoriness=False
collegeMeeting.defaultAdviceType="positive"
collegeMeeting.itemAdviceInvalidateStates = []
collegeMeeting.customAdvisers = [
    {'row_id': 'unique_id_002',
     'group': 'service-finances',
     'for_item_created_from': today,
     'delay': '5',
     'delay_left_alert': '2',
     'delay_label': 'Incidence financière >= 22.000€', },
    {'row_id': 'unique_id_003',
     'group': 'service-finances',
     'for_item_created_from': today,
     'delay': '10',
     'delay_left_alert': '4',
     'delay_label': 'Incidence financière >= 22.000€', },
    {'row_id': 'unique_id_004',
     'group': 'service-finances',
     'for_item_created_from': today,
     'delay': '20',
     'delay_left_alert': '4',
     'delay_label': 'Incidence financière >= 22.000€', }, ]
collegeMeeting.itemPowerObserversStates = ('itemfrozen',
                                           'accepted',
					   'validated'
                                           'prevalidated',
                                           'delayed',
                                           'refused',
                                           'accepted_but_modified',
                                           'pre_accepted'
                                           'accepted_and_closed',
					   'refused_and_closed',
					   'delayed_and_closed',
					   'accepted_but_modified_and_closed',
)
collegeMeeting.meetingPowerObserversStates = ('created','frozen', 'decided', 'closed','archived')
collegeMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed', 'accepted_but_modified', 'pre_accepted','accepted_and_closed','refused_and_closed','delayed_and_closed','accepted_but_modified_and_closed',]
collegeMeeting.transitionsForPresentingAnItem = ('propose', 'validate', 'present', )
#collegeMeeting.onTransitionFieldTransforms = (
#    ({'transition': 'delay',
#      'field_name': 'MeetingItem.decision',
#      'tal_expression': "string:<p>Le Collège décide de reporter le point.</p>${here/getDecision}"},))
collegeMeeting.onMeetingTransitionItemTransitionToTrigger = ({'meeting_transition': 'freeze',
                                                              'item_transition': 'itemfreeze'},)
collegeMeeting.powerAdvisersGroups = ('service-finances', 'secretariat','service-juridique-vb' )
collegeMeeting.itemBudgetInfosStates = ('proposed', 'validated', 'presented','prevalidated','itemfrozen')
collegeMeeting.itemCopyGroupsStates =     ('itemfrozen',
                                           'accepted',
					   'validated'
                                           'prevalidated',
                                           'delayed',
                                           'refused',
                                           'accepted_but_modified',
                                           'pre_accepted'
                                           'accepted_and_closed',
					   'refused_and_closed',
					   'delayed_and_closed',
					   'accepted_but_modified_and_closed',
)

collegeMeeting.useCopies = True
collegeMeeting.enableAnnexConfidentiality=True
collegeMeeting.enableAdviceConfidentiality=True
collegeMeeting.adviceConfidentialityDefault=False
collegeMeeting.selectableCopyGroups = [
groups[1].getIdSuffixed('reviewers'),
groups[2].getIdSuffixed('reviewers'),
groups[3].getIdSuffixed('reviewers'),
groups[4].getIdSuffixed('reviewers'),
groups[5].getIdSuffixed('reviewers'),
groups[6].getIdSuffixed('reviewers'),
groups[7].getIdSuffixed('reviewers'),
groups[8].getIdSuffixed('reviewers'),
groups[9].getIdSuffixed('reviewers'),
groups[10].getIdSuffixed('reviewers'),
groups[11].getIdSuffixed('reviewers'),
groups[12].getIdSuffixed('reviewers'),
groups[14].getIdSuffixed('creators'),
groups[15].getIdSuffixed('reviewers'),
groups[16].getIdSuffixed('reviewers'),
groups[17].getIdSuffixed('reviewers'),
groups[19].getIdSuffixed('reviewers'),
groups[21].getIdSuffixed('reviewers'),
groups[22].getIdSuffixed('reviewers'),
groups[23].getIdSuffixed('reviewers'),
groups[24].getIdSuffixed('observers'),
groups[25].getIdSuffixed('reviewers'),
groups[26].getIdSuffixed('creators'),
groups[27].getIdSuffixed('reviewers'),
groups[30].getIdSuffixed('reviewers'),
groups[32].getIdSuffixed('reviewers'),
groups[33].getIdSuffixed('reviewers'),
groups[34].getIdSuffixed('reviewers'),
groups[35].getIdSuffixed('reviewers'),
groups[36].getIdSuffixed('reviewers'),
groups[37].getIdSuffixed('reviewers'),
groups[38].getIdSuffixed('reviewers'),
groups[39].getIdSuffixed('observers'),
groups[40].getIdSuffixed('reviewers'),
groups[41].getIdSuffixed('reviewers'),
groups[42].getIdSuffixed('reviewers'),
groups[43].getIdSuffixed('observers'),
groups[44].getIdSuffixed('reviewers'),
groups[45].getIdSuffixed('reviewers'),
groups[46].getIdSuffixed('reviewers'),
groups[47].getIdSuffixed('reviewers'),
groups[48].getIdSuffixed('reviewers'),
groups[49].getIdSuffixed('observers'),
groups[50].getIdSuffixed('reviewers'),
groups[51].getIdSuffixed('reviewers'),
groups[24].getIdSuffixed('reviewers')
]

collegeMeeting.podTemplates = collegeTemplates

bourgmestre_mu = MeetingUserDescriptor('claeer',
                                       duty='Bourgmestre',
				       replacementDuty="Bourgmestre f.f.",
                                       usages=['assemblyMember', 'signer', ],
                                       signatureIsDefault=True)
Echevin1 = MeetingUserDescriptor('elimal',
                                duty='Echevin',
			        replacementDuty="Bourgmestre f.f.",
                                usages=['assemblyMember','signer', ])
Echevin2 = MeetingUserDescriptor('guyhav',
                                duty='Echevin',
			        replacementDuty="Bourgmestre f.f.",
                                usages=['assemblyMember','signer', ])
Echevin3 = MeetingUserDescriptor('fraleo',
                                duty='Echevin',
			        replacementDuty="Bourgmestre f.f.",
                                usages=['assemblyMember','signer', ])
Echevin4 = MeetingUserDescriptor('bencos',
                                duty='Echevin',
			        replacementDuty="Bourgmestre f.f.",
                                usages=['assemblyMember','signer', ])
Echevin5 = MeetingUserDescriptor('micdec',
                                duty='Echevin',
			        replacementDuty="Bourgmestre f.f.",
                                usages=['assemblyMember','signer', ])
Echevin6 = MeetingUserDescriptor('sancru',
                                duty="Présidente du Conseil de l'action sociale",
			        replacementDuty="Bourgmestre f.f.",
                                usages=['assemblyMember','signer', ])
dgen_mu = MeetingUserDescriptor('yvagem',
                                duty='Directeur Général',
			        replacementDuty="Directeur Général f.f.",
                                usages=['assemblyMember', 'signer', ],
                                signatureIsDefault=True)
dgen_mu2 = MeetingUserDescriptor('rongos',
                                duty='Directeur Général f.f.',
			        replacementDuty="Directeur Général f.f.",
                                usages=['signer', ])

collegeMeeting.meetingUsers = [bourgmestre_mu, Echevin1,Echevin2,Echevin3,Echevin4,Echevin5,Echevin6,dgen_mu,dgen_mu2]

collegeMeeting.itemFormationTemplates = [
    ItemTemplateDescriptor(
        id='demande-de-formation',
        title='Demande de formation',
        proposingGroup='secretariat',
        description='',
        category='45-personnel'),
]

#collegeMeeting.meetingConfigsToCloneTo = [{'meeting_config': 'meeting-config-council',
#                                           'trigger_workflow_transitions_until': '__nothing__'}, ]
# Conseil communal
councilMeeting = MeetingConfigDescriptor(
    'meeting-config-council', 'Conseil Communal',
    'Conseil Communal')
councilMeeting.meetingManagers = ['dgen', ]
councilMeeting.assembly = 'Pierre Dupont - Bourgmestre,\n' \
                          'Charles Exemple - 1er Echevin,\n' \
                          'Echevin Un, Echevin Deux, Echevin Trois - Echevins,\n' \
                          'Jacqueline Exemple, Responsable du CPAS'
councilMeeting.signatures = 'Le Secrétaire communal\nPierre Dupont\nLe Bourgmestre\nCharles Exemple'
councilMeeting.certifiedSignatures = [
    {'signatureNumber': '1',
     'name': u'Mr Vraiment Présent',
     'function': u'Le Secrétaire communal',
     'date_from': '',
     'date_to': '',
     },
    {'signatureNumber': '2',
     'name': u'Mr Charles Exemple',
     'function': u'Le Bourgmestre',
     'date_from': '',
     'date_to': '',
     },
]
councilMeeting.places = """Place1\n\r
Place2\n\r
Place3\n\r"""
councilMeeting.categories = categories
councilMeeting.shortName = 'Council'
councilMeeting.meetingFileTypes = [annexe, annexeBudget, annexeCahier,
                                   annexeDecision, annexeAvis, annexeAvisLegal]
councilMeeting.usedItemAttributes = ['detailedDescription',
                                     'oralQuestion',
                                     'itemInitiator',
                                     'observations',
                                     'privacy',
                                     'itemAssembly', ]
councilMeeting.usedMeetingAttributes = ['startDate',
                                        'midDate',
                                        'endDate',
                                        'signatures',
                                        'assembly',
                                        'place',
                                        'observations', ]
councilMeeting.recordMeetingHistoryStates = []
councilMeeting.itemsListVisibleColumns = ['state', 'proposingGroup', 'annexes', 'annexesDecision', 'actions', ]
councilMeeting.itemColumns = ['creator',
                              'state',
                              'proposingGroup',
                              'annexes',
                              'annexesDecision',
                              'advices',
                              'actions',
                              'meeting', ]
councilMeeting.xhtmlTransformFields = ('MeetingItem.description',
                                       'MeetingItem.detailedDescription',
                                       'MeetingItem.decision',
                                       'MeetingItem.observations',
                                       'Meeting.observations', )
councilMeeting.xhtmlTransformTypes = ('removeBlanks',)
councilMeeting.itemWorkflow = 'meetingitemcollegeandenne_workflow'
councilMeeting.meetingWorkflow = 'meetingcollege_workflow'
councilMeeting.itemConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCouncilWorkflowConditions'
councilMeeting.itemActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingItemCouncilWorkflowActions'
councilMeeting.meetingConditionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCouncilWorkflowConditions'
councilMeeting.meetingActionsInterface = 'Products.MeetingAndenne.interfaces.IMeetingCouncilWorkflowActions'
councilMeeting.transitionsToConfirm = []
councilMeeting.meetingTopicStates = ('created', 'frozen')
councilMeeting.decisionTopicStates = ('decided', 'closed','archived')
councilMeeting.itemAdviceStates = ('validated',)
councilMeeting.enforceAdviceMandatoriness = False
councilMeeting.insertingMethodsOnAddItem = ({'insertingMethod': 'on_proposing_groups',
                                             'reverse': '0'}, )
councilMeeting.recordItemHistoryStates = []
councilMeeting.maxShownMeetings = 5
councilMeeting.maxDaysDecisions = 60
councilMeeting.meetingAppDefaultView = 'topic_searchmyitems'
councilMeeting.itemDocFormats = ('odt', 'pdf')
councilMeeting.meetingDocFormats = ('odt', 'pdf')
councilMeeting.useAdvices = False
councilMeeting.itemAdviceStates = ()
councilMeeting.itemAdviceEditStates = ()
councilMeeting.itemAdviceViewStates = ()
councilMeeting.itemDecidedStates = ['accepted', 'refused', 'delayed', 'accepted_but_modified', 'pre_accepted']
councilMeeting.transitionsForPresentingAnItem = ('propose', 'validate', 'present', )
councilMeeting.onMeetingTransitionItemTransitionToTrigger = ({'meeting_transition': 'freeze',
                                                              'item_transition': 'itemfreeze'},

                                                             {'meeting_transition': 'publish',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'publish',
                                                              'item_transition': 'itempublish'},

                                                             {'meeting_transition': 'decide',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'decide',
                                                              'item_transition': 'itempublish'},

                                                             {'meeting_transition': 'publish_decisions',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'publish_decisions',
                                                              'item_transition': 'itempublish'},
                                                             {'meeting_transition': 'publish_decisions',
                                                              'item_transition': 'accept'},

                                                             {'meeting_transition': 'close',
                                                              'item_transition': 'itemfreeze'},
                                                             {'meeting_transition': 'close',
                                                              'item_transition': 'itempublish'},
                                                             {'meeting_transition': 'close',
                                                              'item_transition': 'accept'},)
councilMeeting.itemPowerObserversStates = ('itemfrozen',
                                           'itempublished',
                                           'accepted', 'delayed',
                                           'refused',
                                           'accepted_but_modified', 'pre_accepted')
councilMeeting.meetingPowerObserversStates = ('frozen','created', 'decided', 'closed','archived')
councilMeeting.powerAdvisersGroups = ()
councilMeeting.itemBudgetInfosStates = ('proposed', 'validated', 'presented')
councilMeeting.useCopies = True
councilMeeting.selectableCopyGroups = [groups[0].getIdSuffixed('reviewers'),
                                       groups[1].getIdSuffixed('reviewers'),
                                       groups[2].getIdSuffixed('reviewers'),
                                       groups[4].getIdSuffixed('reviewers')]
#councilMeeting.podTemplates = councilTemplates

receveur_mu = MeetingUserDescriptor('receveur',
                                    duty='Receveur communal',
                                    usages=['assemblyMember', 'signer', 'asker', ])

councilMeeting.meetingUsers = [receveur_mu]

councilMeeting.recurringItems = [
    RecurringItemDescriptor(
        id='recurringagenda1',
        title='Approuve le procès-verbal de la séance antérieure',
        description='Approuve le procès-verbal de la séance antérieure',
        category='recurrents',
        proposingGroup='secretariat',
        decision='Procès-verbal approuvé'), ]
councilMeeting.itemFormationTemplates = []

data = PloneMeetingConfiguration(meetingFolderTitle='Mes séances',
                                 meetingConfigs=(collegeMeeting, councilMeeting),
                                 groups=groups)
data.unoEnabledPython = '/usr/bin/python'
data.usedColorSystem = 'state_color'
data.enableUserPreferences = False
# ------------------------------------------------------------------------------
