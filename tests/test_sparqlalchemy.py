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

    def test_import(self):
        self.assertEqual (len(self.sas), 30)

    def test_query(self):

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

        for row in res:
            for v in res.vars:
                logging.debug('sparql result row: %s=%s' % (v, row[v]))



if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    unittest.main()

