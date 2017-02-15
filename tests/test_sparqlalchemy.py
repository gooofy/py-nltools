#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2017 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
import logging
import codecs
import rdflib

from nltools import misc
from nltools.sparqlalchemy import SPARQLAlchemyStore

class TestSPARQLAlchemy (unittest.TestCase):

    def setUp(self):

        config = misc.load_config('.nlprc')

        #
        # db, store
        #

        db_url = config.get('db', 'url')
        self.sas = SPARQLAlchemyStore(db_url, 'unittests', echo=False)
        self.context = u'http://example.com'
        
        #
        # import triples to test on
        #

        self.sas.clear_graph(self.context)

        samplefn = 'tests/triples.n3'

        with codecs.open(samplefn, 'r', 'utf8') as samplef:

            data = samplef.read()

            self.sas.parse(data=data, context=self.context, format='n3')

    # @unittest.skip("temporarily disabled")
    def test_import(self):
        self.assertEqual (len(self.sas), 152)

    # @unittest.skip("temporarily disabled")
    def test_query_optional(self):

        sparql = """
                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                 PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                 PREFIX schema: <http://schema.org/>
                 PREFIX dbr: <http://dbpedia.org/resource/>
                 PREFIX dbo: <http://dbpedia.org/ontology/>
                 SELECT ?leader ?label ?leaderobj 
                 WHERE {
                     ?leader rdfs:label ?label. 
                     ?leader rdf:type schema:Person.
                     OPTIONAL {?leaderobj dbo:leader ?leader}
                 }
                 """

        res = self.sas.query(sparql)

        self.assertEqual(len(res), 24)

        for row in res:
            s = ''
            for v in res.vars:
                s += ' %s=%s' % (v, row[v])
            logging.debug('sparql result row: %s' % s)

    # @unittest.skip("temporarily disabled")
    def test_query_filter(self):

        sparql = """
                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                 PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                 PREFIX schema: <http://schema.org/>
                 PREFIX dbr: <http://dbpedia.org/resource/>
                 PREFIX dbo: <http://dbpedia.org/ontology/>
                 SELECT ?leader ?label ?leaderobj 
                 WHERE {
                     ?leader rdfs:label ?label. 
                     ?leader rdf:type schema:Person.
                     OPTIONAL {?leaderobj dbo:leader ?leader}
                     FILTER (lang(?label) = 'de')
                 }
                 """

        res = self.sas.query(sparql)

        self.assertEqual(len(res), 2)

        for row in res:
            s = ''
            for v in res.vars:
                s += ' %s=%s' % (v, row[v])
            logging.debug('sparql result row: %s' % s)

        sparql = """
                 PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
                 PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                 PREFIX schema: <http://schema.org/>
                 PREFIX dbr:    <http://dbpedia.org/resource/>
                 PREFIX dbo:    <http://dbpedia.org/ontology/>
                 PREFIX owl:    <http://www.w3.org/2002/07/owl#> 
                 PREFIX wdt:    <http://www.wikidata.org/prop/direct/> 
                 SELECT ?label ?birthPlace ?wdgenderlabel
                 WHERE {
                     ?chancellor rdfs:label ?label.
                     ?chancellor dbo:birthPlace ?birthPlace.
                     ?chancellor rdf:type schema:Person.
                     ?birthPlace rdf:type dbo:Settlement.
                     ?chancellor owl:sameAs ?wdchancellor.
                     ?wdchancellor wdt:P21 ?wdgender.
                     ?wdgender rdfs:label ?wdgenderlabel.
                     FILTER (lang(?label) = 'de')
                     FILTER (lang(?wdgenderlabel) = 'de')
                 }"""

        res = self.sas.query(sparql)

        self.assertEqual(len(res), 2)

        for row in res:
            s = ''
            for v in res.vars:
                s += ' %s=%s' % (v, row[v])
            logging.debug('sparql result row: %s' % s)

    # @unittest.skip("temporarily disabled")
    def test_distinct(self):

        sparql = """
                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                 PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                 PREFIX schema: <http://schema.org/>
                 PREFIX dbr: <http://dbpedia.org/resource/>
                 PREFIX dbo: <http://dbpedia.org/ontology/>
                 SELECT DISTINCT ?leader  
                 WHERE {
                     ?leader rdfs:label ?label. 
                     ?leader rdf:type schema:Person.
                 }
                 """

        res = self.sas.query(sparql)

        self.assertEqual(len(res), 2)

        for row in res:
            s = ''
            for v in res.vars:
                s += ' %s=%s' % (v, row[v])
            logging.debug('sparql result row: %s' % s)

    # @unittest.skip("temporarily disabled")
    def test_dates(self):

        sparql = """
                 PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                 PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                 PREFIX schema: <http://schema.org/>
                 PREFIX dbr: <http://dbpedia.org/resource/>
                 PREFIX dbo: <http://dbpedia.org/ontology/>
                 PREFIX hal: <http://hal.zamia.org/kb/> 
                 SELECT ?temp_min ?temp_max ?precipitation ?clouds ?icon
                 WHERE {
                     ?wev hal:dt_end ?dt_end. 
                     ?wev hal:dt_start ?dt_start.
                     ?wev hal:location dbr:Stuttgart.
                     ?wev hal:temp_min ?temp_min   .
                     ?wev hal:temp_max ?temp_max   .
                     ?wev hal:precipitation ?precipitation .
                     ?wev hal:clouds ?clouds .
                     ?wev hal:icon ?icon .
                     FILTER (?dt_start >= \"2016-12-04T10:20:13+05:30\"^^xsd:dateTime &&
                             ?dt_end   <= \"2016-12-23T10:20:13+05:30\"^^xsd:dateTime)
                 }
                 """

        res = self.sas.query(sparql)

        self.assertEqual(len(res), 2)

        for row in res:
            s = ''
            for v in res.vars:
                s += ' %s=%s' % (v, row[v])
            logging.debug('sparql result row: %s' % s)


# sparql_macro ('GERMAN_CHANCELLORS', "SELECT ?label ?leaderof
#                                      WHERE {
#                                          ?chancellor rdfs:label ?label.
#                                          ?chancellor rdf:type schema:Person.
#                                          ?chancellor dbp:office dbr:Chancellor_of_Germany.
#                                          OPTIONAL { ?leaderof dbo:leader ?chancellor }.
#                                          FILTER (lang(?label) = 'de')
#                                      }", L, LEADEROF).
# 

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    unittest.main()

