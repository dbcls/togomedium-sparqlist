# Get organisms by a growth medium ID

Retrieve organisms which are able to be cultured in the given growth medium.

## Parameters

* `gm_id` Growth medium ID
  * default: M6
  * examples: NBRC_M1005, JCM_M1, NBRC_M1039, SY1, HM_D00088_mse, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `count` count results

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT (DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/media>
WHERE {
  ?medium_id (dcterms:identifier | skos:altLabel) "{{gm_id}}" ;
    gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain rdf:type sio:SIO_010055 ;
    gmo:taxon ?taxon_url ;
    dcterms:identifier ?strain_id ;
    rdfs:label ?strain_name ;
    gmo:origin_strain/dcterms:identifier ?original_strain_name .
  ?taxon_url ddbj-tax:scientificName ?name ;
    dcterms:identifier ?tax_id  .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve organism information

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?tax_id ?name
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/media>
{
  ?medium_id (dcterms:identifier | skos:altLabel) "{{gm_id}}" ;
    gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain rdf:type sio:SIO_010055 ;
    gmo:taxon ?taxon_url ;
    dcterms:identifier ?strain_id ;
    rdfs:label ?strain_name ;
    gmo:origin_strain/dcterms:identifier ?original_strain_name .
  ?taxon_url ddbj-tax:scientificName ?name ;
    dcterms:identifier ?tax_id  .
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings ;
    let count_rows = count.results.bindings[0] ;
    let organisms = {} ;
    organisms.contents = [];

    organisms.total = 0;
    organisms.limit = 0;
    organisms.offset = 0;

    if (rows.length == 0) {
      return organisms;
    }

    for(let i = 0; i < rows.length; i++) {
      organisms.contents.push({
        tax_id: {label: rows[i].tax_id.value,
                 href: "/taxon/" + rows[i].tax_id.value},
        name: rows[i].name.value
      });
    }

    organisms.columns = [];
    organisms.columns.push({key: "tax_id", label: "Organism"});
    organisms.columns.push({key: "name", label: "Name"});
    organisms.total = count_rows.total.value;
    organisms.limit = count_rows.limit.value;
    organisms.offset = count_rows.offset.value;

    return organisms ;
  }
})
```
