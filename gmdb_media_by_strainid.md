# Get growth media by a Strain ID

List growth media used for strains(s) with the given TogoMedium Strain ID.

## Parameters

* `strain_id` TogoMedium strainID
  * default: S602
  * examples: S38839, S34401, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://togomedium.org/sparql

## `count` count results

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?medium) AS ?total) ?limit ?offset
FROM <http://togomedium.org/media>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
WHERE {
  VALUES ?search_strain_id { "{{strain_id}}" }
  ?strain dcterms:identifier ?search_strain_id ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media information

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?media_id ?original_media_id ?label
FROM <http://togomedium.org/media>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
WHERE {
  VALUES ?search_strain_id { "{{strain_id}}" }
  ?strain dcterms:identifier ?search_strain_id ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 ; #exist media
    rdfs:label ?media_name ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id .
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
    const KEY_NAME = "name";
    const columns = [
      {key: KEY_GM_ID, label: "Medium"},
      {key: KEY_ORGINAL_GM_ID, label: "Information source"},
      {key: KEY_NAME, label: "Name"},
    ];
    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((item) => ({
        [KEY_NAME]: !!item.label ? item.label : "",
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
