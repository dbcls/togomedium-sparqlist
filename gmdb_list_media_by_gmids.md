# List growth media with the given GMIDs (for pagination)

Show a list of growth media with the given GM ID(s).

## Parameters

* `gm_ids` GM ID
  * default: M6,SY46,HM_D00205,NBRC_M5,JCM_M25
  * examples: SY48,HM_D00220,NBRC_M108,JCM_M231
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0


## Endpoint

http://togomedium.org/sparql

## `media_values`
```javascript
({
  json(params) {
    return params["gm_ids"].split(",").map((gmid) => {
      return "\""+ gmid.trim() + "\""
    }).join(" ");
  }
})
```

## `count` count results

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT ?medium_uri) AS ?total) ?limit ?offset
FROM <http://togomedium.org/media>
WHERE {
  VALUES ?medium_no { {{media_values}} }
  ?medium_uri (dcterms:identifier | skos:altLabel) ?medium_no ;
    rdf:type gmo:GMO_000001 ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?media_name .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` list of growth media

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?media_id ?original_media_id ?media_name
FROM <http://togomedium.org/media>
WHERE {
  VALUES ?medium_no { {{media_values}} }
  ?medium_uri (dcterms:identifier | skos:altLabel) ?medium_no ;
    rdf:type gmo:GMO_000001 ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?name .
  BIND (if(STR(?name) = "", "(Unnamed medium)", ?name) AS ?media_name)
}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings;
    let count_rows = count.results.bindings[0];
    let gms = {};
    gms.contents = [];

    gms.total = 0;
    gms.limit = 0;
    gms.offset = 0;

    if (rows.length == 0) {
      return gms;
    }

    for (let i = 0; i < rows.length ;i++) {
      gms.contents.push({
        media_id: {label: rows[i].media_id.value,
                href: "/medium/" + rows[i].media_id.value},
        original_media_id: rows[i].original_media_id.value,
        media_name: rows[i].media_name.value
      });
    }

    gms.columns = [];
    gms.columns.push({key: "media_id", label: "Medium"});
    gms.columns.push({key: "original_media_id", label: "Information source"});
    gms.columns.push({key: "media_name", label: "Name"});
    gms.total = count_rows.total.value;
    gms.limit = count_rows.limit.value;
    gms.offset = count_rows.offset.value;
    return gms;
  }
})
```
