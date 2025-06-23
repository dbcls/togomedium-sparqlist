# Ancestors list of a taxon

## Parameters

* `tax_id`
  * default: c__Bacilli
  * example: s__Bacillus_CA%20shivajii

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `ancestors_list`

```sparql
DEFINE sql:select-option "order"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gtdb: <http://identifiers.org/gtdb/>

SELECT  DISTINCT ?tax ?name ?rank ?depth
FROM <http://togomedium.org/gtdb/filtered_has_strain>
WHERE {
  {
    SELECT DISTINCT ?tax COUNT(?ancestor_tax_id) AS ?depth
    {
      VALUES ?taxon_type { ddbj-tax:Taxon gtdb:Taxon }
      ?search_gtdb_id dcterms:identifier "{{tax_id}}" ;
        a ?taxon_type ;
        rdfs:subClassOf* ?tax .
      ?tax rdfs:subClassOf* ?ancestor_tax_id .
    } GROUP BY ?tax
  }
  ?tax ddbj-tax:rank ?rank ;
    rdfs:label ?name .
} ORDER BY ?depth
```

## Output

```javascript
({
  json({ancestors_list}) {
    let list = ancestors_list.results.bindings;
    return list.map((row) => {
      let tax_id = row["tax"]["value"].split("/").pop();
      let rank = row["rank"]["value"].split("/").pop();
      return {"tax_id": tax_id, "name": row["name"]["value"], "rank": rank}
    });
  }
})
```