# Get similar growth media by a GM ID

Retrieve growth media similar to the growth media given as an argument.

## Parameters

* `gm_id` GMO ID
  * default: JCM_M25
  * examples: SY46,HM_D00205,NBRC_M5
* `limit` limit
  * default: 10
* `offset` offset
  * default: 1

## Endpoint

http://growthmedium.org/sparql

## `count` count results

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(?gm) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/cluster/200/>
FROM <http://growthmedium.org/media/>
WHERE {
  VALUES (?query_gm ?score) { (<http://purl.jp/bio/10/gm/{{gm_id}}> "100") } .
  ?cluster rdfs:seeAlso ?query_gm ;
           rdfs:seeAlso ?gm .
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?gm_name .
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```


## `result` retrieve GMO component information

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?gm_id ?gm ?gm_name ?score
FROM <http://growthmedium.org/media/cluster/200/>
FROM <http://growthmedium.org/media/>
WHERE {
  VALUES (?query_gm ?score) { (<http://purl.jp/bio/10/gm/{{gm_id}}> "100") } .
  ?cluster rdfs:seeAlso ?query_gm ;
           rdfs:seeAlso ?gm .
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?gm_name .
  }
}
ORDER BY ?gm_id
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
       if (rows[i].gm_name) {
         gms.contents.push({gm_id: {label: rows[i].gm_id.value, href: "/medium/" + rows[i].gm_id.value}, 
                            name: rows[i].gm_name.value,
                            score: rows[i].score.value});
       } else {
         gms.contents.push({gm_id: {label: rows[i].gm_id.value, href: "/medium/" + rows[i].gm_id.value},
                            name: "",
                            score: rows[i].score.value});
       }
    }
    gms.columns = [];
    gms.columns.push({key: "gm_id", label: "GM ID"});
    gms.columns.push({key: "name", label: "Name"});
    gms.columns.push({key: "score", label: "Score"});
    gms.total = count_rows.total.value;
    gms.limit = count_rows.limit.value;
    gms.offset = count_rows.offset.value;
    return gms;
  }
})
```