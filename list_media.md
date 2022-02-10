# List growth media (for pagination)

Show a list of growth media in TogoMedium.

## Parameters

* `limit` limit
  * default: 20
* `offset` offset
  * default: 0


## Endpoint

http://growthmedium.org/sparql

## `count` count total number of growth media

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT ?gm_id) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  ?gm a gmo:GMO_000001 ;
      dcterms:identifier ?gm_id
  OPTIONAL {
     ?gm rdfs:label|gmo:GMO_000102 ?label
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

SELECT DISTINCT *
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  ?gm a gmo:GMO_000001 ;
      dcterms:identifier ?gm_id
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
    
    const KEY_GM_ID = "gm_id";
    const KEY_Label= "label";
    const columns = [
      {key: KEY_GM_ID, label: "GM ID"},
      {key: KEY_Label, label: "Name"},
    ];

    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((item) => ({
        [KEY_Label]: !!item.label ? item.label : "",
        [KEY_GM_ID]: {
          label: item.gm_id,
          href: `/medium/${item.gm_id}`,
        },
      }));
    return {total, offset, contents, columns, limit};
  }
})
```
