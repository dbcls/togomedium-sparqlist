# Not yet implemented

List growth media used for organisms that belongs to the lower taxonomy rank of the specified NCBI taxonomy ID.

## Parameters

* `tax_id` NCBI taxID
  * default: 203404
  * examples: 410359, 266117, 1209989, 543526, 315405, 1409, 1931, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://togomedium.org/sparql

## `count` count results

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX taxncbi: <http://www.ncbi.nlm.nih.gov/taxonomy/>
PREFIX taxup: <http://purl.uniprot.org/taxonomy/>
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT ?gm) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
WHERE {
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  }
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  ?t dcterms:identifier {{tax_id}} .
  ?t taxont:scientificName ?name
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```



## `result` retrieve media information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX taxncbi: <http://www.ncbi.nlm.nih.gov/taxonomy/>
PREFIX taxup: <http://purl.uniprot.org/taxonomy/>
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT *
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
WHERE {
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  }
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  ?t dcterms:identifier {{tax_id}} .
  ?t taxont:scientificName ?name
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    // return {result,count};
    let rows = result.results.bindings;
    let count_rows = count.results.bindings[0];
    let media = {};
    media.contents = [];
    
    media.total = 0;
    media.limit = 0;
    media.offset = 0;
    
    if (rows.length == 0) {
      return media;      
    }
    
    for (let i = 0; i < rows.length; i++) {
      media.contents.push({
        gm_id: {label: rows[i].gm_id.value,
                href: "/medium/" + rows[i].gm.value},
        name: rows[i].label.value
      });
    }
    
    media.columns = [];
    media.columns.push({key: "gm_id", label: "Medium"});
    media.columns.push({key: "name", label: "Name"});
    media.total = count_rows.total.value ;
    media.limit = count_rows.limit.value ;
    media.offset = count_rows.offset.value ;
    return media ;
  }
})
```
