# List growth media components in TogoMedium (for pagination)

Show a list of growth media components.

## Parameters

* `limit` limit
  * default: 20
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `count` count the number of components in TogoMedium

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT
  (COUNT(DISTINCT ?gmo_id) AS ?total) ?limit ?offset
FROM <http://togomedium.org/gmo>
WHERE {
  ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
    dcterms:identifier ?gmo_id ;
    skos:prefLabel ?l .
  OPTIONAL {
    ?gmo skos:altLabel ?alt_label
    FILTER(LANG(?alt_label) = "en")
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve GMO component information

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT
  ?gmo_id
  (?gmo AS ?component)
  (?l AS ?label)
  (GROUP_CONCAT(?alt_label; SEPARATOR = ", ") AS ?alt_labels)
FROM <http://togomedium.org/gmo>
WHERE {
  ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
     dcterms:identifier ?gmo_id ;
     skos:prefLabel ?l .
  OPTIONAL {
    ?gmo skos:altLabel ?alt_label
    FILTER(LANG(?alt_label) = "en")
  }
}
GROUP BY ?gmo_id ?gmo ?l
ORDER BY ?label
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {

    let rows = result.results.bindings;
    let count_rows = count.results.bindings[0];
    let components = {};
    components.contents = [];

    components.total = 0;
    components.limit = 0;
    components.offset = 0;

    if (rows.length == 0) {
      return components;
    }
    for (let i = 0; i < rows.length ;i++) {
      if (rows[i].alt_labels && rows[i].alt_labels.value.length > 0) {
        components.contents.push({
          gmo_id: {label: rows[i].gmo_id.value,
                   href: "/component/" + rows[i].gmo_id.value},
          name: rows[i].label.value + "; " + rows[i].alt_labels.value
        });
      } else {
        components.contents.push({
          gmo_id: {label: rows[i].gmo_id.value,
                   href: "/component/" + rows[i].gmo_id.value},
          name: rows[i].label.value
        });
      }
    }

    components.columns = [];
    components.columns.push({key: "gmo_id", label: "GMO ID"});
    components.columns.push({key: "name", label: "Name"});
    components.total = count_rows.total.value ;
    components.limit = count_rows.limit.value ;
    components.offset = count_rows.offset.value ;
    return components;
  }
})
```
