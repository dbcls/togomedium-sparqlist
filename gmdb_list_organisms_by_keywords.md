# List organisms with the given keyword

Show a list of organisms with the given keyword.

## Parameters

* `keyword` keyword
  * default: Fructobacillus
  * examples: DSM 20438, Tolypocladium cylindrosporum
* `limit` limit
  * default: 10
* `offset` offset
  * default: 1

## Endpoint

http://growthmedium.org/sparql


## `count` count results

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT
  (COUNT(DISTINCT(?tax_id) AS ?total)) ?offset ?limit
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>
WHERE {
  ?t a taxo:Taxon ;
    taxo:rank ?r ;
    dcterms:identifier ?tax_id ;
    taxo:scientificName ?l .
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  ?r rdfs:label ?r_label
  FILTER(REGEX(?l, "{{keyword}}", "i"))
  OPTIONAL {
    ?t taxo:authority ?auth
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
GROUP BY ?tax_id
```

## Output

```javascript
({
  json({result}) {
    let rows = result.results.bindings ;
    let taxonomies = [] ;
    
    for (let i = 0; i < rows.length ;i++) {
      taxonomies.push({
        tax_id: rows[i].tax_id.value,
        taxonomy: rows[i].taxonomy.value,
        label: rows[i].label.value,
        authority_name: rows[i].authority.value
      });
    }
    return taxonomies;
  }
})
```
