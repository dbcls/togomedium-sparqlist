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

http://growthmedium.org/sparql

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
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT 
  (COUNT(DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  VALUES ?tax_id { {{tax_id_ary}} } .
  ?t a taxo:Taxon ;
       taxo:rank ?r ;
       dcterms:identifier ?tax_id ;
       rdfs:label ?l .
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  ?r rdfs:label ?r_label
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
  (GROUP_CONCAT(?auth; SEPARATOR = ", ") AS ?authority)
  (SAMPLE(?r_label) AS ?rank)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/taxonomy/>
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  VALUES ?tax_id { {{tax_id_ary}} } .
  ?t a taxo:Taxon ;
       taxo:rank ?r ;
       dcterms:identifier ?tax_id ;
       rdfs:label ?l .
  ?gm gmo:GMO_000114 ?org .
  ?org gmo:GMO_000020 ?t .
  ?r rdfs:label ?r_label
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
                 href: "/organism/" + rows[i].taxonomy.value},
        name: rows[i].label.value,
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
