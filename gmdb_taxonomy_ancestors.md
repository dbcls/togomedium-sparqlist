# Ancestors list of a taxon

## Parameters

* `tax_id`
  * default: 498845
  * example: 2161, 403219

## Endpoint

http://togomedium.org/sparql

## `ancestors_list`

```sparql
DEFINE sql:select-option "order"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT  DISTINCT ?tax ?name ?rank ?depth
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
WHERE {
  {
    SELECT DISTINCT ?tax COUNT(?ancestor_tax_id) AS ?depth
    {
      VALUES ?search_tax_id { taxid:{{tax_id}} }
      ?search_tax_id rdf:type taxo:Taxon ;
        rdfs:subClassOf* ?tax .
      ?tax rdfs:subClassOf* ?ancestor_tax_id .
    } GROUP BY ?tax
  }
  ?tax taxo:rank ?rank ;
    taxo:scientificName ?name .
  FILTER (?tax != taxid:1 && ?tax != taxid:131567)
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