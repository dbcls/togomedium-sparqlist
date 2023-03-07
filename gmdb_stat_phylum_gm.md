# Statistics number of gm by phylum

Get statistics of the number of growth medium by phylum

## Parameters

* `limit` limit
  * default: 1000
* `offset` offset
  * default: 1

## Endpoint

http://growthmedium.org/sparql

## `result` retrieve media information

```sparql
DEFINE sql:select-option "order"
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT ?phylum ?phylum_id ?phylum_label ?limit ?offset (COUNT(DISTINCT ?medium_uri) AS ?media)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/media/2023>
{
  ?medium_uri gmo:GMO_000114 ?culture_for ;
     rdf:type gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain gmo:taxon ?taxon_url ;
    rdf:type sio:SIO_010055 .
  ?taxon_url ddbj-tax:scientificName ?name ;
    rdfs:subClassOf+ ?phylum .
  ?phylum ddbj-tax:rank ddbj-tax:Phylum ;
          dcterms:identifier ?phylum_id ;
          rdfs:label ?phylum_label .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
GROUP BY ?phylum ?phylum_id ?phylum_label ?limit ?offset
ORDER BY DESC(?media)
```

## Output

```javascript
({
  json({result}) {
    let rows = result.results.bindings ;
    let results = {} ;
    results.contents = [];

    for (let i = 0; i < rows.length; i++) {
      results.contents.push({"phylum": {label: rows[i].phylum_label.value,
                                        href: "/taxon/" + rows[i].phylum_id.value},
                            "gms": rows[i].media.value});
    }

    results.columns = [];
    results.columns.push({key: "phylum", label: "Phylum"});
    results.columns.push({key: "gms", label: "The number of growth media"});
    results.total = rows.length ;
    results.limit = rows[0].limit.value ;
    results.offset = rows[0].offset.value ;

    return results ;
  }
})
```
