import os
import datetime
import shutil
import tempfile
import urllib.request

from typing import Iterable, Generator

import rdflib
from rdflib import Dataset, ConjunctiveGraph, Graph, URIRef, Literal, XSD, Namespace, RDFS, BNode, OWL

# pip install git+https://github.com/LvanWissen/RDFAlchemy.git
from rdfalchemy import rdfSubject, rdfMultiple, rdfSingle

create = Namespace("https://data.create.humanities.uva.nl/")
schema = Namespace("http://schema.org/")
void = Namespace("http://rdfs.org/ns/void#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
dcterms = Namespace("http://purl.org/dc/terms/")

rdflib.graph.DATASET_DEFAULT_GRAPH_ID = create


class Dataset(rdfSubject):
    """Dataset class, both a schema:Dataset and a void:Dataset.

    Indicate at least:
        * name (name of the dataset, str)
        * description (detailed description (Markdown allowed), str)

    See also: https://developers.google.com/search/docs/data-types/dataset
    """

    rdf_type = void.Dataset, schema.Dataset
    label = rdfMultiple(RDFS.label)

    ##########
    # schema #
    ##########

    name = rdfMultiple(schema.name)
    description = rdfMultiple(schema.description)
    alternateName = rdfMultiple(schema.alternateName)
    creator = rdfMultiple(schema.creator,
                          range_type=(schema.Person, schema.Organization))
    citation = rdfMultiple(schema.citation,
                           range_type=(Literal, schema.CreativeWork))
    hasPart = rdfMultiple(schema.hasPart, range_type=(URIRef, schema.Dataset))
    isPartOf = rdfSingle(schema.isPartOf, range_type=(URIRef, schema.Dataset))
    identifier = rdfMultiple(schema.identifier,
                             range_type=(URIRef, Literal,
                                         schema.PropertyValue))
    keywords = rdfMultiple(schema.keywords, range_type=Literal)
    license = rdfMultiple(schema.license,
                          range_type=(URIRef, schema.CreativeWork))
    sameAs = rdfMultiple(schema.sameAs, range_type=URIRef)
    spatialCoverage = rdfMultiple(schema.spatialCoverage,
                                  range_type=(Literal, schema.Place))
    temporalCoverage = rdfMultiple(schema.temporalCoverage, range_type=Literal)
    variableMeasured = rdfMultiple(schema.variableMeasured,
                                   range_type=(Literal, schema.PropertyValue))
    version = rdfMultiple(schema.sameAs, range_type=Literal)
    url = rdfMultiple(schema.url, range_type=URIRef)

    distribution = rdfMultiple(schema.distribution,
                               range_type=schema.DataDownload)
    dateModified = rdfSingle(schema.dateModified)

    ########
    # void #
    ########

    dctitle = rdfMultiple(dcterms.title)
    dcdescription = rdfMultiple(dcterms.description)
    dccreator = rdfMultiple(dcterms.creator)
    dcpublisher = rdfMultiple(dcterms.publisher)
    dccontributor = rdfMultiple(dcterms.contributor)
    dcsource = rdfSingle(dcterms.source)
    dcdate = rdfSingle(dcterms.date)
    dccreated = rdfSingle(dcterms.created)
    dcissued = rdfSingle(dcterms.issued)
    dcmodified = rdfSingle(dcterms.modified)

    dataDump = rdfSingle(void.dataDump)
    sparqlEndpoint = rdfSingle(void.sparqlEndpoint)
    exampleResource = rdfSingle(void.exampleResource)
    vocabulary = rdfMultiple(void.vocabulary)
    triples = rdfSingle(void.triples)

    inDataset = rdfSingle(void.inDataset)
    subset = rdfMultiple(void.subset)

    # I left out some very specific void properties.


class DataDownload(rdfSubject):
    """Class to point to a data dump download in the schema vocabulary.
    
    Indicate at least:
        * contentUrl (url to file)
        * encodingFormat (MIME type, str)
    """

    rdf_type = schema.DataDownload

    contentUrl = rdfSingle(schema.contentUrl)
    encodingFormat = rdfSingle(schema.encodingFormat)


class Linkset(Dataset):
    """Linkset class from the void vocabulary.
    
    Indicate at least:
        * target (2..*)
        * linkPredicate (property used to link entities (e.g. owl:sameAs))
    """

    rdf_type = void.Linkset

    target = rdfMultiple(void.target, range_type=void.Dataset)
    linkPredicate = rdfMultiple(void.linkPredicate, range_type=URIRef)


PREFIX = "https://adamlink.nl/data/rdf/"
STRATEN = "https://adamlink.nl/data/rdf/streets"
GEBOUWEN = "https://adamlink.nl/data/rdf/buildings"
PERSONS = "https://adamlink.nl/data/rdf/persons"
WIJKEN = "https://adamlink.nl/data/rdf/districts"


def downloadDatasets(datasets: Iterable) -> Generator[tuple, None, None]:
    """Download the adamlink datasets and temporarily store them.
    
    Args:
        datasets (Iterable): List of urls to datasets.
    
    Yields:
        Generator[tuple]: [description]
    """

    for ds in datasets:
        with urllib.request.urlopen(ds) as response:

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(response, tmp_file)

            yield (response.url, tmp_file.name)


def main():

    # If there was no format issue in the streets data, this function would
    # work. Instead, download the data yourself and point to it:
    # datasets = downloadDatasets(datasets=(GEBOUWEN, PERSONS, WIJKEN))
    datasets = [('https://adamlink.nl/data/rdf/streets',
                 'datasets/adamlinkstraten.ttl'),
                ('https://adamlink.nl/data/rdf/buildings',
                 'datasets/adamlinkgebouwen.ttl'),
                ('https://adamlink.nl/data/rdf/districts',
                 'datasets/adamlinkbuurten.ttl'),
                ('https://adamlink.nl/data/rdf/persons',
                 'datasets/adamlinkpersonen.ttl')]

    dsG = rdflib.Dataset()  # rdflib Dataset
    rdfSubject.db = dsG  # hook onto rdfAlchemy

    TITLE = ["Adamlink"]
    DESCRIPTION = [
        Literal(
            """Adamlink, een project van [Stichting AdamNet](http://www.adamnet.nl), wil Amsterdamse collecties verbinden en als LOD beschikbaar maken.

Om collecties te verbinden hebben we identifiers ([URIs](https://nl.wikipedia.org/wiki/Uniform_resource_identifier)) voor concepten als straten, personen en gebouwen nodig. Vaak zijn die al beschikbaar, bijvoorbeeld in de [BAG](https://nl.wikipedia.org/wiki/Basisregistraties_Adressen_en_Gebouwen), [RKDartists](https://rkd.nl/nl/explore/artists) of [Wikidata](https://www.wikidata.org).

Hier voegen we onze eigen Adamlink URIs aan die identifiers toe. Niet omdat we die beter vinden dan BAG, RKDartists of Wikidata, maar omdat bepaalde concepten - verdwenen straten bijvoorbeeld - niet in genoemde authority sets terug te vinden zijn. En omdat we op Adamlink allerlei naamvarianten van concepten bijeen kunnen brengen.

We proberen Adamlink als hub laten fungeren, door bijvoorbeeld bij een straat naar zowel BAG als Wikidata te verwijzen. Regelmatig nemen we data eerst op Adamlink op, bijvoorbeeld alle geportretteerden die we in de beeldbank van het Stadsarchief tegenkomen, om die personen vervolgens (zowel scriptsgewijs als handmatig) te verbinden met bestaande authority sets als Wikidata, Ecartico of RKDartists.

Maakt en publiceert u data met (historische) straat-, gebouw- of persoonsnamen? Gebruik dan altijd een identifier die door zoveel mogelijk anderen ook gebruikt wordt. U heeft dan toegang tot alle andere informatie die over zo'n concept beschikbaar is, zoals naamsvarianten of de locatie of de tijd waarin het concept leefde of bestond. En u verbindt uw data ook met de collecties van Amsterdamse erfgoedinstellingen.""",
            lang='nl'),
        Literal("Reference data for Amsterdam collections.", lang='en')
    ]
    DATE = Literal(datetime.datetime.now().strftime('%Y-%m-%d'),
                   datatype=XSD.datetime)

    ds = Dataset(create.term('id/adamlink/'),
                 label=TITLE,
                 name=TITLE,
                 dctitle=TITLE,
                 description=DESCRIPTION,
                 dcdescription=DESCRIPTION,
                 url=[URIRef("https://www.adamlink.nl/")],
                 temporalCoverage=[Literal("1275-10-27/..")],
                 spatialCoverage=[Literal("Amsterdam")],
                 dateModified=DATE,
                 dcdate=DATE,
                 dcmodified=DATE)

    subdatasets = []

    # Add the datasets as separate graphs. Metadata on these graphs is in the
    # default graph.
    for uri, fp in datasets:

        graphtype = uri.replace(PREFIX, '')
        guri = create.term('id/adamlink/' + graphtype + '/')

        TITLE = [f"Adamlink {graphtype.title()}"]
        DESCRIPTION = [
            Literal(
                f"Data over {graphtype} uit Adamlink - Referentiedata voor Amsterdamse collecties.",
                lang='nl'),
            Literal(
                f"Data on {graphtype} from Adamlink - Reference data for Amsterdam collections.",
                lang='en')
        ]

        download = DataDownload(None,
                                contentUrl=URIRef(uri),
                                encodingFormat="application/turtle")

        subds = Dataset(guri,
                        label=TITLE,
                        name=TITLE,
                        dctitle=TITLE,
                        description=DESCRIPTION,
                        dcdescription=DESCRIPTION,
                        url=[URIRef("https://www.adamlink.nl/")],
                        temporalCoverage=[Literal("1275-10-27/..")],
                        spatialCoverage=[Literal("Amsterdam")],
                        distribution=[download])

        # Add data to the respective graph
        print("Parsing", uri)
        subgraph = rdflib.Graph(identifier=guri)
        subgraph.parse(fp, format='turtle')

        dsG.add_graph(subgraph)
        subdatasets.append(subds)

    print("Adding more meta data and dataset relations")
    for subds in subdatasets:
        subds.isPartOf = ds
        subds.inDataset = ds

        subds.triples = sum(1 for i in subgraph.subjects())

    ds.hasPart = subdatasets
    ds.subset = subdatasets

    ds.triples = sum(
        1
        for i in dsG.graph(identifier=create.term('id/adamlink/')).subjects())

    dsG.bind('void', void)
    dsG.bind('dcterms', dcterms)
    dsG.bind('schema', schema)

    print("Serializing!")
    dsG.serialize('adamlink.trig', format='trig')


if __name__ == "__main__":
    main()