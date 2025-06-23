
# List organisms with the given keyword (for pagination)

Show a list of organisms with the given keyword.

## Parameters

* `keyword` keyword
  * default: Streptococcus
  * examples: DSM 20438, Tolypocladium cylindrosporum
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `count` count results

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT
  (COUNT(DISTINCT ?tax_id) AS ?total) ?offset ?limit
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
  ?t a ddbj-tax:Taxon ;
     dcterms:identifier ?tax_id ;
     ddbj-tax:scientificName ?l .
  FILTER(REGEX(?l, "{{keyword}}", "i"))
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve organisms information

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT ?tax_id ?t ?l
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
  ?t a ddbj-tax:Taxon ;
     dcterms:identifier ?tax_id ;
     ddbj-tax:scientificName ?l .
  FILTER(REGEX(?l, "{{keyword}}", "i"))
  FILTER(isNumeric(?tax_id) = true)
}
GROUP BY ?tax_id
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings ;
    let count_rows = count.results.bindings[0] ;
    let taxonomies = {} ;
    taxonomies.contents = [];

    taxonomies.total = 0;
    taxonomies.limit = 0;
    taxonomies.offset = 0;

    if (rows.length == 0) {
      return taxonomies;
    }

    for (let i = 0; i < rows.length ;i++) {
      taxonomies.contents.push({
        tax_id: {
          label: rows[i].tax_id.value,
          href: "/taxon/" + rows[i].tax_id.value
        },
        label: rows[i].l.value
      });
    }

    taxonomies.columns = [];
    taxonomies.columns.push({key: "tax_id", label: "Tax ID"});
    taxonomies.columns.push({key: "label", label: "Name"});
    taxonomies.total = count_rows.total.value ;
    taxonomies.limit = count_rows.limit.value ;
    taxonomies.offset = count_rows.offset.value ;

    return taxonomies;
  }
})
```