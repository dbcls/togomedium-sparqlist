# Get phenotypes by a strain ID

## Parameters

* `strain_id` TogoMedium Strain ID
  * default: 000000001
* `limit` limit
  * default: 10
* `offset` offset
  * default: 1
 
 ## Endpoint

http://growthmedium.org/sparql

## `count` count results
```sparql
prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
prefix dcterms: <http://purl.org/dc/terms/>
prefix sio: <http://semanticscience.org/resource/>
prefix prov:    <http://www.w3.org/ns/prov#>
prefix mpo: <http://purl.jp/bio/10/mpo#>

SELECT (COUNT(?phenotype) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/mpo/v0.74>
{
  <http://togomedium.org/strain/{{strain_id}}>  sio:SIO_001279 ?phenotype .
  ?phenotype rdf:type prov:Entity ;
    prov:hadPrimarySource ?source_uri ;
    rdfs:label ?source_label ;
    ?phenotype_property ?phenotype_value .
  GRAPH <http://growthmedium.org/mpo/v0.74>
  {
     ?phenotype_property rdf:type ?property_type ;
       rdfs:label ?property_label .
     FILTER (lang(?property_label) = 'en')
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media information

```sparql
prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
prefix dcterms: <http://purl.org/dc/terms/>
prefix sio: <http://semanticscience.org/resource/>
prefix prov:    <http://www.w3.org/ns/prov#>
prefix mpo: <http://purl.jp/bio/10/mpo#>

SELECT DISTINCT ?source_uri ?source_label
  ?phenotype_property ?property_type ?property_label 
  ?phenotype_value ?value_type ?value_label
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/mpo/v0.74>
WHERE {
  <http://togomedium.org/strain/{{strain_id}}>  sio:SIO_001279 ?phenotype .
  ?phenotype rdf:type prov:Entity ;
    prov:hadPrimarySource ?source_uri ;
    rdfs:label ?source_label ;
    ?phenotype_property ?phenotype_value .
  GRAPH <http://growthmedium.org/mpo/v0.74>
  {
     ?phenotype_property rdf:type ?property_type ;
       rdfs:label ?property_label .
     FILTER (lang(?property_label) = 'en')
  }
  OPTIONAL {
    GRAPH <http://growthmedium.org/mpo/v0.74>
    {
      ?phenotype_value rdf:type ?value_type ;
        rdfs:label ?value_label .
      FILTER (lang(?value_label) = 'en')
    }
  }
} ORDER BY ?phenotype_property ?source_uri ?phenotype_value
```
## Output

```javascript
({
  json({result, count}) {
     let header =   [{key: "source", label: "Source"}, {key: "property", label: ""}, {key: "value", label: "Phenotype"} ];
     if (result.results.bindings.length == 0) {
       return {"total": 0, "limit": 0, "offset": 0, "contents": [], "columns": headers};
     }
     let count_rows = count.results.bindings[0] ;
     let ret = {
       "total": count_rows.total.value,
       "limit":  count_rows.limit.value,
       "offset": count_rows.offset.value,
       "columns": header
    }
    ret["contents"] = result.results.bindings.map((item) => {
      let phenotype_data = { "source": { "label": item.source_label.value, "href":  item.source_uri.value}, "property": item.property_label.value }
      if (item.value_type) {
        phenotype_data["value"] = item.value_label.value;
      } else {
        phenotype_data["value"] = item.phenotype_value.value;
      }
      return phenotype_data;
    });
     return ret;
  }
})
```