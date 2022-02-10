# List taxons by a taxonomy rank



## Parameters

* `tax_id`
  * default: 1239
  * example: 2, 2157
* `rank` 
  * default: Class
  * examples: Phylum, Order, Family, Genus, Species

## Endpoint

http://growthmedium.org/sparql

## `result`

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT  DISTINCT ?tax ?name
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
#FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
#FROM <http://growthmedium.org/gmo/>
WHERE {
  VALUES ?search_tax_id { taxid:{{tax_id}} }
  ?search_tax_id rdf:type taxo:Taxon .
  ?tax rdfs:subClassOf* ?search_tax_id .
  ?tax taxo:rank taxo:{{rank}} .
  ?medium_tax rdfs:subClassOf* ?tax .  
  ?org gmo:GMO_000020 ?medium_tax .
  ?gm gmo:GMO_000114 ?org .
  ?tax taxo:scientificName ?name .
  FILTER(!REGEX(?name, "Candidatus"))
} LIMIT 9999
```

## Output

```javascript
({
  json({result}) {
    let rows = result.results.bindings ;
    let taxonomies = [] ;
    
    for (let i = 0; i < rows.length ;i++) {
      if (!rows[i].name.value.match(/candidate/)) {
      taxonomies.push({
        id: rows[i].tax.value,
        name: rows[i].name.value
      });
      }
    }
    return taxonomies ;
  }
})
```


