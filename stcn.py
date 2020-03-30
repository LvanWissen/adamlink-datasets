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


def main(fp=None):

    # If there was no format issue in the streets data, this function would
    # work. Instead, download the data yourself and point to it:
    # datasets = downloadDatasets(datasets=(GEBOUWEN, PERSONS, WIJKEN))

    dsG = rdflib.Dataset()  # rdflib Dataset
    rdfSubject.db = dsG  # hook onto rdfAlchemy

    TITLE = ["STCN"]
    DESCRIPTION = [
        Literal(
            """STCN Golden Agents dump. schema:PublicationEvents explicitly typed.""",
            lang='en'),
        Literal(
            """De STCN is de retrospectieve nationale bibliografie van Nederland voor de periode 1540-1800; ook opgenomen zijn summiere beschrijvingen van Nederlandse (post-)incunabelen.
Het bestand staat als wetenschappelijk bibliografisch onderzoeksinstrument aan iedereen ter beschikking. Uiteindelijk zal de STCN beschrijvingen bevatten van alle boeken die tot 1800 in Nederland zijn verschenen, en van alle boeken die buiten Nederland in de Nederlandse taal zijn gepubliceerd.

De STCN wordt samengesteld op basis van collecties in binnen- en buitenland. Alle boeken zijn met het boek in de hand (in autopsie) beschreven. De omvang van het bestand was begin 2018 ca. 210.000 titels in ongeveer 550.000 exemplaren. Het bestand wordt dagelijks uitgebreid.

De STCN wordt samengesteld en uitgegeven door de Koninklijke Bibliotheek.""",
            lang='nl')
    ]

    DATE = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
                   datatype=XSD.datetime)

    ds = Dataset(
        create.term('id/stcn/'),
        label=TITLE,
        name=TITLE,
        dctitle=TITLE,
        description=DESCRIPTION,
        dcdescription=DESCRIPTION,
        image=URIRef(
            "https://www.kb.nl/sites/default/files/styles/indexplaatje_conditional/public/stcn-00.jpg"
        ),
        url=[
            URIRef(
                "https://www.kb.nl/organisatie/onderzoek-expertise/informatie-infrastructuur-diensten-voor-bibliotheken/short-title-catalogue-netherlands-stcn"
            )
        ],
        temporalCoverage=[Literal("1540-01-01/1800-12-31")],
        spatialCoverage=[Literal("The Netherlands")],
        dateModified=DATE,
        dcdate=DATE,
        dcmodified=DATE,
        licenseprop=URIRef(
            "https://creativecommons.org/publicdomain/zero/1.0/"))

    # Add the datasets as separate graphs. Metadata on these graphs is in the

    # default graph.
    guri = create.term('id/stcn/')

    # download = DataDownload(None,
    #                         contentUrl=URIRef(uri),
    #                         encodingFormat="application/turtle")

    g = rdflib.Graph(identifier=guri)

    g.bind('schema', schema)
    g.bind('foaf', foaf)
    g.bind('dcterms', dcterms)
    g.bind('owl', OWL)
    g.bind('pnv', Namespace('https://w3id.org/pnv#'))
    g.bind('kbdef', Namespace('http://data.bibliotheken.nl/def#'))
    # g.bind('bio', Namespace('http://purl.org/vocab/bio/0.1/'))
    g.bind('sem', Namespace('http://semanticweb.cs.vu.nl/2009/11/sem/#'))
    g.bind('skos', Namespace('http://www.w3.org/2004/02/skos/core#'))
    g.bind('time', Namespace('http://www.w3.org/2006/time#'))

    turtlefiles = [
        os.path.join('data/stcn', i) for i in os.listdir('data/stcn')
        if i.endswith('.ttl')
    ]
    for n, f in enumerate(turtlefiles, 1):
        print(f"Parsing {n}/{len(turtlefiles)}\t {f}")
        g.parse(f, format='turtle')

    dsG.add_graph(g)

    ds.triples = sum(1 for i in g.subjects())

    dsG.bind('void', void)
    dsG.bind('dcterms', dcterms)
    dsG.bind('schema', schema)

    print("Serializing!")
    dsG.serialize('datasets/stcn.trig', format='trig')


if __name__ == "__main__":
    main()
