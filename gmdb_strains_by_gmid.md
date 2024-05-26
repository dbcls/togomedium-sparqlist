# Get strains by a growth medium ID

Retrieve strains which are able to be cultured in the given growth medium.

## Parameters

* `gm_id` Growth medium ID
  * default: M6
  * examples: NBRC_M1005, JCM_M1, NBRC_M1039, SY1, HM_D00088_mse, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://togomedium.org/sparql

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

SELECT (COUNT (DISTINCT ?strain) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
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

SELECT ?strain_id ?strain_name ?tax_id ?tax_name
  (GROUP_CONCAT(DISTINCT ?original_strain_id; SEPARATOR = ", ") AS ?original_strain_ids)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
FROM <http://togomedium.org/media>
{
  ?medium_id (dcterms:identifier | skos:altLabel) "{{gm_id}}" ;
    gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain rdf:type sio:SIO_010055 ;
    dcterms:identifier ?strain_id ;
    rdfs:label ?strain_name ;
    gmo:origin_strain/dcterms:identifier ?original_strain_id .
  OPTIONAL {
    ?strain gmo:taxon ?taxon_url .
    ?taxon_url dcterms:identifier ?tax_id ;
      rdfs:label ?tax_name .
  }
} GROUP BY ?strain_id ?strain_name ?tax_id ?tax_name
ORDER BY ?strain_name
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings ;
    let count_rows = count.results.bindings[0] ;
    let strains = {} ;
    strains.contents = [];

    strains.total = 0;
    strains.limit = 0;
    strains.offset = 0;

    if (rows.length == 0) {
      return strains;
    }

    for(let i = 0; i < rows.length; i++) {
      strains.contents.push({
        strain_id: {label: rows[i].strain_id.value,
                 href: "/strain/" + rows[i].strain_id.value},
        name: rows[i].strain_name.value,
        other_ids: rows[i].original_strain_ids.value,
        taxonomy: {label: rows[i].tax_name ? rows[i].tax_name.value : "",
                 href: rows[i].tax_id ? "/taxon/" + rows[i].tax_id.value : ""}
      });
    }

    strains.columns = [];
    strains.columns.push({key: "strain_id", label: "Strain ID"});
    strains.columns.push({key: "name", label: "Name"});
    strains.columns.push({key: "other_ids", label: "Other IDs"});
    strains.columns.push({key: "taxonomy", label: "Taxonomy"});
    strains.total = count_rows.total.value;
    strains.limit = count_rows.limit.value;
    strains.offset = count_rows.offset.value;

    return strains ;
  }
})
```
