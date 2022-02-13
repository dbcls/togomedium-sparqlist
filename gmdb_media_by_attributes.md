# Get growth media by multiple GMO IDs

Retrieve growth media with all the specified GMO IDs.  
If the hierarchical hit contains even one component, `exact-match` will return false

## Parameters

* `gmo_ids` GMO ID
  * default: GMO_001001,GMO_001815
  * examples: GMO_001001, GMO_001815, GMO_001084, ...
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

## `exact_query_text` query params

```javascript
({
  json({gmo_ids}) {
    gmo_id_list = gmo_ids.split(',').map((gmo_id) => { return gmo_id.trim()});
    let identifier_query = "";
    let gmo2medium_query = "";
    gmo_id_list.forEach((gmo_id, idx) => {
      identifier_query += "?gmo_id" + idx + " dcterms:identifier " + "\"" + gmo_id + "\" .\n";
      gmo2medium_query += "?gm olo:slot/olo:item/gmo:has_component/gmo:gmo_id ?gmo_id" + idx + " .\n";
    });
    let query_text = identifier_query + gmo2medium_query
    return query_text;
  }
})
```

## `hieralcal_query_text` query params with subClassOf

```javascript
({
  json({gmo_ids}) {
    gmo_id_list = gmo_ids.split(',').map((gmo_id) => { return gmo_id.trim()});
    let identifier_query = "";
    let subclassof_query = "";
    let gmo2medium_query = "";
    gmo_id_list.forEach((gmo_id, idx) => {
      identifier_query += "?gmo_id" + idx + " dcterms:identifier " + "\"" + gmo_id + "\" .\n";
      subclassof_query += "?gmo_id_desc" + idx + " rdfs:subClassOf* ?gmo_id" + idx + " .\n";
      gmo2medium_query += "?gm olo:slot/olo:item/gmo:has_component/gmo:gmo_id ?gmo_id_desc" + idx + " .\n";
    });
    let query_text = identifier_query + subclassof_query + gmo2medium_query
    return query_text;
  }
})
```

## `count` number of hit media with  hieralcal query

```sparql
DEFINE sql:select-option "order"
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT (COUNT(DISTINCT ?gm) AS ?total) ?limit ?offset
#FROM <http://localhost:8893/gmo/nbrc>
#FROM <http://localhost:8893/gmo/jcm>
#FROM <http://localhost:8893/gmo/manual>
#FROM <http://localhost:8893/gmo>
FROM <http://growthmedium.org/media/20210316>
FROM <http://growthmedium.org/gmo/v0.23>
WHERE {
{{hieralcal_query_text}}
  ?gm rdfs:label ?label .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
LIMIT {{limit}}
OFFSET {{offset}}
```
## `result` retrieve media with  hieralcal query

```sparql
DEFINE sql:select-option "order"
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT DISTINCT ?gm ?label
#FROM <http://localhost:8893/gmo/nbrc>
#FROM <http://localhost:8893/gmo/jcm>
#FROM <http://localhost:8893/gmo/manual>
#FROM <http://localhost:8893/gmo>
FROM <http://growthmedium.org/media/20210316>
FROM <http://growthmedium.org/gmo/v0.23>
WHERE {
{{hieralcal_query_text}}
  ?gm rdfs:label ?label .
}
LIMIT {{limit}}
OFFSET {{offset}}
```
## `exact_result` retrieve media without hieralcal query

```sparql
DEFINE sql:select-option "order"
PREFIX gm: <http://purl.jp/bio/10/gm/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT DISTINCT ?gm
#FROM <http://localhost:8893/gmo/nbrc>
#FROM <http://localhost:8893/gmo/jcm>
#FROM <http://localhost:8893/gmo/manual>
#FROM <http://localhost:8893/gmo>
FROM <http://growthmedium.org/media/20210316>
FROM <http://growthmedium.org/gmo/v0.23>
WHERE {
{{exact_query_text}}
  ?gm rdfs:label ?label .
}
```

## Output

```javascript
({
  json({result, count, exact_result}) {
    let rows = result.results.bindings;
    let exact_rows = exact_result.results.bindings;
    let exact_match_gmo_id =  exact_rows.map((row) => { return row["gm"]["value"].split("/").pop()});
    return rows.map((row) => {
      let gm_id = row["gm"]["value"].split("/").pop();
      // subClassOfを使用せずにヒットした場合はtrue, subClassOf*を使用して階層ヒットした場合はfalse
      if (exact_match_gmo_id.includes(gm_id)) {
        return {"gm_id": gm_id, "name": row["label"]["value"], "exact_match": true};
      } else {
        return {"gm_id": gm_id, "name": row["label"]["value"], "exact_match": false};
      }
    });
  }
})
```