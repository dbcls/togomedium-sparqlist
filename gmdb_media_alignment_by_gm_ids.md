# Get component list for media alignment view

Retrieve component list for media alignment view

## Parameters
* `gm_ids` list of medium id
  * default: M941,M2794
  * default: SY4047,JCM_M900

## Endpoint
http://growthmedium.org/sparql

## `media_values`
```javascript
({
  json(params) {
    return params["gm_ids"].split(",").map((gmid) => {
      return "\""+ gmid.trim() + "\""
    }).join(" ");
  }
})
```
## `media_id_list`
```javascript
({
  json(params) {
    return params["gm_ids"].split(",").map((gmid) => {
      return gmid.trim();
    });
  }
})
```
## `medium_component`
```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT DISTINCT ?medium_id ?original_media_id ?medium_name ?gmo_id
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
WHERE {
  VALUES ?medium_no { {{media_values}} }
  ?medium (dcterms:identifier | skos:altLabel) ?medium_no ;
    dcterms:identifier ?medium_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?medium_name .
  ?medium olo:slot/olo:item ?paragraph .
  ?paragraph rdf:type gmo:Component .
  ?paragraph gmo:has_component ?component .
  ?component  rdfs:label ?component_label .
  ?component gmo:gmo_id ?gmo_id .
  ?gmo_id rdfs:label ?gmo_label .
  FILTER (lang(?gmo_label) = 'en')
}
```

## `medium_organism`
```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX sio: <http://semanticscience.org/resource/>

SELECT DISTINCT ?medium_id ?tax ?tax_name
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/strain/2023>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
WHERE {
  VALUES ?medium_no { {{media_values}} }
  ?medium (dcterms:identifier | skos:altLabel) ?medium_no ;
    dcterms:identifier ?medium_id ;
    gmo:GMO_000114/gmo:strain_id ?strain .
  ?strain a sio:SIO_010055 ;
    gmo:taxon ?tax .
  ?tax rdfs:label ?tax_name .
}
```

## `hieralcal_component_list`
```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT DISTINCT ?ancestor_gmo_id ?ancestor_gmo_label ?parent_gmo_id ?disp_order ?category_name
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
FROM <http://growthmedium.org/gmo/v0.24/display_order>
WHERE {
  VALUES ?medium_no  { {{media_values}} }
  ?medium (dcterms:identifier | skos:altLabel) ?medium_no ;
    rdfs:label ?medium_name .
  ?medium olo:slot/olo:item ?paragraph .
  ?paragraph rdf:type gmo:Component ;
    gmo:has_component ?component .
  ?component  rdfs:label ?component_label ;
    gmo:gmo_id ?gmo_id .
  ?gmo_id rdfs:subClassOf* ?ancestor_gmo_id .
   ?ancestor_gmo_id rdfs:label ?ancestor_gmo_label .
   FILTER (lang(?ancestor_gmo_label) = 'en')
  ?ancestor_gmo_id rdfs:subClassOf ?parent_gmo_id ;
    gmo:display_order ?disp_order ;
    gmo:category ?category_name .
} ORDER BY ?disp_order
```


## Output

```javascript
({
  json({media_id_list, medium_component, medium_organism, hieralcal_component_list}) {
    let medium_component_list = medium_component.results.bindings;
    let medium_organism_list = medium_organism.results.bindings;

    // media
    let medium_id_list = medium_component_list.map((row) => { return row["medium_id"]["value"]})
    let medium_id_uniq_list = Array.from(new Set(medium_id_list));
    let media = [];
    medium_id_uniq_list.forEach((medium_id) => {
      let media_info = {"gm_id": medium_id};
      let component_list = [];
      let organism_list = [];
      let media_name = "";
      let hit_media = medium_component_list.find((row) => row["medium_id"]["value"] == medium_id);
      media_info["name"] = hit_media["medium_name"]["value"];
      media_info["original_media_id"] = hit_media["original_media_id"]["value"];
      medium_component_list.forEach((row) => {
        if (row["medium_id"]["value"] == medium_id) {
          component_list.push(row["gmo_id"]["value"].split("/").pop());
        }
      });
      medium_organism_list.forEach((row) => {
        if (row["medium_id"]["value"] == medium_id) {
          organism_list.push(row["tax"]["value"].split("/").pop());
        }
      });
      media_info["components"] = Array.from(new Set(component_list));
      media_info["organisms"] = Array.from(new Set(organism_list));
      media.push(media_info);
    });
    // paramsの指定順にsort
    let media_order = {};
    media_id_list.map((gmid, idx) => {
      media_order[gmid] = idx;
    });
    media.sort(function(a,b){
      let a_order = media_order[a["gm_id"]];
      let b_order = media_order[b["gm_id"]];
      if( a_order < b_order ) return -1;
      if( a_order > b_order ) return 1;
      return 0;
    });
    // organisms
    let tax_list = medium_organism_list.map((row) => {
      return {"tax_id": row["tax"]["value"].split("/").pop(), "name": row["tax_name"]["value"] }
    });
    // components
    let medium_component_hieralcal_list = hieralcal_component_list.results.bindings;
    let component_list = medium_component_hieralcal_list.map((row) => {
      let gmoid = row["ancestor_gmo_id"]["value"].split("/").pop();
      let gmo_label = row["ancestor_gmo_label"]["value"];
      let parent = row["parent_gmo_id"]["value"].split("/").pop();
      if (parent == "GMO_000002") {
        parent = null;
      }
      let category = row["category_name"]["value"];
      let display_order = parseInt(row["disp_order"]["value"]);
      return {"gmo_id": gmoid, "name": gmo_label, parent: parent, category: category, display_order: display_order}
    });

    return {"media": media, "organisms": Array.from(new Set(tax_list)), "components": component_list }
  }
})
```