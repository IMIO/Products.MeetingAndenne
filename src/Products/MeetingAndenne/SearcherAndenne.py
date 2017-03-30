# -*- coding: utf-8 -*-
#
# File: SearcherAndenne.py
#
# Copyright (c) 2017 by Service Informatique Ville d'Andenne
#
# GNU General Public License (GPL)
#

__author__ = """Sébastien RONVEAUX <sebastien.ronveaux@ac.andenne.be>, Fabio MARCUZZI
<fabio.marcuzzi@ac.andenne.be"""
__docformat__ = 'plaintext'


from Products.CMFPlone.PloneBatch import Batch
from Products.PloneMeeting.utils import getDateFromRequest, prepareSearchValue
from Products.PloneMeeting.Searcher import Searcher

# ------------------------------------------------------------------------------
class SearcherAndenne(Searcher):
    '''The searcher creates and executes queries in the portal_catalog
       which are triggered by the user from the "advanced search" screen in
       PloneMeeting.'''

    def getMailSearchParams(self, mainParams, dateInterval):
        '''Adds to dict p_mainParams the parameters which are needed for
           performing (a) mail-specific query(ies) in the portal_catalog.'''
        res = mainParams.copy()
        res['portal_type'] = 'CourrierFile'
        res['created'] = {'query': dateInterval, 'range': 'minmax'}
        res['sort_on'] = self.sortKey or 'created'
        res['isDefinedInTool'] = False

        if self.keywords:
            # What fields need to be queried?
            kTargets = self.getMultiValue('mail_keywords_target')
            if 'search_mail_contents' in kTargets:
                # Search among mails titles and contents
                self.addKeywords(res, 'Title')
                self.addKeywords(res, 'indexExtractedText')
            if 'search_mail_references' in kTargets:
                self.addKeywords(res, 'getRefcourrier')
            if 'search_mail_senders' in kTargets:
                self.addKeywords(res, 'getDestOrigin')
        destUsers = self.getMultiValue('destUsers')
        if destUsers:
            res['getDestUsers'] = destUsers
        mailTypes = self.getMultiValue('mailTypes')
        if mailTypes:
            res['getTypecourrier'] = mailTypes
        return res

    def mergeResults(self, results, sortKey):
        '''p_results contains several lists of brains that we need to merge.
           We need to take the p_sortKey into account.'''
        res = []
        moreBrains = True
        nextIndexes = [0] * len(results)
        nextCandidates = {}  # ~{i_listNumber: brain}~
        while moreBrains:
            # Compute next candidates
            nextCandidates.clear()
            i = -1
            for nextIndex in nextIndexes:
                i += 1
                brainsList = results[i]
                if nextIndex < len(brainsList):
                    # There is at least one more candidate in this list
                    nextCandidates[i] = brainsList[nextIndex]
            if not nextCandidates:
                moreBrains = False
            else:
                # Compute the winner among all candidates
                winner = None
                winnerListNumber = None
                for listNumber, candidate in nextCandidates.iteritems():
                    if not winner:
                        winner = candidate
                        winnerListNumber = listNumber
                    else:
                        # Compare the current winner to this candidate
                        winnerKey = self.getValueFromIndex(winner, sortKey)
                        candidateKey = self.getValueFromIndex(candidate, sortKey)
                        # The comparison condition follows sort order
                        if self.sortOrder == 'reverse':
                            condition = winnerKey < candidateKey
                        else:
                            condition = winnerKey > candidateKey
                        if condition:
                            winner = candidate
                            winnerListNumber = listNumber
                        else:
                            if winner.getRID() == candidate.getRID():
                                nextIndexes[listNumber] += 1
                # Add the winner to the result and prepare next iteration
                res.append(winner)
                nextIndexes[winnerListNumber] += 1
        return res

    def searchAnnexes(self, params):
        '''Executes the portal_catalog search(es) for querying mails, and
           returns corresponding brains.'''
        res = []   # We will begin by storing here a list of lists of brains.
        # Indeed, several queries may be performed.
        if 'Title' in params:
            # Execute the Title-related query
            tParams = params.copy()
            if 'indexExtractedText' in tParams:
                del tParams['indexExtractedText']
            if 'getRefcourrier' in tParams:
                del tParams['getRefcourrier']
            if 'gestDestOrigin' in tParams:
                del tParams['getDestOrigin']
            res.append(self.queryCatalog(tParams))
            del params['Title']  # The title has been "consumed".
        if 'indexExtractedText' in params:
            # Execute the extractedText-related query
            iParams = params.copy();
            if 'getRefcourrier' in iParams:
                del iParams['getRefcourrier']
            if 'getDestOrigin' in iParams:
                del iParams['getDestOrigin']
            res.append(self.queryCatalog(iParams))
            del params['indexExtractedText'] # The extractedText has been "consumed".
        if 'getRefcourrier' in params:
            # Execute the MailReference-related query
            rParams = params.copy();
            if 'getDestOrigin' in rParams:
                del rParams['getDestOrigin']
            res.append(self.queryCatalog(rParams))
            del params['getRefcourrier'] # The MailReference has been "consumed".
        if 'getDestOrigin' in params:
            res.append(self.queryCatalog(params))
        # No result yet? Execute the single query from p_params.
        if not res:
            res.append(self.queryCatalog(params))
        if len(res) == 1:
            return res[0]
        else:
