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

http://growthmedium.org/sparql

## `count` count results

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT (COUNT(?gm) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/media/20210316>

WHERE {
  ?gm a gmo:GMO_00001 ;
    dcterms:identifier ?gm_id .
  {
    ?gm rdfs:label ?label .
    FILTER(REGEX(?label, "{{keyword}}", "i"))
  } UNION {
    ?gm rdfs:label ?label ;
      gmo:GMO_000114 ?media_strain .
    ?media_strain gmo:strain_id ?strain_id .
    ?strain_id gmo:taxon ?strain_tax .
    ?strain_tax taxont:scientificName ?name .
    FILTER(REGEX(?name, "{{keyword}}", "i"))
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve media

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT DISTINCT ?gm ?gm_id ?label
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/media/20210316>

WHERE {
  ?gm a gmo:GMO_00001 ;
    dcterms:identifier ?gm_id .
  {
    ?gm rdfs:label ?label .
    FILTER(REGEX(?label, "{{keyword}}", "i"))
  } UNION {
    ?gm rdfs:label ?label ;
      gmo:GMO_000114 ?media_strain .
    ?media_strain gmo:strain_id ?strain_id .
    ?strain_id gmo:taxon ?strain_tax .
    ?strain_tax taxont:scientificName ?name .
    FILTER(REGEX(?name, "{{keyword}}", "i"))
  }
}
ORDER BY ?gm
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
        gm_id: {
          label: rows[i].gm_id.value,
          href: "/medium/" + rows[i].gm_id.value,
        },
        name: rows[i].label.value
      });
    }

    contents = gms_with_taxonomy.concat(gms_wo_taxonomy);
    gms.contents = contents;
    gms.columns = [];
    gms.columns.push({key: "gm_id", label: "GM ID"});
    gms.columns.push({key: "name", label: "Name"});
    gms.total = count_rows.total.value ;
    gms.limit = count_rows.limit.value ;
    gms.offset = count_rows.offset.value ;
    return gms;
  }
})
```
