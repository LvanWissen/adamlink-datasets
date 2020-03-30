import os
import datetime
import shutil
import tempfile
import urllib.request

from typing import Iterable, Generator

import rdflib
from rdflib import Dataset, ConjunctiveGraph, Graph, URIRef, Literal, XSD, Namespace, RDFS, BNode, OWL

from ontology import Dataset, DataDownload, Linkset, rdfSubject

create = Namespace("https://data.create.humanities.uva.nl/")
schema = Namespace("http://schema.org/")
void = Namespace("http://rdfs.org/ns/void#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
dcterms = Namespace("http://purl.org/dc/terms/")

rdflib.graph.DATASET_DEFAULT_GRAPH_ID = create
rdflib.NORMALIZE_LITERALS = False


def main(fp='data/ecartico.nt'):

    # If there was no format issue in the streets data, this function would
    # work. Instead, download the data yourself and point to it:
    # datasets = downloadDatasets(datasets=(GEBOUWEN, PERSONS, WIJKEN))

    dsG = rdflib.Dataset()  # rdflib Dataset
    rdfSubject.db = dsG  # hook onto rdfAlchemy

    TITLE = ["ECARTICO"]
    DESCRIPTION = [
        Literal(
            """Linking cultural industries in the early modern Low Countries, ca. 1475 - ca. 1725. ECARTICO is a comprehensive collection of structured biographical data concerning painters, engravers, printers, book sellers, gold- and silversmiths and others involved in the ‘cultural industries’ of the Low Countries in the sixteenth and seventeenth centuries. As in other biographical databases, users can [search and browse](http://www.vondel.humanities.uva.nl/ecartico/persons/) for data on individuals or make selections of certain types of data. However, ECARTICO also allows users to [visualize and analyze](http://www.vondel.humanities.uva.nl/ecartico/analysis/) data on cultural entrepreneurs and their ‘milieus’.

## Focus on analysis

The focus on analysis sets ECARTICO apart from other (biographical) resources in this field. One of the reasons to start with ECARTICO was that we felt that available resources were primarily designed for storage and retrieval of single data with little ‑ if any ‑ opportunities for aggregation and analysis. As a consequence other resources also offer poor support for modelling social and genealogical networks.

ECARTICO was not designed as an electronic reference work, although it can be used as such. Rather think of ECARTICO as a ‘social medium’ for the cultural industries of the Dutch and Flemish Golden Ages.

## Old and new data

ECARTICO is standing on the shoulders of giants. Much of the data present in ECARTICO is derived from the wealth of biographical and genealogical studies, that has been published over the last centuries. Also much data is derived from original research on primary sources. Many biographical details can be found in ECARTICO, that can not be found anywhere else.

## History

ECARTICO has its roots in the research project [Economic and Artistic Competition in the Amsterdam art market c. 1630-1690: history painting in Amsterdam in Rembrandt's time](http://www.nwo.nl/onderzoek-en-resultaten/onderzoeksprojecten/19/2300136219.html), which was funded by the [Netherlands Organisation for Scientific Research](http://www.nwo.nl/), and headed by Eric Jan Sluijter and Marten Jan Bok. Initially it was intended as a prosopographical research database dealing with history painters in seventeenth century Amsterdam. However, the scope of the database has become much wider because we could build upon data compiled by Pieter Groenendijk for [his lexicon (2006)](http://www.primaverapers.nl/shop/index.php?main_page=product_info&cPath=16_12&products_id=151) of 16th and 17th century visual artists from the Northern and the Southern Netherlands.

During the period 2010-2013 ECARTICO was further expanded within the research project The Cultural Industry of Amsterdam in the Golden Age, which was funded by the [The Royal Netherlands Academy of Arts and Sciences](http://www.knaw.nl/), and headed by Eric Jan Sluijter and Harm Nijboer. As part of this project the scope of ECARTICO has widened to other cultural industries like printing, publishing, sculpture, goldsmithery and theatre.

## Lacunae

Up until now, data entry has been strongly inclined towards the Dutch Republic and with a focus on Amsterdam. Especially the Southern Netherlands are still underrepresented. For instance, data from the Antwerp _Liggeren_ and the Bruges _Memorielijst_ have not been entered systematically, yet.

At this moment ECARTICO is still mostly geared towards visual artists. However we are catching up with publishers and printers at a fast pace.

Do you want to assist in expanding ECARTICO? Please contact us!

## Future development

New data are added on an almost daily base. Meanwhile the technological infrastructure of ECARTICO is kept under continuous review.

Current projects are:

*   Adding data on Dutch printers and publishers, prior to 1720
*   Implementation of revision management
*   Making ECARTICO available as Linked Open Data""",
            lang='en')
    ]

    DATE = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
                   datatype=XSD.datetime)

    ds = Dataset(
        create.term('id/ecartico/'),
        label=TITLE,
        name=TITLE,
        dctitle=TITLE,
        description=DESCRIPTION,
        dcdescription=DESCRIPTION,
        image=URIRef(
            "http://www.vondel.humanities.uva.nl/ecartico/images/logo.png"),
        url=[URIRef("http://www.vondel.humanities.uva.nl/ecartico/")],
        temporalCoverage=[Literal("1475-01-01/1725-12-31")],
        spatialCoverage=[Literal("The Netherlands")],
        dateModified=DATE,
        dcdate=DATE,
        dcmodified=DATE,
        licenseprop=URIRef("https://creativecommons.org/licenses/by-sa/3.0/"))

    # Add the datasets as separate graphs. Metadata on these graphs is in the

    # default graph.
    guri = create.term('id/ecartico/')

    # download = DataDownload(None,
    #                         contentUrl=URIRef(uri),
    #                         encodingFormat="application/turtle")

    g = rdflib.Graph(identifier=guri)

    g.bind('schema', schema)
    g.bind('foaf', foaf)
    g.bind('dcterms', dcterms)
    g.bind('owl', OWL)
    g.bind('pnv', Namespace('https://w3id.org/pnv#'))
    g.bind(
        'ecartico',
        Namespace('http://www.vondel.humanities.uva.nl/ecartico/lod/vocab/#'))
    g.bind('bio', Namespace('http://purl.org/vocab/bio/0.1/'))
    g.bind('sem', Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/#'))
    g.bind('skos', Namespace('http://www.w3.org/2004/02/skos/core#'))
    g.bind('time', Namespace('http://www.w3.org/2006/time#'))

    g.parse(fp, format='nt')

    dsG.add_graph(g)

    ds.triples = sum(1 for i in g.subjects())

    dsG.bind('void', void)
    dsG.bind('dcterms', dcterms)
    dsG.bind('schema', schema)

    print("Serializing!")
    dsG.serialize('datasets/ecartico.trig', format='trig')


if __name__ == "__main__":
    main()
