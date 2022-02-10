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
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX taxncbi: <http://www.ncbi.nlm.nih.gov/taxonomy/>
PREFIX taxup: <http://purl.uniprot.org/taxonomy/>
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?phylum ?phylum_id ?phylum_label ?limit ?offset (COUNT(?gm) AS ?media)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/gmo/>
FROM <http://growthmedium.org/media/>
WHERE {
  ?taxon_url taxont:scientificName ?name ;
    rdfs:subClassOf+ ?phylum .
  ?phylum taxont:rank taxont:Phylum ;
          dcterms:identifier ?phylum_id ;
          rdfs:label ?phylum_label .
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?taxon_url .
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
