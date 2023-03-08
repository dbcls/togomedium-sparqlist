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
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT (COUNT(DISTINCT ?medium) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
WHERE {
  ?gmo dcterms:identifier "{{gmo_id}}" .
  ?medium olo:slot/olo:item/gmo:has_component/gmo:gmo_id ?gmo .
  ?medium dcterms:identifier ?media_id ;
    skos:altLabel ?orignal_media_id ;
    rdfs:label ?label .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT DISTINCT ?media_id ?label ?original_media_id
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
WHERE {
  ?gmo dcterms:identifier "{{gmo_id}}" .
  ?medium olo:slot/olo:item/gmo:has_component/gmo:gmo_id ?gmo .
  ?medium dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?media_name .
  BIND (if(STR(?media_name) = "", "(Unnamed medium)", ?media_name) AS ?label)

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
      media.contents.push({
        media_id: {label: rows[i].media_id.value,
                href: "/medium/" + rows[i].media_id.value},
        original_media_id: rows[i].original_media_id.value,
        name: rows[i].label.value
      });
    }

    media.columns = [];
    media.columns.push({key: "media_id", label: "GM ID"});
    media.columns.push({key: "name", label: "Name"});
    media.total = count_rows.total.value;
    media.limit = count_rows.limit.value;
    media.offset = count_rows.offset.value;
    return media;
  }
})
```
