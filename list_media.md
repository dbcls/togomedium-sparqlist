# List growth media (for pagination)

Show a list of growth media in TogoMedium.

## Parameters

* `limit` limit
  * default: 20
* `offset` offset
  * default: 0


## Endpoint

http://togomedium.org/sparql

## `count` count total number of growth media

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?medium_uri) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/2023>
WHERE {
  ?medium_uri a gmo:GMO_000001 ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?label .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve GMO component information

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?media_id ?original_media_id ?label ?source_uri
FROM <http://growthmedium.org/media/2023>
WHERE {
  ?medium_uri a gmo:GMO_000001 ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?media_name .
  OPTIONAL {
    ?medium_uri gmo:GMO_000108 ?source_uri .
  }
  BIND (if(STR(?media_name) = "", "(Unnamed medium)", ?media_name) AS ?label)
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    const parseSparqlObject = (obj) => {
      const result = {};
      try {
        Object.entries(obj).forEach(([key, item]) => {
          result[key] = item["value"];
        });
      } catch (e) {
      }
      return Object.entries(result).length ? result : null;
    };

    const info = parseSparqlObject(count.results.bindings[0]);
    const total = !!info ? parseInt(info.total) : 0;
    const offset = !!info ? parseInt(info.offset) : 0;
    const limit = !!info ? parseInt(info.limit) : 0;

    const KEY_GM_ID = "media_id";
    const KEY_ORGINAL_GM_ID = "original_media_id";
    const KEY_Label= "label";
    const columns = [
      {key: KEY_GM_ID, label: "Medium"},
      {key: KEY_ORGINAL_GM_ID, label: "Information source"},
      {key: KEY_Label, label: "Name"},
    ];

    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((item) => ({
        [KEY_Label]: !!item.label ? item.label : "",
        [KEY_ORGINAL_GM_ID]: item.original_media_id,
        [KEY_GM_ID]: {
          label: item.media_id,
          href: `/medium/${item.media_id}`,
        },
      }));
    return {total, offset, contents, columns, limit};
  }
})
```
