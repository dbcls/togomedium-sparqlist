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

http://growthmedium.org/sparql

## `count` count results

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT ?gm) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
WHERE {
  VALUES ?search_tax { taxid:{{tax_id}} }
  ?search_tax rdf:type taxont:Taxon .
  ?tax rdfs:subClassOf* ?search_tax .
  ?org gmo:GMO_000020 ?tax .
  ?gm gmo:GMO_000114 ?org .
  ?gm dcterms:identifier ?gm_id .
  OPTIONAL {
    ?gm rdfs:label|gmo:GMO_000102 ?label
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```



## `result` retrieve media information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?gm_id ?label
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
WHERE {
  VALUES ?search_tax { taxid:{{tax_id}} }
  ?search_tax rdf:type taxont:Taxon .
  ?tax rdfs:subClassOf* ?search_tax .
  ?org gmo:GMO_000020 ?tax .
  ?gm gmo:GMO_000114 ?org .
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
    const KEY_NAME = "name";
    const columns = [
      {key: KEY_GM_ID, label: "GM ID"},
      {key: KEY_NAME, label: "Name"},
    ];
    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((item) => ({
        [KEY_NAME]: !!item.label ? item.label : "",
        [KEY_GM_ID]: {
          label: item.gm_id,
          href: `/medium/${item.gm_id}`,
        },
      }));

    return {total, offset, contents, columns, limit};
  }
})
```
