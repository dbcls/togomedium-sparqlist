# Children list of a taxon

## Parameters

* `tax_id`
  * default: c__Bacilli
  * example: s__Bacillus_CA%20shivajii

## Endpoint

http://togomedium.org/sparql

## `children_list`

```sparql
DEFINE sql:select-option "order"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gtdb: <http://identifiers.org/gtdb/>

SELECT  DISTINCT ?tax ?name ?rank
FROM <http://togohmedium.org/gtdb/filterd_has_strain>
WHERE {
  VALUES ?taxon_type { ddbj-tax:Taxon gtdb:Taxon }
  ?search_gtdb_id dcterms:identifier "{{tax_id}}" ;
    a ?taxon_type .
  ?tax rdfs:subClassOf ?search_gtdb_id ;
    ddbj-tax:rank ?rank ;
    rdfs:label ?name .
}
```

## Output

```javascript
({
  json({children_list}) {
    let list = children_list.results.bindings;
    return list.map((row) => {
      let tax_id = row["tax"]["value"].split("/").pop();
      let rank = row["rank"]["value"].split("/").pop();
      return {"tax_id": tax_id, "name": row["name"]["value"], "rank": rank}
    });
  }
})
```

