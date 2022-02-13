# Get growth media by a GMO ID

Retrieve growth media including a component with the given GMO ID.

## Parameters

* `tax_ids` Taxonomy ID (multiple)
  * default: 1148,2303, 1386
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
    return params["tax_ids"].split(",").map((taxid) => {
      return "taxid:" + taxid.trim()
    }).join(" ");
  }
})
```
## `count` count results
```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?medium_id) AS ?total) ?limit ?offset
# TODO: switch ep and graph
FROM <http://localhost:8893/gmo/strain>
FROM <http://localhost:8893/gmo/taxonomy>
FROM <http://localhost:8893/gmo/nbrc>
FROM <http://localhost:8893/gmo/jcm>
FROM <http://localhost:8893/gmo/manual>
WHERE {
  VALUES ?tax_ids { {{tax_values}} }
  ?tax_ids rdf:type ddbj-tax:Taxon .
  ?search_tax  rdfs:subClassOf* ?tax_ids .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_00001 ; #exist media
   rdfs:label ?media_name .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?medium_id ?medium_name
# TODO: switch ep and graph
FROM <http://localhost:8893/gmo/strain>
FROM <http://localhost:8893/gmo/taxonomy>
FROM <http://localhost:8893/gmo/nbrc>
FROM <http://localhost:8893/gmo/jcm>
FROM <http://localhost:8893/gmo/manual>
WHERE {
  VALUES ?tax_ids { {{tax_values}} }
  ?tax_ids rdf:type ddbj-tax:Taxon .
  ?search_tax  rdfs:subClassOf* ?tax_ids .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_00001 ; #exist media
   rdfs:label ?medium_name .
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings;
    return rows.map((row) => {
      let medium_id = row["medium_id"]["value"].split("/").pop();
      return {"gm_id": medium_id, "name": row["medium_name"]["value"]};
    });
  }
})
```