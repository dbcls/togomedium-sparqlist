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
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?phylum ?phylum_id ?phylum_label ?limit ?offset (COUNT(?media_url) AS ?media)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/media/20210316>
WHERE {
  ?media_url gmo:GMO_000114 ?media_strain .
  ?media_strain gmo:strain_id ?strain_id .
  ?strain_id gmo:taxon ?strain_tax .
  ?strain_tax rdfs:subClassOf* ?phylum .
  ?phylum taxont:rank taxont:Phylum ;
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
