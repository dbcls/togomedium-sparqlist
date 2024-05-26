# Get growth medium by a growth medium ID

Retrieve a growth medium with the given growth medium ID.

## Parameters

* `gm_id` Growth medium ID
  * default: NBRC_M249
  * examples: JCM_M1, NBRC_M1039, SY1, HM_D00088_mse, ...

## Endpoint

http://togomedium.org/sparql

## `metadata` retrieve medium metadata

```sparql
prefix gmo:     <http://purl.jp/bio/10/gmo/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 

SELECT ?gm ?name ?src_url ?ph
FROM <http://growthmedium.org/media/20210316>
FROM <http://togomedium.org/gmo>
{
  VALUES ?gm_no { "{{gm_id}}" }
  ?gm dcterms:identifier ?gm_no ;
    rdfs:label ?name ;
    gmo:GMO_000108 ?src_url .
  OPTIONAL { ?gm gmo:ph ?ph }
}
```
## `component_table`retrieve medium component table paragraph

```sparql
DEFINE sql:select-option "order"
prefix gm:     <http://togomedium.org/>
prefix gmo:     <http://purl.jp/bio/10/gmo/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
prefix xsd:     <http://www.w3.org/2001/XMLSchema#>
prefix olo:     <http://purl.org/ontology/olo/core#>
prefix sio:     <http://semanticscience.org/resource/>

SELECT ?paragraph_index ?subcomponent_name ?component_name ?volume ?unit ?conc_value ?conc_unit ?gmo ?gmo_id ?label ?property_id ?property ?property_label ?role_id ?role ?role_label
FROM <http://growthmedium.org/media/20210316>
FROM <http://togomedium.org/gmo>
FROM <http://growthmedium.org/uo>
{
  VALUES ?medium_no { "{{gm_id}}" }
  ?medium dcterms:identifier ?medium_no ;
    olo:slot ?slot.
  ?slot olo:index ?paragraph_index ;
   olo:item ?component_table .
  ?component_table rdf:type gmo:Component .
  OPTIONAL { ?component_table rdfs:label ?subcomponent_name }
  ?component_table gmo:has_component ?component .
  ?component rdfs:label ?component_name .
  OPTIONAL  {
    ?component sio:SIO_000216/sio:SIO_000300 ?volume ;
      sio:SIO_000216/sio:SIO_000221 ?unit_class .
      ?unit_class <oboInOwl:hasExactSynonym> ?unit .
  }
  OPTIONAL  {
    ?component gmo:has-concentration-value/sio:SIO_000300 ?conc_value ;
      gmo:has-concentration-value/sio:SIO_000221 ?conc_unit_class .
      ?conc_unit_class <oboInOwl:hasExactSynonym> ?conc_unit .
  }
  OPTIONAL  {
    ?component gmo:gmo_id ?gmo .
      ?gmo rdfs:label ?label ;
      dcterms:identifier ?gmo_id .
     FILTER (lang(?label) = "en")
    OPTIONAL {
      ?gmo gmo:GMO_000113 ?property .
      ?property rdfs:label ?property_label .
      ?property dcterms:identifier ?property_id
    }
    OPTIONAL {
      ?gmo gmo:GMO_000112 ?role .
      ?role rdfs:label ?role_label .
      ?role dcterms:identifier ?role_id
      FILTER(LANG(?role_label) = "en")
    }
  }
} ORDER BY ?paragraph_index
```

## `comment_list` retrieve medium comment paragraph
```sparql
DEFINE sql:select-option "order"
prefix gmo:     <http://purl.jp/bio/10/gmo/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
prefix olo:     <http://purl.org/ontology/olo/core#>

SELECT ?paragraph_index ?comment
FROM <http://growthmedium.org/media/20210316>
FROM <http://togomedium.org/gmo>
{
  VALUES ?medium_no {  "{{gm_id}}" }
  ?medium dcterms:identifier ?medium_no ;
    olo:slot ?slot.
  ?slot olo:index ?paragraph_index ;
   olo:item ?paragraph .
  ?paragraph rdf:type gmo:Comment; 
    rdfs:comment ?comment .
} ORDER BY ?paragraph_index
```

## Output
```javascript
({
  json({metadata, component_table, comment_list}) {
    
    return {metadata, component_table, comment_list};    
  }
})
```