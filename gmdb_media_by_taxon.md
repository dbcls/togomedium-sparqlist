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
FROM <http://growthmedium.org/strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://growthmedium.org/media/20210316>
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
FROM <http://growthmedium.org/strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://growthmedium.org/media/20210316>
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
    let count_result = count.results.bindings[0];
    let total = count_result ? parseInt(count_result["total"]["value"]) : 0;
    let offset = count_result ? parseInt(count_result["offset"]["value"]) : 0;
    let limit = count_result ? parseInt(count_result["limit"]["value"]) : 0;

    let rows = result.results.bindings;
    let contents = rows.map((row) => {
      let medium_id = row["medium_id"]["value"].split("/").pop();
      return {"gm_id": medium_id, "name": row["medium_name"]["value"]};
    });
    return {"total": total, "offset": offset, "limit": limit, "contents": contents};
  }
})
```