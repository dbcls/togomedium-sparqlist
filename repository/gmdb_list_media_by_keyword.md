# List growth media with the given keyword (for pagination)

Show a list of growth media with the given keyword.

## Parameters

* `keyword` keyword
  * default: MRS medium
  * examples: Methanogenium, YM ager, Bacto
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `count` count results

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?medium_uri) AS ?total) ?limit ?offset
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/gmo>
WHERE {
  ?medium_uri a gmo:GMO_000001 ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id .
  {
    ?medium_uri rdfs:label ?label
    FILTER(REGEX(?label, "{{keyword}}", "i"))
  } UNION {
    ?medium_uri gmo:GMO_000114 ?culture_for ;
     rdf:type gmo:GMO_000001 . #exist media
    ?culture_for gmo:strain_id ?strain .
    ?strain gmo:taxon ?taxon_url ;
      rdf:type sio:SIO_010055 .
    ?taxon_url ddbj-tax:scientificName ?name .
    FILTER(REGEX(?name, "{{keyword}}", "i"))
  }
  OPTIONAL { ?medium_uri gmo:GMO_000108 ?src_url }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?medium_uri ?media_id ?original_media_id
  (GROUP_CONCAT(?label; SEPARATOR = ", ") AS ?label)
  (GROUP_CONCAT(DISTINCT ?tax_name; SEPARATOR = ", ") AS ?organism_names)
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/gmo>
WHERE {
  ?medium_uri a gmo:GMO_000001 ;
    dcterms:identifier ?media_id ;
    skos:altLabel ?original_media_id .
  {
    ?medium_uri rdfs:label ?label .
    FILTER(REGEX(?label, "{{keyword}}", "i"))
  } UNION {
    ?medium_uri gmo:GMO_000114 ?culture_for ;
     rdf:type gmo:GMO_000001 . #exist media
    ?culture_for gmo:strain_id ?strain .
    ?strain gmo:taxon ?taxon_url ;
      rdf:type sio:SIO_010055 .
    ?taxon_url ddbj-tax:scientificName ?tax_name .
    FILTER(REGEX(?tax_name, "{{keyword}}", "i"))
  }
  OPTIONAL { ?medium_uri gmo:GMO_000108 ?src_url }
}
GROUP BY ?medium_uri ?media_id ?original_media_id
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {

    let count_rows = count.results.bindings[0] ;
    let rows = result.results.bindings ;
    let gms_with_taxonomy = [] ;
    let gms_wo_taxonomy = [] ;
    let contents = [];
    let columns = [];
    let gms = {};

    gms.total = 0;
    gms.limit = 0;
    gms.offset = 0;

    if (rows.length == 0) {
      gms.contents = [];
      return gms;
    }

    for (let i = 0; i < rows.length ;i++) {
      gms_with_taxonomy.push({
        media_id: {
          label: rows[i].media_id.value,
          href: "/medium/" + rows[i].media_id.value,
        },
        name: rows[i].label.value,
        organism_names: rows[i].organism_names.value
      });
    }

    contents = gms_with_taxonomy.concat(gms_wo_taxonomy);
    gms.contents = contents;
    gms.columns = [];
    gms.columns.push({key: "media_id", label: "Medium"});
    gms.columns.push({key: "name", label: "Name"});
    gms.columns.push({key: "organism_names", label: "Organism names"});
    gms.total = count_rows.total.value ;
    gms.limit = count_rows.limit.value ;
    gms.offset = count_rows.offset.value ;
    return gms;
  }
})
```
