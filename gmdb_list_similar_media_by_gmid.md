# Get similar growth media by a GM ID

Retrieve growth media similar to the growth media given as an argument.

## Parameters

* `gm_id` GMO ID
  * default: M18
  * examples: JCM_M25
* `limit` limit
  * default: 10
* `offset` offset
  * default: 1

## Endpoint

http://togomedium.org/sparql

## `count` count results

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX gmo:     <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(?media_original_name) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/similarity>
{
  VALUES ?medium_no { "{{gm_id}}" }
  ?search_media (dcterms:identifier | skos:altLabel) ?medium_no .
  ?blank gmo:GMO_000115 ?search_media ;
    gmo:GMO_000115 ?media ;
    rdf:value ?score .
  FILTER (?search_media != ?media )
  ?media skos:altLabel ?media_original_name ;
    rdfs:label ?media_name .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```


## `result` retrieve GMO component information

```sparql
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX gmo:     <http://purl.jp/bio/10/gmo/>

SELECT ?media
 (?medium_id AS ?gm_id)
 (?media_name AS ?gm_name)
 ?score
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/similarity>
{
  VALUES ?medium_no { "{{gm_id}}" }
  ?search_media (dcterms:identifier | skos:altLabel) ?medium_no .
  ?blank gmo:GMO_000115 ?search_media ;
    gmo:GMO_000115 ?media ;
    rdf:value ?score .
  FILTER (?search_media != ?media )
  ?media skos:altLabel ?media_original_name ;
    dcterms:identifier ?medium_id ;
    rdfs:label ?name .
  BIND (if(STR(?name) = "", "(Unnamed medium)", ?name) AS ?media_name)
} ORDER BY DESC(?score)
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings ;
    let count_rows = count.results.bindings[0] ;
    let gms = {} ;
    gms.contents = [];

    gms.total = 0;
    gms.limit = 0;
    gms.offset = 0;

    if (rows.length == 0) {
      return gms;
    }

    for (let i = 0; i < rows.length; i++) {
        gms.contents.push({gm_id: {label: rows[i].gm_id.value, href: "/medium/" + rows[i].gm_id.value},
                name: rows[i].gm_name.value,
                score: (Math.round(parseFloat(rows[i].score.value) * 1000))/10});
    }
    gms.columns = [];
    gms.columns.push({key: "gm_id", label: "Medium"});
    gms.columns.push({key: "name", label: "Name"});
    gms.columns.push({key: "score", label: "Score"});
    gms.total = count_rows.total.value;
    gms.limit = count_rows.limit.value;
    gms.offset = count_rows.offset.value;
    return gms;
  }
})
```