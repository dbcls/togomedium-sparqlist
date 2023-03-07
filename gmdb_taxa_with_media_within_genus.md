# Get taxa with media within genus

Retrieve tax_ids with media within genus.

## Parameters

* `tax_ids` Taxonomy ID (multiple)
  * default: 77580,28024,2771,38275,2

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

SELECT DISTINCT ?tax_ids COUNT(?medium_id) AS ?media_count
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/media/2023>
WHERE {
  {
    SELECT ?tax_ids
    {
      VALUES ?tax_ids { {{tax_values}}   }
      ?tax_ids a ddbj-tax:Taxon ;
         rdfs:subClassOf* ?ancestors .
       ?ancestors ddbj-tax:rank ?rank.
       FILTER  (?rank = ddbj-tax:Genus || ?rank = ddbj-tax:Species)
     }
  }
  ?tax_ids rdf:type ddbj-tax:Taxon .
  ?search_tax  rdfs:subClassOf* ?tax_ids .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 ; #exist media
   rdfs:label ?medium_name .
} GROUP BY ?tax_ids
```

## Output

```javascript
({
  json({result}) {
	return result.results.bindings.map((item) => item.tax_ids.value.split("/").pop());
  }
})
```