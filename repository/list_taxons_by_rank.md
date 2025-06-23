# List taxons by a taxonomy rank



## Parameters

* `tax_id`
  * default: 1239
  * example: 2, 2157
* `rank`
  * default: Class
  * examples: Phylum, Order, Family, Genus, Species

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `result`

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>


SELECT  DISTINCT ?tax ?name
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
FROM <http://togomedium.org/media>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
WHERE {
  VALUES ?search_tax_id { taxid:{{tax_id}} }
  ?search_tax_id rdf:type ddbj-tax:Taxon .
  ?tax rdfs:subClassOf* ?search_tax_id .
  ?tax ddbj-tax:rank ddbj-tax:{{rank}} .
  ?medium_tax rdfs:subClassOf* ?tax .
  ?strain gmo:taxon ?medium_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?tax ddbj-tax:scientificName ?name .
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


