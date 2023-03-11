# List all growth media (for pagination)

Show a list of growth media with the given keyword.

## Parameters

* `limit` limit
  * default: 50
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

## `count` count results

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT (COUNT(DISTINCT ?gm) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
    ?gm a gmo:GMO_000001 ;
        dcterms:identifier ?gm_id {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  } UNION {
    ?gm rdfs:label|gmo:GMO_000102 ?label ;
        gmo:GMO_000114 ?org .
    ?org gmo:GMO_000020 ?t .
    ?t taxont:scientificName ?name
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media 

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT DISTINCT ?gm ?gm_id ?label
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/0.18/>

WHERE {
    ?gm a gmo:GMO_000001 ;
        dcterms:identifier ?gm_id {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  } UNION {
    ?gm rdfs:label|gmo:GMO_000102 ?label ;
        gmo:GMO_000114 ?org .
    ?org gmo:GMO_000020 ?t .
    ?t taxont:scientificName ?name
  }
}
ORDER BY ?gm
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {

    let count_rows = count.results.bindings[0] ;
    let rows = result.results.bindings ;
    let gms_with_taxonomy = [] ;
    let gms_wo_taxonomy = [] ;
    let contents = [];
    let columns = [];
    let gms = {};
    
    gms.total = 0;
    gms.limit = 0;
    gms.offset = 0;
    
    if (rows.length == 0) {
      gms.contents = [];
      return gms;
    }
    
    for (let i = 0; i < rows.length ;i++) {
      gms_with_taxonomy.push({
        gm_id: {
          label: rows[i].gm_id.value,
          href: "/medium/" + rows[i].gm_id.value,
        },
        name: rows[i].label.value
      });
    }
    
    contents = gms_with_taxonomy.concat(gms_wo_taxonomy);
    gms.contents = contents;
    gms.columns = [];
    gms.columns.push({key: "gm_id", label: "Medium"});
    gms.columns.push({key: "name", label: "Name"});
    gms.total = count_rows.total.value ;
    gms.limit = count_rows.limit.value ;
    gms.offset = count_rows.offset.value ;
    return gms;
  }
})
```
