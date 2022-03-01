# Get organism by phenotype

Retrieve organism by phenotype

## Parameters

* `growth_temp` range(min,max) of temperature
  * examples: 20,40
* `growth_ph`  range(min,max) of pH
  * examples: 5,8
* `growth_salinity`  range(min,max) of salinity percentage
  * examples: 0,10
* `MPO_10002` Oxygen requirement type
  * examples: MPO_04002
* `MPO_07001` Gram Strain type
  * examples: MPO_07002
* `MPO_02000` Motility type
  * examples: MPO_02001
* `MPO_01001` Cell shape type
  * examples: MPO_01015
* `MPO_03006` Salinity type
  * examples: MPO_03007
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://growthmedium.org/sparql

## `temp_query_txt`
```javascript
({
  json(params) {
    const temp_criteria_query = `
    {
      VALUES ?min_temp_prop { mpo:MPO_10010 mpo:MPO_10020 }
      VALUES ?max_temp_prop { mpo:MPO_10011 mpo:MPO_10021 }
      ?phenotype ?min_temp_prop ?min_temp_value .
      ?phenotype ?max_temp_prop ?max_temp_value .
      FILTER (?min_temp_value >= #{min} && ?max_temp_value <= #{max})
    }
    UNION
    {
      VALUES ?exact_temp_prop { mpo:MPO_10008 mpo:MPO_10009 }
      ?phenotype ?exact_temp_prop ?exact_temp_value .
      FILTER (?exact_temp_value >= #{min} && ?exact_temp_value <= #{max})
    }`;

    let temp_query_txt = "";
    if (params["growth_temp"] && params["growth_temp"] != "") {
      temp_val = params["growth_temp"].split(",").map((val) => { return val.trim()});
      if (temp_val.length == 2 && temp_val[0].match(/^\-?[0-9\.]+$/) && temp_val[1].match(/^\-?[0-9\.]+$/) ) {
        temp_query_txt = temp_criteria_query.replace(/#{min}/g, temp_val[0]).replace(/#{max}/g, temp_val[1]);
      }
    }
    return temp_query_txt;
  }
})
```

## `ph_query_txt`
```javascript
({
  json(params) {
    const ph_criteria_query = `
     {
      VALUES ?min_ph_prop { mpo:MPO_10006 mpo:MPO_10022 }
      VALUES ?max_ph_prop { mpo:MPO_10007 mpo:MPO_10023 }
      ?phenotype ?min_ph_prop ?min_ph_value .
      ?phenotype ?max_ph_prop ?max_ph_value .
      FILTER (?min_ph_value >= #{min} && ?max_ph_value <= #{max})
    }
    UNION
    {
      VALUES ?exact_ph_prop { mpo:MPO_10004 mpo:MPO_10005 }
      ?phenotype ?exact_ph_prop ?exact_ph_value .
      FILTER (?exact_ph_value >= #{min} && ?exact_ph_value <= #{max})
    }`;

    let ph_query_txt = "";
    if (params["growth_ph"] && params["growth_ph"] != "") {
      ph_val = params["growth_ph"].split(",").map((val) => { return val.trim()});
      if (ph_val.length == 2 && ph_val[0].match(/^\-?[0-9\.]+$/) && ph_val[1].match(/^\-?[0-9\.]+$/) ) {
        ph_query_txt = ph_criteria_query.replace(/#{min}/g, ph_val[0]).replace(/#{max}/g, ph_val[1]);
      }
    }
    return ph_query_txt;
  }
})
```
## `salinity_numeric_query_txt`
```javascript
({
  json(params) {
    const salinity_criteria_query = `
     {
      VALUES ?min_salinity_prop { mpo:MPO_10030 mpo:MPO_10033 }
      VALUES ?max_salinity_prop { mpo:MPO_10029 mpo:MPO_10032 }
      ?phenotype ?min_salinity_prop ?min_salinity_value .
      ?phenotype ?max_salinity_prop ?max_salinity_value .
      FILTER (?min_salinity_value >= #{min} && ?max_salinity_value <= #{max})
    }
    UNION
    {
      VALUES ?exact_salinity_prop { mpo:MPO_10028 mpo:MPO_10031 }
      ?phenotype ?exact_salinity_prop ?exact_salinity_value .
      FILTER (?exact_salinity_value >= #{min} && ?exact_salinity_value <= #{max})
    }`;

    let salinity_query_txt = "";
    if (params["growth_salinity"] && params["growth_salinity"] != "") {
      salinity_val = params["growth_salinity"].split(",").map((val) => { return val.trim()});
      if (salinity_val.length == 2 && salinity_val[0].match(/^\-?[0-9\.]+$/) && salinity_val[1].match(/^\-?[0-9\.]+$/) ) {
        salinity_query_txt = salinity_criteria_query.replace(/#{min}/g, salinity_val[0]).replace(/#{max}/g, salinity_val[1]);
      }
    }
    return salinity_query_txt;
  }
})
```

## `oxygen_req_query_txt`
```javascript
({
  json(params) {
    let oxygen_req_query_txt = "";
    if (params["MPO_10002"] && params["MPO_10002"] != "" && params["MPO_10002"].startsWith("MPO")) {
      oxygen_req_query_txt = "?phenotype mpo:MPO_10002 mpo:" + params["MPO_10002"].trim() + " ."
    }
    return oxygen_req_query_txt;
  }
})
```

## `gram_strain_query_txt`
```javascript
({
  json(params) {
    let gram_strain_query_txt = "";
    if (params["MPO_07001"] && params["MPO_07001"] != "" && params["MPO_07001"].startsWith("MPO")) {
      gram_strain_query_txt = "?phenotype mpo:MPO_07001 mpo:" + params["MPO_07001"].trim() + " ."
    }
    return gram_strain_query_txt;
  }
})
```
## `motility_query_txt`
```javascript
({
  json(params) {
    let motility_query_txt = "";
    if (params["MPO_02000"] && params["MPO_02000"] != "" && params["MPO_02000"].startsWith("MPO")) {
      motility_query_txt = "?phenotype mpo:MPO_02000 mpo:" + params["MPO_02000"].trim() + " ."
    }
    return motility_query_txt;
  }
})
```
## `cell_shape_query_txt`
```javascript
({
  json(params) {
    let cell_shape_query_txt = "";
    if (params["MPO_01001"] && params["MPO_01001"] != "" && params["MPO_01001"].startsWith("MPO")) {
      cell_shape_query_txt = "?phenotype mpo:MPO_01001 mpo:" + params["MPO_01001"].trim() + " ."
    }
    return cell_shape_query_txt;
  }
})
```
## `salinity_query_txt`
```javascript
({
  json(params) {
    let salinity_query_txt = "";
    if (params["MPO_03006"] && params["MPO_03006"] != "" && params["MPO_03006"].startsWith("MPO")) {
      salinity_query_txt = "?phenotype mpo:MPO_03006 mpo:" + params["MPO_03006"].trim() + " ."
    }
    return salinity_query_txt;
  }
})
```
## `count`
```sparql
PREFIX mpo: <http://purl.jp/bio/10/mpo#>
PREFIX prov:    <http://www.w3.org/ns/prov#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?tax_id) AS ?total) ?limit ?offset
FROM <http://growthmedium.org/strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://growthmedium.org/media/20210316>
{
  ?phenotype a prov:Entity .
  {{temp_query_txt}}
  {{ph_query_txt}}
  {{salinity_numeric_query_txt}}
  {{oxygen_req_query_txt}}
  {{gram_strain_query_txt}}
  {{motility_query_txt}}
  {{cell_shape_query_txt}}
  {{salinity_query_txt}}
  ?strain sio:SIO_001279 ?phenotype ;
    rdf:type sio:SIO_010055 ;
    rdfs:label ?strain_name ;
    gmo:taxon  ?tax_id .
  ?tax_id rdfs:label ?tax_name .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for .
  ?medium_id rdf:type gmo:GMO_00001 .
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result`
```sparql
PREFIX mpo: <http://purl.jp/bio/10/mpo#>
PREFIX prov:    <http://www.w3.org/ns/prov#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?tax_id ?tax_name  #?strain ?strain_name
FROM <http://growthmedium.org/strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://growthmedium.org/media/20210316>
{
  ?phenotype a prov:Entity .
  {{temp_query_txt}}
  {{ph_query_txt}}
  {{salinity_numeric_query_txt}}
  {{oxygen_req_query_txt}}
  {{gram_strain_query_txt}}
  {{motility_query_txt}}
  {{cell_shape_query_txt}}
  {{salinity_query_txt}}
  ?strain sio:SIO_001279 ?phenotype ;
    rdf:type sio:SIO_010055 ;
    rdfs:label ?strain_name ;
    gmo:taxon  ?tax_id .
  ?tax_id rdfs:label ?tax_name .
  ?culture_for gmo:strain_id ?strain .
  ?medium_id gmo:GMO_000114 ?culture_for .
  ?medium_id rdf:type gmo:GMO_00001 . #exist media
}
LIMIT {{limit}}
OFFSET {{offset}}
```

## `Output`
```javascript
({
  json({result, count}) {
    let rows = result.results.bindings;
    return rows.map((row) => {
      let tax_id = row["tax_id"]["value"].split("/").pop();
      return {"tax_id": tax_id, "name": row["tax_name"]["value"]};
    });
  }
})
```
