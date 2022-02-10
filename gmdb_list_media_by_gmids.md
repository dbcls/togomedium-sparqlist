# List growth media with the given GMIDs (for pagination)

Show a list of growth media with the given GM ID(s).

## Parameters

* `gm_ids` GM ID
  * default: SY46,HM_D00205,NBRC_M5,JCM_M25
  * examples: SY48,HM_D00220,NBRC_M108,JCM_M231
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0


## Endpoint

http://growthmedium.org/sparql

## `gm_id_ary` Parse_argument
```javascript
(gm_ids) => {
  const gm_id_ary = gm_ids.gm_ids.split(",").map((e, i, array)=>{
    return '\"' + e + '\"'
  }).join(" ");
  console.log(gm_ids); 
  return gm_id_ary;
};

```

## `count` count results

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT (COUNT(DISTINCT ?gm_id) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  VALUES ?gm_id { {{gm_id_ary}} } .
  ?gm a gmo:GMO_000001 ;
      dcterms:identifier ?gm_id
  OPTIONAL {
     ?gm rdfs:label|gmo:GMO_000102 ?label
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result` list of growth media

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT *
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/>

WHERE {
  VALUES ?gm_id { {{gm_id_ary}} } .
  ?gm a gmo:GMO_000001 ;
      dcterms:identifier ?gm_id
   OPTIONAL {
     ?gm rdfs:label|gmo:GMO_000102 ?label
   }
}
```

## Output

```javascript
({
  json({result, count}) {
    let rows = result.results.bindings;
    let count_rows = count.results.bindings[0];
    let gms = {};
    gms.contents = [];
    
    gms.total = 0;
    gms.limit = 0;
    gms.offset = 0;
    
    if (rows.length == 0) {
      return gms;
    }
    
    for (let i = 0; i < rows.length ;i++) {
      gms.contents.push({
        gm_id: {label: rows[i].gm_id.value,
                href: "/medium/" + rows[i].gm_id.value},
        label: rows[i].label.value
      });
    }
    
    gms.columns = [];
    gms.columns.push({key: "gm_id", label: "GM ID"});
    gms.columns.push({key: "name", label: "Name"});
    gms.total = count_rows.total.value;
    gms.limit = count_rows.limit.value;
    gms.offset = count_rows.offset.value;
    return gms;
  }
})
```