#            print "Les titles"
#            for i in res[0]:
#                print i[8]
#
#            print "Les indexExtractedText"
#            for i in res[1]:
#                print i[8]

            sortKey = params['sort_on']
            return self.mergeResults(res, sortKey)

    def run(self):
        '''Creates and executes queries and returns the result.'''
        rq = self.searchParams
        # Determine the start number
        batchStart = int(self.rq.get('b_start', 0))
        # Determine "from" and "to" dates that determine the time period for
        # the search.
        fromDate = getDateFromRequest(rq.get('from_day'),
                                      rq.get('from_month'),
                                      rq.get('from_year'),
                                      start=True)
        toDate = getDateFromRequest(rq.get('to_day'),
                                    rq.get('to_month'),
                                    rq.get('to_year'),
                                    start=False)
        # Prepare the keywords query if keywords have been entered by the user
        if rq.get('keywords', None):
            self.keywords = prepareSearchValue(rq.get('keywords'))
        # Prepare main search parameters.
        mainParams = {'sort_order': self.sortOrder}
        # If a filter has been defined on a field (ie the user typed some
        # keywords in a column header for further filtering the search), we take
        # it into account here.
        if self.filterKey:
            mainParams[self.filterKey] = prepareSearchValue(self.filterValue)
        # Perform the search.
        batchSize = self.tool.getMaxShownFound()
        if self.searchedType == 'MeetingItem':
            params = self.getItemSearchParams(mainParams, [fromDate, toDate])
            itemBrains = self.queryCatalog(params)
            res = Batch(itemBrains, batchSize, batchStart, orphan=0)
        elif self.searchedType == 'Meeting':
            params = self.getMeetingSearchParams(mainParams, [fromDate, toDate])
            meetingBrains = self.queryCatalog(params)
            res = Batch(meetingBrains, batchSize, batchStart, orphan=0)
        elif self.searchedType == 'MeetingFile':
            params = self.getAnnexSearchParams(mainParams, [fromDate, toDate])
            annexBrains = self.searchAnnexes(params)
            res = Batch(annexBrains, batchSize, batchStart, orphan=0)
        elif self.searchedType == 'CourrierFile':
            params = self.getMailSearchParams(mainParams, [fromDate, toDate])
            mailBrains = self.searchMails(params)
            res = Batch(mailBrains, batchSize, batchStart, orphan=0)
        return res
# ------------------------------------------------------------------------------
