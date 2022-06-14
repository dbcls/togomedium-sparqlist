# Get organisms by a growth medium ID

Retrieve organisms which are able to be cultured in the given growth medium.

## Parameters

* `gm_id` Growth medium ID
  * default: JCM_M13
  * examples: NBRC_M1005, JCM_M1, NBRC_M1039, SY1, HM_D00088_mse, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

## `count` count results

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT (DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/20210316>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
WHERE {
  ?media dcterms:identifier "{{gm_id}}" ;
    gmo:GMO_000114 ?media_strain .
  ?media_strain gmo:strain_id ?strain_id .
  ?strain_id gmo:taxon ?strain_tax .
  ?strain_tax dcterms:identifier ?tax_id .
  ?strain_tax taxont:scientificName ?name .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve organism information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?tax_id ?name
FROM <http://growthmedium.org/media/20210316>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
WHERE {
  ?media dcterms:identifier "{{gm_id}}" ;
    gmo:GMO_000114 ?media_strain .
  ?media_strain gmo:strain_id ?strain_id .
  ?strain_id gmo:taxon ?strain_tax .
  ?strain_tax dcterms:identifier ?tax_id .
  ?strain_tax taxont:scientificName ?name .
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
                 href: "/organism/" + rows[i].tax_id.value},
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
