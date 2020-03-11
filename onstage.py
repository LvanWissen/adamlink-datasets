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


def main(fp='data/onstage.nt'):

    # If there was no format issue in the streets data, this function would
    # work. Instead, download the data yourself and point to it:
    # datasets = downloadDatasets(datasets=(GEBOUWEN, PERSONS, WIJKEN))

    dsG = rdflib.Dataset()  # rdflib Dataset
    rdfSubject.db = dsG  # hook onto rdfAlchemy

    TITLE = ["ONSTAGE"]
    DESCRIPTION = [
        Literal(
            """Online Datasystem of Theatre in Amsterdam from the Golden Age to the present. This is your address for questions about the repertoire, performances, popularity and revenues of the cultural program in Amsterdam’s public theatre during the period 1637 - 1772. All data provided in this system links to archival source materials in contemporary administration.

The [Shows page](http://www.vondel.humanities.uva.nl/onstage/shows/) gives you access by date to chronological lists of the theater program, and the plays staged per day. At the [Plays page](http://www.vondel.humanities.uva.nl/onstage/plays/) you have access to the repertoire by title, and for each play you will find its performances and revenues throughout time. At the [Persons page](http://www.vondel.humanities.uva.nl/onstage/persons/) you can access the data for playwrights, actors and actresses, and translators involved in the rich national and international variety of the Amsterdam Theater productions.

Go see your favorite play!""",
            lang='en')
    ]

    DATE = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
                   datatype=XSD.datetime)

    ds = Dataset(
        create.term('id/onstage/'),
        label=TITLE,
        name=TITLE,
        dctitle=TITLE,
        description=DESCRIPTION,
        dcdescription=DESCRIPTION,
        image=URIRef(
            "http://www.vondel.humanities.uva.nl/onstage/images/logo.png"),
        url=[URIRef("http://www.vondel.humanities.uva.nl/onstage/")],
        temporalCoverage=[Literal("1637-01-01/1772-12-31")],
        spatialCoverage=[Literal("Amsterdam")],
        dateModified=DATE,
        dcdate=DATE,
        dcmodified=DATE)

    # Add the datasets as separate graphs. Metadata on these graphs is in the

    # default graph.
    guri = create.term('id/onstage/')

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
        'onstage',
        Namespace('http://www.vondel.humanities.uva.nl/onstage/lod/vocab/#'))
    g.bind('bio', Namespace('http://purl.org/vocab/bio/0.1/'))
    g.bind('sem', Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/#'))
    g.bind('skos', Namespace('http://www.w3.org/2004/02/skos/core#'))
    g.bind('time', Namespace('http://www.w3.org/2006/time#'))

    g.parse(fp, format='nt')

    dsG.add_graph(g)

    ds.triples = sum(
        1 for i in g.subjects())

    dsG.bind('void', void)
    dsG.bind('dcterms', dcterms)
    dsG.bind('schema', schema)

    print("Serializing!")
    dsG.serialize('datasets/onstage.trig', format='trig')


if __name__ == "__main__":
    main()
