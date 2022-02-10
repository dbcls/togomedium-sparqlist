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
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT 
  (COUNT(DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
#FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  ?t a taxo:Taxon ;
     dcterms:identifier ?tax_id ;
     rdfs:label ?l .
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  OPTIONAL {
    ?t taxo:authority ?auth
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
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT 
  ?tax_id
  (SAMPLE(?t) AS ?taxonomy)
  (SAMPLE(?l) AS ?label)
  (GROUP_CONCAT(DISTINCT(?auth); SEPARATOR = ", ") AS ?authority)
  (GROUP_CONCAT(DISTINCT(?gm_id); SEPARATOR = ", ") AS ?media_ids)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
#FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  ?t a taxo:Taxon ;
       dcterms:identifier ?tax_id ;
       rdfs:label ?l .
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  ?gm dcterms:identifier ?gm_id
  OPTIONAL {
    ?t taxo:authority ?auth
  }
} 
GROUP BY ?tax_id
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
