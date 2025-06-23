# List organisms with the given tax IDs (for pagination)

Show a list of organisms with the given tax ID(s).

## Parameters

* `tax_ids` tax IDs
  * default: 157463,1383816,38005
  * examples: 156980,1490222,392500,525904
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `tax_id_ary` Parse_argument
```javascript

(tax_ids) => {
  const tax_id_ary = tax_ids.tax_ids.split(",").map((e, i, array)=>{
    return e
  }).join(" ");
  return tax_id_ary;
};

```

## `count` count organisms with given taxids

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT
  (COUNT(DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
WHERE {
  VALUES ?tax_id { {{tax_id_ary}} } .
  ?taxon_url a ddbj-tax:Taxon ;
    ddbj-tax:rank ?rank ;
    dcterms:identifier ?tax_id ;
    rdfs:label ?tax_name .
  ?strain gmo:taxon ?taxon_url ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?rank rdfs:label ?rank_label .
  OPTIONAL {
    ?taxon_url ddbj-tax:authority ?auth
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}

```

## `result` retrieve organisms with given taxids

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT ?tax_id ?taxon_url ?tax_name ?rank_label
  (GROUP_CONCAT(?auth; SEPARATOR = ", ") AS ?authority)
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
WHERE {
  VALUES ?tax_id { {{tax_id_ary}} } .
  ?taxon_url a ddbj-tax:Taxon ;
    ddbj-tax:rank ?rank ;
    dcterms:identifier ?tax_id ;
    rdfs:label ?tax_name .
  ?strain gmo:taxon ?taxon_url ;
    rdf:type sio:SIO_010055 .
  ?culture_for gmo:strain_id ?strain .
  ?medium_uri gmo:GMO_000114 ?culture_for ;
    rdf:type gmo:GMO_000001 . #exist media
  ?rank rdfs:label ?rank_label .
  OPTIONAL {
    ?taxon_url ddbj-tax:authority ?auth
  }
}
GROUP BY ?taxon_url ?tax_id ?tax_name  ?rank_label
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
        tax_id: {label: rows[i].tax_id.value,
                 href: "/taxon/" + rows[i].tax_id.value},
        name: rows[i].tax_name.value,
        authority_name: rows[i].authority.value
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
