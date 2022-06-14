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
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT
  (COUNT(DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/media/20210316>

WHERE {
  ?media gmo:GMO_000114 ?media_strain ;
    dcterms:identifier ?gm_id .
  ?media_strain gmo:strain_id ?strain_id .
  ?strain_id gmo:taxon ?tax .
  ?tax a taxo:Taxon ;
     dcterms:identifier ?tax_id ;
     rdfs:label ?tax_name .
  OPTIONAL {
    ?tax taxo:authority ?auth
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` retrieve organisms with given taxids

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT
  ?tax_id
  (?tax_name AS ?label)
  (GROUP_CONCAT(DISTINCT(?auth); SEPARATOR = ", ") AS ?authority)
  (GROUP_CONCAT(DISTINCT(?gm_id); SEPARATOR = ", ") AS ?media_ids)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain>
FROM <http://growthmedium.org/media/20210316>

WHERE {
  ?media gmo:GMO_000114 ?media_strain ;
    dcterms:identifier ?gm_id .
  ?media_strain gmo:strain_id ?strain_id .
  ?strain_id gmo:taxon ?tax .
  ?tax a taxo:Taxon ;
     dcterms:identifier ?tax_id ;
     rdfs:label ?tax_name .
  OPTIONAL {
    ?tax taxo:authority ?auth
  }
}
GROUP BY ?tax_id ?tax_name
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
        authority_name: unescapeJsonString(rows[i].authority.value),
        media: rows[i].media_ids.value
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
