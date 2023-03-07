# List growth media components name in TogoMedium
Show all list of growth media component names.

## Endpoint

http://growthmedium.org/sparql

## `all_component_list` retrieve GMO component information

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?gmo_uri ?gmo_id  ?label
FROM <http://growthmedium.org/gmo/v0.24>
WHERE {
  ?gmo_uri rdfs:subClassOf+ gmo:GMO_000002 ;
     dcterms:identifier ?gmo_id ;
     rdfs:label ?label .
  FILTER (lang(?label) = 'en')
  FILTER (strStarts(str(?gmo_id), "GMO_"))
}
ORDER BY ?label
```

## Output

```javascript
({
  json({all_component_list}) {
    let list = all_component_list.results.bindings;
    return list.map((row) => { return {"gmo_id": row["gmo_id"]["value"], "name": row["label"]["value"]}});
  }
})
```