import os
import datetime
import pandas as pd

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


def buildLinkset(csvfile: str, linkPredicate=OWL.sameAs,
                 identifier=None) -> rdflib.Graph:

    g = rdflib.Graph(identifier=identifier)
    rdfSubject.db = g

    g.bind('owl', OWL)

    df = pd.read_csv(csvfile)

    for link in df.to_dict(orient='records'):

        g.add((URIRef(link['uri1']), linkPredicate, URIRef(link['uri2'])))
        g.add((URIRef(link['uri2']), linkPredicate, URIRef(link['uri1'])))

    return g


def main(csvfile, linkPredicate, destination):

    g = buildLinkset(csvfile=csvfile,
                     linkPredicate=linkPredicate,
                     identifier=create.term('id/linkset/rijksmuseum/'))

    dsG = rdflib.Dataset()
    dsG.add_graph(g)

    DATE = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
                   datatype=XSD.datetime)

    rdfSubject.db = dsG
    ds = Linkset(
        create.term('id/linkset/rijksmuseum/'),
        name=[Literal("Rijksmuseum person linkset", lang='en')],
        description=[
            Literal(
                "Dataset that links Rijksmuseum persons to Wikidata and Ecartico. Data harvested from Europeana and Ecartico.",
                lang='en')
        ],
        dateModified=DATE,
        dcdate=DATE,
        dcmodified=DATE,
        target=[
            create.term('id/rijksmuseum/'),
            create.term('id/ecartico/'),
            URIRef("https://wikidata.org/")
        ],
        linkPredicate=[linkPredicate])

    linksetDs = Dataset(
        create.term('id/linkset/'),
        name=[Literal("Linkset collection", lang='en')],
        description=["Collection of linksets stored in this triplestore."])

    linksetDs.subset = [ds]
    linksetDs.hasPart = [ds]
    ds.isPartOf = linksetDs
    ds.inDataset = linksetDs

    dsG.bind('void', void)
    dsG.bind('dcterms', dcterms)
    dsG.bind('schema', schema)
    dsG.serialize(destination=destination, format='trig')


if __name__ == "__main__":
    main(csvfile='/home/leon/Downloads/rijksmuseum.csv',
         linkPredicate=OWL.sameAs,
         destination="datasets/linkset-rijksmuseum.trig")
"""
Should be combined with the output of:

```sparql
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX schema: <http://schema.org/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

CONSTRUCT {
  
    ?person owl:sameAs ?rijksuri .
    ?rijksuri owl:sameAs ?person .
}
  WHERE {
  GRAPH <https://data.create.humanities.uva.nl/id/adamlink/persons/> {
    ?person a schema:Person ;
  		owl:sameAs ?uri .
    
    FILTER(REGEX(?uri, "urn:rijksmuseum:people:", "i"))
    BIND(URI(REPLACE(STR(?uri), "urn:rijksmuseum:people:", "http://hdl.handle.net/10934/", "i")) AS ?rijksuri)
    
  } 
    
} LIMIT 100000
```

"""