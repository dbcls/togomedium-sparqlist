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

## `tax_values`
```javascript
({
  json(params) {
    let tax_values = "";
    return params["tax_id"].split(",").map((taxid) => {
      return "taxid:" + taxid.trim()
    }).join(" ");
  }
})
```

## `count` count results

```sparql
#DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>


SELECT (COUNT(DISTINCT ?medium) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/media/20210316>
WHERE {
  VALUES ?tax_ids { {{tax_values}} }
  ?tax_ids rdf:type ddbj-tax:Taxon .
  ?search_tax rdfs:subClassOf* ?tax_ids .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    dcterms:identifier ?medium_id ;
    rdf:type gmo:GMO_00001 ; #exist media
   rdfs:label ?media_name .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```



## `result` retrieve media information

```sparql
#DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT DISTINCT (?medium_id AS ?gm_id) (?media_name AS ?label)
FROM <http://growthmedium.org/strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/media/20210316>
WHERE {
  VALUES ?tax_ids { {{tax_values}} }
  ?tax_ids rdf:type ddbj-tax:Taxon .
  ?search_tax  rdfs:subClassOf* ?tax_ids .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    dcterms:identifier ?medium_id ;
    rdf:type gmo:GMO_00001 ; #exist media
   rdfs:label ?media_name .
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
