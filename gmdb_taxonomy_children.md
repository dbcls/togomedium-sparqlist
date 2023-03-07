# Children list of a taxon

## Parameters

* `tax_id`
  * default: 1239
  * example: 2, 2157

## Endpoint

http://growthmedium.org/sparql

## `children_list`

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT  DISTINCT ?tax ?name ?rank
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
WHERE {
  VALUES ?search_tax_id { taxid:{{tax_id}} }
  ?search_tax_id rdf:type taxo:Taxon .
  ?tax rdfs:subClassOf ?search_tax_id ;
    taxo:rank ?rank ;
    taxo:scientificName ?name .
  #FILTER(!REGEX(?name, "Candidatus"))
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

