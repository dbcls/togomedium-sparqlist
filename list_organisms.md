# List organisms in TogoMedium (for pagination)

Show a list of organisms in TogoMedium.

## Parameters

* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

## `count` count number of all organisms in TogoMedium

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT
  (COUNT(DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/media/2023>
WHERE {
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain gmo:taxon ?taxon_url .
  # dcterms:identifier ?strain_id ;
  # rdfs:label ?strain_name ;
  # origin_strain/dcterms:identifier ?original_strain_names
  ?taxon_url dcterms:identifier ?tax_id
  OPTIONAL {
    ?taxon_url ddbj-tax:authority ?auth
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve organisms with given taxids

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT
  ?tax_id ?label
  (GROUP_CONCAT(DISTINCT(?auth); SEPARATOR = ", ") AS ?authority)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/media/2023>
WHERE {
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?culture_for gmo:strain_id ?strain .
  ?strain gmo:taxon ?taxon_url ;
    rdf:type sio:SIO_010055 .
  # dcterms:identifier ?strain_id ;
  # rdfs:label ?strain_name ;
  # origin_strain/dcterms:identifier ?original_strain_names
  ?taxon_url dcterms:identifier ?tax_id ;
    rdfs:label ?label
  OPTIONAL {
    ?taxon_url ddbj-tax:authority ?auth
  }
}
GROUP BY ?tax_id ?label
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
        tax_id: {label: rows[i].tax_id.value,
                 href: "/organism/" + rows[i].tax_id.value},
        name: rows[i].label.value,
        authority_name: unescapeJsonString(rows[i].authority.value)
      });
    }

    taxonomies.columns = [];
    taxonomies.columns.push({key: "tax_id", label: "Tax ID"});
    taxonomies.columns.push({key: "name", label: "Name"});
    taxonomies.columns.push({key: "authority_name", label: "Authority name"});
    taxonomies.total = count_rows.total.value ;
    taxonomies.limit = count_rows.limit.value ;
    taxonomies.offset = count_rows.offset.value ;

    return taxonomies;
  }
})
```
