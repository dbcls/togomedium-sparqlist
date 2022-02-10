# Get growth media by a GMO ID

Retrieve growth media including a component with the given GMO ID.

## Parameters

* `gmo_id` GMO ID
  * default: GMO_001020
  * examples: GMO_001584, GMO_001018, GMO_001054, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

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
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX mccv:  <http://purl.jp/bio/10/mccv#>

SELECT (COUNT(DISTINCT ?gm) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
WHERE {
  ?gmo dcterms:identifier "{{gmo_id}}" .
  ?gm gmo:GMO_000104 ?gmo .
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media

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
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX mccv:  <http://purl.jp/bio/10/mccv#>

SELECT DISTINCT ?gm ?gm_id ?label
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
WHERE {
  ?gmo dcterms:identifier "{{gmo_id}}" .
  ?gm gmo:GMO_000104 ?gmo .
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  }
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
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
      if ("label" in rows[i]) {
        media.contents.push({
          gm_id: {label: rows[i].gm_id.value,
                  href: "/medium/" + rows[i].gm_id.value},
          name: rows[i].label.value
        });
      } else {
        media.contents.push({
          gm_id: {label: rows[i].gm_id.value,
                  href: "/medium/" + rows[i].gm_id.value},
          name: ""
        });
      }
    }

    media.columns = [];
    media.columns.push({key: "gm_id", label: "GM ID"});
    media.columns.push({key: "name", label: "Name"});
    media.total = count_rows.total.value;
    media.limit = count_rows.limit.value;
    media.offset = count_rows.offset.value;
    return media;
  }
})
```
