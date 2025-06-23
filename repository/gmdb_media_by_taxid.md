# Get growth media by a tax ID

List growth media used for organism(s) with the given NCBI taxonomy ID.

## Parameters

* `tax_id` NCBI taxID
  * default: 203404
  * examples: 410359, 266117, 1209989, 543526, 315405, 1409, 1931, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `count` count results

```sparql
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT ?medium) AS ?total) ?limit ?offset
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
  VALUES ?search_tax { taxid:{{tax_id}} }
  ?search_tax rdf:type ddbj-tax:Taxon .
  ?tax rdfs:subClassOf* ?search_tax .
  ?strain gmo:taxon ?tax .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 ; #exist media
    rdfs:label ?label ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```



## `result` retrieve media information

```sparql
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?media_id ?original_media_id ?label
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
  VALUES ?search_tax { taxid:{{tax_id}} }
  ?search_tax rdf:type ddbj-tax:Taxon .
  ?tax rdfs:subClassOf* ?search_tax .
  ?strain gmo:taxon ?tax .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 ; #exist media
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
