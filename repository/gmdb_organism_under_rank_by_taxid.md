# List of lower-ranked taxons by a taxonomy rank

## Parameters

* `tax_id`
  * default: 201174
  * example: 1883(huge ginus), 562(species rank), (strain)
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `ranks`
```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?rank
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
WHERE {
  VALUES ?tax_id { {{tax_id}} }
  ?search_tax a taxont:Taxon ;
      dcterms:identifier ?tax_id .
   ?search_tax rdfs:subClassOf* ?parent_tax .
   ?parent_tax taxont:rank ?rank
}
```
## `rank_pettern`
```javascript
({
  json({ranks}) {
    let rows = ranks.results.bindings ;
    if (rows.length == 0){
      return null;
    }
    const rank_list = ["Superkingdom" , "Phylum", "Class", "Order", "Family", "Genus", "Species" ]
    let index_list = rows.map((row) => {
      return rank_list.findIndex( (rank) => rank === row.rank.value.split('/').pop());
    });
    let rank_pattern = "";
    let max_index = Math.max(...index_list); // 最下位ランクのindex
    if (max_index >= rank_list.length - 1) { // Speciesランクなら下位ランクは指定しない
      rank_pattern = "?any_rank";
    } else { // 一つ下のランクを指定する
      rank_pattern = "taxont:" + rank_list[max_index + 1];
    }
    return rank_pattern ;
  }
})
```

## `count`
```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?child_tax) AS ?total) ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
FROM <http://togomedium.org/media>
WHERE {
  VALUES ?tax_id { {{tax_id}} }
  ?search_tax a taxont:Taxon ;
    dcterms:identifier ?tax_id .
  ?child_tax rdfs:subClassOf* ?search_tax ;
    dcterms:identifier ?child_tax_id ;
    rdfs:label ?child_tax_name ;
    taxont:rank {{rank_pettern}} .
  ?descent_tax rdfs:subClassOf+ ?search_tax .
  ?strain gmo:taxon ?descent_tax .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 . #exist media
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result`
```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT ?child_tax_id ?child_tax_name ?rank_name COUNT(DISTINCT ?medium) AS ?num_of_media
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
FROM <http://togomedium.org/media>
WHERE {
  VALUES ?tax_id { {{tax_id}} }
  ?search_tax a taxont:Taxon ;
     dcterms:identifier ?tax_id .
  ?child_tax rdfs:subClassOf+ ?search_tax ;
    dcterms:identifier ?child_tax_id ;
    rdfs:label ?child_tax_name ;
    taxont:rank {{rank_pettern}} ;
    taxont:rank/rdfs:label ?rank_name .
  OPTIONAL {
    ?descent_tax rdfs:subClassOf* ?child_tax .
    ?strain gmo:taxon ?descent_tax .
    ?culture_for gmo:strain_id ?strain .
    ?medium gmo:GMO_000114 ?culture_for ;
      rdf:type  gmo:GMO_000001 . #exist media
  }
}
GROUP BY  ?child_tax_id ?child_tax_name ?rank_name
ORDER BY DESC(?num_of_media)
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    const parseSparqlObject = (obj) => {
      const result = {};
      try {
        Object.entries(obj).forEach(([key, item]) => {
          result[key] = item["value"];
        });
      } catch (e) {
      }
      return Object.entries(result).length ? result : null;
    };

    const info = parseSparqlObject(count.results.bindings[0]);
    const total = !!info ? parseInt(info.total) : 0;
    const offset = !!info ? parseInt(info.offset) : 0;
    const limit = !!info ? parseInt(info.limit) : 0;

    const KEY_TAX_ID = "tax_id";
    const KEY_Label= "name";
    const KEY_RANK= "rank";
    const KEY_MEDIA_COUNT = "num_of_media";
    const columns = [
      {key: KEY_TAX_ID, label: "Tax ID"},
      {key: KEY_Label, label: "Name"},
      {key: KEY_RANK, label: "Rank"},
      {key: KEY_MEDIA_COUNT, label: "Num Of Media"}
    ];

    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((item) => ({
        [KEY_Label]: item.child_tax_name,
        [KEY_RANK]: item.rank_name.charAt(0).toUpperCase() + item.rank_name.slice(1).toLowerCase(), // capitalize
        [KEY_MEDIA_COUNT]: item.num_of_media,
        [KEY_TAX_ID]: {
          label: item.child_tax_id,
          href: `/taxon/${item.child_tax_id}`,
        },
      }));
    return {total, offset, contents, columns, limit};
  }
})
```
