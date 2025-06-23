# Get growth media by GTDB taxon IDs

Retrieve growth media including a component with the given GMO ID.

## Parameters

* `tax_ids` Taxonomy ID (multiple)
  * default: c__Cyanobacteriia, s__Thermoplasma%20acidophilum, g__Bacillus
  * example: g__Bacillus, GB_GCA_022733635.1, "RS_GCF_000722875.1
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `tax_values`
```javascript
({
  json(params) {
    let tax_values = "";
    return params["tax_ids"].split(",").map((taxid) => {
      return "\"" + taxid.trim() + "\""
    }).join(" ");
  }
})
```
## `count` count results
```sparql
DEFINE sql:select-option "order"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX gtdb: <http://identifiers.org/gtdb/>

SELECT (COUNT(DISTINCT ?medium_id) AS ?total) ?limit ?offset
FROM <http://togomedium.org/gtdb/filtered_has_strain>
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
WHERE {
 {
  SELECT DISTINCT ?ncbi_tax_id
  FROM <http://togomedium.org/gtdb/filtered_has_strain>
  {
    VALUES ?taxon_type { ddbj-tax:Taxon gtdb:Taxon }
    VALUES ?tax_ids { {{tax_values}} }
    ?search_gtdb_id dcterms:identifier ?tax_ids ;
      a ?taxon_type .
    ?gtdb_id rdfs:subClassOf* ?search_gtdb_id ;
     rdfs:seeAlso ?ncbi_tax_id .
  }
}
  ?ncbi_tax_id rdf:type ddbj-tax:Taxon .
  ?search_tax rdfs:subClassOf* ?ncbi_tax_id .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 ; #exist media
    rdfs:label ?name ;
    skos:altLabel ?original_media_id .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media

```sparql
DEFINE sql:select-option "order"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX gtdb: <http://identifiers.org/gtdb/>

SELECT DISTINCT ?medium_id ?medium_name ?original_media_id
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/gtdb/filtered_has_strain>
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
WHERE {
 {
  SELECT DISTINCT ?ncbi_tax_id
  FROM <http://togomedium.org/gtdb/filtered_has_strain>
  {
    VALUES ?taxon_type { ddbj-tax:Taxon gtdb:Taxon }
    VALUES ?tax_ids { {{tax_values}} }
    ?search_gtdb_id dcterms:identifier ?tax_ids ;
      a ?taxon_type .
    ?gtdb_id rdfs:subClassOf* ?search_gtdb_id ;
     rdfs:seeAlso ?ncbi_tax_id .
  }
}
  ?ncbi_tax_id rdf:type ddbj-tax:Taxon .
  ?search_tax rdfs:subClassOf* ?ncbi_tax_id .
  ?strain gmo:taxon ?search_tax ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 ; #exist media
    rdfs:label ?name ;
    skos:altLabel ?original_media_id .
  BIND (if(STR(?name) = "", "(Unnamed medium)", ?name) AS ?medium_name)
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    let count_result = count.results.bindings[0];
    let total = count_result ? parseInt(count_result["total"]["value"]) : 0;
    let offset = count_result ? parseInt(count_result["offset"]["value"]) : 0;
    let limit = count_result ? parseInt(count_result["limit"]["value"]) : 0;

    let rows = result.results.bindings;
    let contents = rows.map((row) => {
      let medium_id = row["medium_id"]["value"].split("/").pop();
      return {"gm_id": medium_id, "name": row["medium_name"]["value"], "original_media_id": row["original_media_id"]["value"]};
    });
    return {"total": total, "offset": offset, "limit": limit, "contents": contents};
  }
})
```
