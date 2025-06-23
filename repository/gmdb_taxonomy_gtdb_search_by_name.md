# Taxon search by name
Searches species names using incremental prefix matching.

## Parameters

* `q`
  * example: "Nocardioides", "nocardioi", "Bacil"
* `max`
  * default: 100

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `search_result`

```sparql
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gtdb: <http://identifiers.org/gtdb/>

SELECT DISTINCT ?tax_id ?scientific_name ?rank 
FROM <http://togomedium.org/gtdb/filtered_has_strain>
WHERE {
  VALUES ?taxon_type { ddbj-tax:Taxon gtdb:Taxon }
  VALUES ?label { rdfs:label skos:altLabel }
  ?tax_id a ?taxon_type ;
    ?label ?scientific_name .
  ?scientific_name bif:contains '"{{q}}*"' .
  ?tax_id ddbj-tax:rank ?rank .
} ORDER BY ?scientific_name LIMIT {{max}}
```

## Output

```javascript
({
  json({search_result}) {
    let list = search_result.results.bindings;
    return list.map((row) => {
      let tax_id = row["tax_id"]["value"].split("/").pop();
      let rank = row["rank"]["value"].split("/").pop();
      return {"tax_id": tax_id, "name": row["scientific_name"]["value"], "rank": rank}
    });
  }
})
```