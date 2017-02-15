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

#
# quick'n'dirty rdf triple store using rdflib and sqlalchemy
#

import os
import sys
import traceback
import codecs
import logging
import requests
import StringIO

from time import time
from optparse import OptionParser

from nltools import misc

import rdflib
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql             import parser, algebra

from sqlalchemy import create_engine, sql, func
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, UnicodeText, Index

def format_algebra(f, q):

    def pp(f, p, ind=u""):

        # logging.debug('pp(p=%s)' % repr(p))

        f.write(u"|%s%s(\n" % (ind, p.name))
        for k in p:
            if not isinstance(p[k], CompValue):
                f.write (u'|%s  %s = %s\n' % (ind, k, unicode(p[k])))
            else:
                f.write('|%s  %s =\n' % (ind, k))
                pp(f, p[k], ind + u"    ")

        f.write(u"|%s)\n" % ind)

    try:
        pp(f, q.algebra)
    except AttributeError:
        # it's update, just a list
        for x in q:
            pp(f, x)


class SPARQLAlchemyStore(object):

    def __init__(self, db_url, tablename, echo=False):

        self.db_url = db_url

        self.metadata = MetaData()

        self.quads = Table(tablename, self.metadata,
            Column('id',       Integer, primary_key=True),
            Column('s',        UnicodeText, index=True),
            Column('p',        UnicodeText, index=True),
            Column('o',        UnicodeText, index=True),
            Column('context',  UnicodeText, index=True),
            Column('lang',     String,      index=True),
            Column('datatype', String),
        )

        Index('idx_%s_spo' % tablename, self.quads.c.s, self.quads.c.p, self.quads.c.o)

        self.engine = create_engine(db_url, echo=echo)

        self.metadata.create_all(self.engine)

    def remove(self, triple, context):
        """Remove a triple from the store."""
        subject, predicate, obj = triple
        logging.error('Unimplemented method: remove(%s)' % repr((triple, context)))

    # def add(self, triple, context=None):
    #     """Add a triple to the store of triples."""
    #     subject, predicate, obj = triple

    #     logging.error('Unimplemented method: add(%s)' % repr((triple, context, quoted)))


    def clear_graph(self, context):

        logging.debug('clear_graph(%s)' % repr(context))

        conn = self.engine.connect()

        stmt = self.quads.delete().where(self.quads.c.context == context)

        conn.execute(stmt)

        conn.close()

    def __len__(self):
        stmt = sql.select([func.count(self.quads.c.id)]).as_scalar()
        conn = self.engine.connect()
        res = conn.execute(sql.select([stmt])).fetchall()
        conn.close()

        logging.debug('__len__: %s' % repr(res))

        return res[0][0]
        

    def addN(self, quads):

        logging.debug('addN(quads)')

        values = []
        cnt    = 0
        for s, p, o, context in quads:

            if isinstance(o, rdflib.Literal):
                ov = unicode(o.value)
                ot = o.datatype
                ol = o.language
            else:
                ov = unicode(o)
                ot = None
                ol = None

            values.append({'b_s'       : s, 
                           'b_p'       : p, 
                           'b_o'       : ov, 
                           'b_context' : unicode(context.identifier),
                           'b_lang'    : ol,
                           'b_datatype': ot })
            cnt += 1
            # logging.debug('quad: %s' % repr(( s,p,o,context, ov, ot, ol)))

        logging.debug('addN: %d quads to add.' % cnt)

        conn = self.engine.connect()

        # first delete existing quads so we have no duplicate edges in our graph

        logging.debug('addN: delete old quads...')
    
        stmt = self.quads.delete()\
                         .where(self.quads.c.s == sql.bindparam('b_s'))\
                         .where(self.quads.c.p == sql.bindparam('b_p'))\
                         .where(self.quads.c.o == sql.bindparam('b_o'))\
                         .where(self.quads.c.context == sql.bindparam('b_context'))

        conn.execute(stmt, values)

        # now, insert quads

        logging.debug('addN: insert new quads...')

        stmt = self.quads.insert().values(\
                         s        = sql.bindparam('b_s'), \
                         p        = sql.bindparam('b_p'), \
                         o        = sql.bindparam('b_o'), \
                         context  = sql.bindparam('b_context'),
                         lang     = sql.bindparam('b_lang'),
                         datatype = sql.bindparam('b_datatype'))

        conn.execute(stmt, values)

        conn.close()

        logging.debug('addN: done.')

        # alternative implementation: "upsert" (not supported by all sqlalchemy DB backends yet

        # update_cte = (
        #     triples.update()
        #     .where(triples.c.s == sql.bindparam('b_s'))
        #     .where(triples.c.p == sql.bindparam('b_p'))
        #     .where(triples.c.o == sql.bindparam('b_o'))
        #     .values(s = sql.bindparam('b_s'))
        #     .returning(sql.literal(1))
        #     .cte('update_cte')
        # )

        # stmt = triples.insert().from_select([ triples.c.s,
        #                                       triples.c.p,
        #                                       triples.c.o,
        #                                     ],
        #                                     sql.select([sql.bindparam('b_s'),
        #                                                 sql.bindparam('b_p'),
        #                                                 sql.bindparam('b_o')
        #                                                 ])
        #                                     .where(~sql.exists(update_cte.select()))
        #                                 )
        # conn = engine.connect()
        # conn.execute(stmt, values)
        # conn.close()

    def parse(self, source=None, publicID=None, format="xml",
              location=None, file=None, data=None, context=u'http://example.com', **args):

        logging.debug('parsing to memory...')

        cj = rdflib.ConjunctiveGraph()
        memg = cj.get_context(context)
        memg.parse(source=source, publicID=publicID, format=format, location=location, 
                   file=file, data=data, **args)

        quads = cj.quads()

        logging.debug('addN ...')
        self.addN(quads)


    def _check_keys(self, d, keys):
        """ensure dict d has only the given keys"""
        for k in d:
            if not (k in keys):
                raise Exception ('unexpected key found: %s' % k)

    #
    # convert an expression to sqlalchemy operators
    #

    def _expr2alchemy(self, node, var_map, var_lang, var_dts):

        res = None

        if isinstance(node, rdflib.term.Literal):
            res = unicode(node)

        elif isinstance(node, rdflib.term.Variable):

            res = var_map[unicode(node)]

        elif node.name == 'RelationalExpression':

            self._check_keys(node, set(['expr', 'op', 'other', '_vars']))

            if node['op'] == '=':

                o1 = self._expr2alchemy(node['expr'], var_map, var_lang, var_dts)
                o2 = self._expr2alchemy(node['other'], var_map, var_lang, var_dts)

                res = o1 == o2

            elif node['op'] == '>=':

                o1 = self._expr2alchemy(node['expr'], var_map, var_lang, var_dts)
                o2 = self._expr2alchemy(node['other'], var_map, var_lang, var_dts)

                res = o1 >= o2

            elif node['op'] == '<=':

                o1 = self._expr2alchemy(node['expr'], var_map, var_lang, var_dts)
                o2 = self._expr2alchemy(node['other'], var_map, var_lang, var_dts)

                res = o1 <= o2

            else:
                raise Exception ('RelationalExpression op %s unknown.' % node['op'])

        elif node.name == 'Builtin_LANG':

            self._check_keys(node, set(['arg', '_vars']))

            # logging.debug ('arg=%s' % node['arg'].__class__)

            if not isinstance (node['arg'], rdflib.term.Variable):
                raise Exception ('Builtin_LANG: argumented expected to be a variable.')

            res = var_lang[unicode(node['arg'])]

        elif node.name == 'ConditionalAndExpression':

            self._check_keys(node, set(['expr', 'other', '_vars']))

            res = self._expr2alchemy(node['expr'], var_map, var_lang, var_dts)

            for e in node['other']:
                
                o = self._expr2alchemy(e, var_map, var_lang, var_dts)

                res = sql.and_(res, o)

        else:

            raise Exception ('expression node type %s unknown.' % node.name)

        return res

    #
    # convert a sparql select statement to an sqlalchemy SELECT statement
    #

    def _algebra2alchemy(self, node):

        res        = None
        var_map    = {}
        var_lang   = {}
        var_dts    = {}

        if node.name == 'SelectQuery':

            self._check_keys(node, set(['p', 'datasetClause', '_vars', 'PV']))

            assert node['datasetClause'] is None # FIXME: implement

            p_stmt, p_var_map, p_var_lang, p_var_dts = self._algebra2alchemy(node['p'])

            for v in node['PV']:
                var_name = unicode(v)
                var_map[var_name] = p_var_map[var_name]

                if var_name in p_var_lang:
                    var_lang[var_name] = p_var_lang[var_name]
                if var_name in p_var_dts:
                    var_dts[var_name] = p_var_dts[var_name]

            sel_list = []
            for var_name in var_map:
                sel_list.append(var_map[var_name].label(var_name))
            for var_name in var_lang:
                sel_list.append(var_lang[var_name].label(var_name + '_lang'))
            for var_name in var_dts:
                sel_list.append(var_dts[var_name].label(var_name + '_dt'))

            res = sql.select(sel_list).select_from(p_stmt).alias()

            for var_name in var_map:
                var_map[var_name] = res.c[var_name]
            for var_name in var_lang:
                var_lang[var_name] = res.c[var_name + '_lang']
            for var_name in var_dts:
                var_dts[var_name] = res.c[var_name + '_dt']

            logging.debug('SelectQuery: res: %s' % res.compile(compile_kwargs={"literal_binds": True}))

        elif node.name == 'Project':

            self._check_keys(node, set(['p', '_vars', 'PV']))

            p_stmt, p_var_map, p_var_lang, p_var_dts = self._algebra2alchemy(node['p'])

            for v in node['PV']:
                var_name = unicode(v)
                var_map[var_name] = p_var_map[var_name]

                if var_name in p_var_lang:
                    var_lang[var_name] = p_var_lang[var_name]
                if var_name in p_var_dts:
                    var_dts[var_name] = p_var_dts[var_name]

            sel_list = []
            for var_name in var_map:
                sel_list.append(var_map[var_name].label(var_name))
            for var_name in var_lang:
                sel_list.append(var_lang[var_name].label(var_name + '_lang'))
            for var_name in var_dts:
                sel_list.append(var_dts[var_name].label(var_name + '_dt'))

            res = sql.select(sel_list).select_from(p_stmt).alias()

            for var_name in var_map:
                var_map[var_name] = res.c[var_name]
            for var_name in var_lang:
                var_lang[var_name] = res.c[var_name + '_lang']
            for var_name in var_dts:
                var_dts[var_name] = res.c[var_name + '_dt']

            logging.debug('Project: res: %s' % res.compile(compile_kwargs={"literal_binds": True}))

        elif node.name == 'Filter':

            self._check_keys(node, set(['p', 'expr', '_vars']))
            p_stmt, var_map, var_lang, var_dts = self._algebra2alchemy(node['p'])

            expr = self._expr2alchemy(node['expr'], var_map, var_lang, var_dts)

            sel_list = []
            for var_name in var_map:
                sel_list.append(var_map[var_name].label(var_name))
            for var_name in var_lang:
                sel_list.append(var_lang[var_name].label(var_name + '_lang'))
            for var_name in var_dts:
                sel_list.append(var_dts[var_name].label(var_name + '_dt'))

            res = sql.select(sel_list).select_from(p_stmt).where(expr).alias()

            for var_name in var_map:
                var_map[var_name] = res.c[var_name]
            for var_name in var_lang:
                var_lang[var_name] = res.c[var_name + '_lang']
            for var_name in var_dts:
                var_dts[var_name] = res.c[var_name + '_dt']

            logging.debug('Filter: res: %s' % res.compile(compile_kwargs={"literal_binds": True}))

        elif node.name == 'Distinct':

            self._check_keys(node, set(['p', '_vars']))
            p_stmt, var_map, var_lang, var_dts = self._algebra2alchemy(node['p'])

            sel_list = []
            for var_name in var_map:
                sel_list.append(var_map[var_name].label(var_name))
            for var_name in var_lang:
                sel_list.append(var_lang[var_name].label(var_name + '_lang'))
            for var_name in var_dts:
                sel_list.append(var_dts[var_name].label(var_name + '_dt'))

            res = sql.select(sel_list).select_from(p_stmt).distinct().alias()

            for var_name in var_map:
                var_map[var_name] = res.c[var_name]
            for var_name in var_lang:
                var_lang[var_name] = res.c[var_name + '_lang']
            for var_name in var_dts:
                var_dts[var_name] = res.c[var_name + '_dt']

            logging.debug('Filter: res: %s' % res.compile(compile_kwargs={"literal_binds": True}))

        elif node.name == 'LeftJoin':

            self._check_keys(node, set(['p1', 'p2', 'expr', '_vars']))

            # FIXME: proper expression support needed
            assert node['expr'].name == 'TrueFilter'
            self._check_keys(node['expr'], set(['_vars']))
            assert len(node['expr']['_vars']) == 0

            p1_stmt, p1_var_map, p1_var_lang, p1_var_dts = self._algebra2alchemy(node['p1'])
            p2_stmt, p2_var_map, p2_var_lang, p2_var_dts = self._algebra2alchemy(node['p2'])

            on_expr = sql.expression.true()

            for var_name in p1_var_map:
                var_map[var_name] = p1_var_map[var_name]
            for var_name in p1_var_lang:
                var_lang[var_name] = p1_var_lang[var_name]
            for var_name in p1_var_dts:
                var_dts[var_name] = p1_var_dts[var_name]

            for var_name in p2_var_map:
                if not var_name in p1_var_map:
                    var_map[var_name] = p2_var_map[var_name]
                    continue
                on_expr = sql.expression.and_(on_expr, p1_var_map[var_name] == p2_var_map[var_name])
            for var_name in p2_var_lang:
                if not var_name in p1_var_lang:
                    var_lang[var_name] = p2_var_lang[var_name]
            for var_name in p2_var_dts:
                if not var_name in p1_var_dts:
                    var_dts[var_name] = p2_var_dts[var_name]
        
            sel_list = []
            for var_name in var_map:
                sel_list.append(var_map[var_name].label(var_name))
            for var_name in var_lang:
                sel_list.append(var_lang[var_name].label(var_name + '_lang'))
            for var_name in var_dts:
                sel_list.append(var_dts[var_name].label(var_name + '_dt'))

            res = sql.select(sel_list).select_from(p1_stmt.outerjoin(p2_stmt, on_expr)).alias()

            for var_name in var_map:
                var_map[var_name] = res.c[var_name]
            for var_name in var_lang:
                var_lang[var_name] = res.c[var_name + '_lang']
            for var_name in var_dts:
                var_dts[var_name] = res.c[var_name + '_dt']

            logging.debug('LeftJoin: res: %s' % res.compile(compile_kwargs={"literal_binds": True}))

        elif node.name == 'BGP':

            self._check_keys(node, set(['triples', '_vars']))

            for t in node['triples']:

                logging.debug('BGP: t=%s' % repr(t))

                where_clause   = sql.expression.true()
                columns        = []
                new_var_map    = {}
                new_var_lang   = {}
                new_var_dts    = {}

                for c_idx, c_name in enumerate (['s','p','o']):

                    if isinstance (t[c_idx], rdflib.term.URIRef):
                        where_clause = sql.expression.and_(where_clause, self.quads.c[c_name] == unicode(t[c_idx]))

                    elif isinstance (t[c_idx], rdflib.term.Variable):
                        var_name = unicode(t[c_idx])

                        if not var_name in new_var_map:
                            col = self.quads.c[c_name].label(var_name)
                            new_var_map[var_name] = col
                            columns.append(col)
                        else:
                            col = self.quads.c[c_name]
                            where_clause = sql.expression.and_(where_clause, new_var_map[var_name] == col)

                        # label / datatype information ?
                        if c_name == 'o':

                            if not var_name in new_var_lang:
                                col = self.quads.c['lang'].label(var_name+'_lang')
                                new_var_lang[var_name] = col
                                columns.append(col)

                            if not var_name in new_var_dts:
                                col = self.quads.c['datatype'].label(var_name+'_dt')
                                new_var_dts[var_name] = col
                                columns.append(col)


                sel = sql.select(columns).where(where_clause).alias()

                if res is None:
                    res = sel

                    for var_name in new_var_map:
                        var_map[var_name] = sel.c[var_name]
                    for var_name in new_var_lang:
                        var_lang[var_name] = sel.c[var_name + '_lang']
                    for var_name in new_var_dts:
                        var_dts[var_name] = sel.c[var_name + '_dt']

                else:

                    # generate join

                    on_expr      = sql.expression.true()
                    for var_name in new_var_map:
                        if not var_name in var_map:
                            var_map[var_name] = sel.c[var_name]
                        else:
                            on_expr = sql.expression.and_(on_expr, var_map[var_name] == sel.c[var_name])

                    for var_name in new_var_lang:
                        if not var_name in var_lang:
                            var_lang[var_name] = sel.c[var_name + '_lang']
                    for var_name in new_var_dts:
                        if not var_name in var_dts:
                            var_dts[var_name] = sel.c[var_name + '_dt']


                    j = res.join(sel, on_expr)

                    # generate select from join

                    columns      = []
                    for var_name in var_map:
                        columns.append(var_map[var_name].label(var_name))
                    for var_name in var_lang:
                        columns.append(var_lang[var_name].label(var_name + '_lang'))
                    for var_name in var_dts:
                        columns.append(var_dts[var_name].label(var_name + '_dt'))

                    res = sql.select(columns).select_from(j).alias()

                    for var_name in var_map:
                        var_map[var_name] = res.c[var_name]
                    for var_name in var_lang:
                        var_lang[var_name] = res.c[var_name + '_lang']
                    for var_name in var_dts:
                        var_dts[var_name] = res.c[var_name + '_dt']
               
                logging.debug('BGP: res: %s ' % res.compile(compile_kwargs={"literal_binds": True}))

        else:

            raise Exception ('node type %s unknown.' % node.name)

        return res, var_map, var_lang, var_dts

    def query(self, q):

        global engine

        logging.debug(q)

        start_time = time()
        pq = parser.parseQuery(q)
        logging.info ('parsing took %fs' % (time() - start_time))

        logging.debug(pq)
        tq = algebra.translateQuery(pq)

        sio = StringIO.StringIO()
        format_algebra(sio, tq)
        sio.seek(0)
        while True:
            line = sio.readline()
            if not line:
                break
            logging.debug(line.strip())

        # print 'tq.prologue:', tq.prologue

        stmt, var_map, var_lang, var_dts = self._algebra2alchemy(tq.algebra)

        logging.debug("executing SQL ...")

        conn = self.engine.connect()

        result = conn.execute(stmt)

        #
        # transform result into rdflib's data structure
        #

        qres = rdflib.query.Result('SELECT')

        rrows = []
        vs    = {}
        for var_name in var_map:
            vs[var_name] = rdflib.term.Variable(var_name)

        logging.debug('result: %s' % repr(result))

        for row in result:
            logging.debug('   row: %s' % repr(row))

            d = {}
            l = []
            for var_name in var_map:
                v = vs[var_name]
                l.append(v)

                lang_col = var_lang[var_name].name if var_name in var_lang else None
                dt_col   = var_dts[var_name].name  if var_name in var_dts  else None

                o    = row[var_name]
                lang = row[lang_col] if lang_col else None
                dt   = row[dt_col]   if dt_col else None

                if lang or dt or not o:
                    d[v] = rdflib.Literal(o, lang=lang, datatype=dt)
                else:
                    d[v] = rdflib.URIRef(o)

            # rr=ResultRow({ Variable('a'): URIRef('urn:cake') }, [Variable('a')])
            rrows.append(rdflib.query.ResultRow(d, l))


        qres.vars     = vs
        qres.bindings = rrows

        conn.close()

        return qres


if __name__ == '__main__':

    #
    # init, cmdline
    #

    misc.init_app('sparqlalchemy')

    option_parser = OptionParser("usage: %prog [options] foo.aiml")

    option_parser.add_option ("-s", "--echo-sql", action="store_true", dest="echo",
                       help="echo sql statements")

    option_parser.add_option ("-v", "--verbose", action="store_true", dest="verbose",
                       help="verbose output")

    (options, args) = option_parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
        if not options.echo:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO)

    config = misc.load_config('.nlprc')

    #
    # db, store
    #

    db_url = config.get('db', 'url')
    sas = SPARQLAlchemyStore(db_url, 'knowledgebase', echo=options.echo)

    #
    # parse sample files, add quads to store
    #

    for sfn in os.listdir('mirror'):

        samplefn = 'mirror/%s' % sfn
        context = u'http://example.com'

        with codecs.open(samplefn, 'r', 'utf8') as samplef:

            data = samplef.read()

            logging.debug('parsing to %s memory...' % samplefn)
            cj = rdflib.ConjunctiveGraph()
            memg = cj.get_context(context)
            memg.parse(format='n3', data=data)

            quads = cj.quads()

            logging.debug('addN ...')
            sas.addN(quads)

    # sas.clear_graph(context)

