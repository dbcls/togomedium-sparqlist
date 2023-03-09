# List strains in TogoMedium (for pagination)

Show a list of strains in TogoMedium.

## Parameters

* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

## `count` count number of all strains in TogoMedium

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT
  (COUNT(DISTINCT ?strain_id) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/media/2023>
WHERE {
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain rdf:type sio:SIO_010055 ;
    dcterms:identifier ?strain_id ;
    rdfs:label ?strain_name ;
    gmo:origin_strain/dcterms:identifier ?original_strain_id .
  OPTIONAL {
    ?strain gmo:taxon ?taxon_url .
    ?taxon_url dcterms:identifier ?tax_id ;
    rdfs:label ?tax_name .
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve all strains

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT
  ?strain_id ?strain_name ?tax_id ?tax_name
  (GROUP_CONCAT(DISTINCT ?original_strain_id; SEPARATOR = ", ") AS ?original_strain_ids)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/media/2023>
WHERE {
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain rdf:type sio:SIO_010055 ;
    dcterms:identifier ?strain_id ;
    rdfs:label ?strain_name ;
    gmo:origin_strain/dcterms:identifier ?original_strain_id .
  OPTIONAL {
    ?strain gmo:taxon ?taxon_url .
    ?taxon_url dcterms:identifier ?tax_id ;
      rdfs:label ?tax_name .
  }
}
GROUP BY ?strain_id ?strain_name ?tax_id ?tax_name
ORDER BY ?strain_name
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    const unescapeJsonString = (str) => {
        return str === null || str === void 0 ? void 0 : str.replace(/\\/g, "");
    };

    let rows = result.results.bindings ;
    let count_rows = count.results.bindings[0] ;
    let strains = {} ;
    strains.contents = [];

    strains.total = 0;
    strains.limit = 0;
    strains.offset = 0;

    if (rows.length == 0) {
      return strains;
    }

    for (let i = 0; i < rows.length ;i++) {
      strains.contents.push({
        strain_id: {label: rows[i].strain_id.value,
                 href: "/organism/" + rows[i].strain_id.value},
        name: rows[i].strain_name.value,
        other_ids: rows[i].original_strain_ids.value,
        taxonomy: {label: rows[i].tax_name ? rows[i].tax_name.value : "",
                 href: rows[i].tax_id ? "/taxon/" + rows[i].tax_id.value : ""}
      });
    }

    strains.columns = [];
    strains.columns.push({key: "strain_id", label: "Tax ID"});
    strains.columns.push({key: "name", label: "Name"});
    strains.columns.push({key: "other_ids", label: "Other IDs"});
    strains.columns.push({key: "taxonomy", label: "Taxonomy"});
    strains.total = count_rows.total.value ;
    strains.limit = count_rows.limit.value ;
    strains.offset = count_rows.offset.value ;

    return strains;
  }
})
```
