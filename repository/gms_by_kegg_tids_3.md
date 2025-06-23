# Growth_media_by_KEGG_TIDs 3 : moriya (gm, growth_media)

## Parameters

* `t_id` KEGG organism identifiers
  * default: T04525,T00311
  * example: T00311


## `t_ids`

```javascript
({t_id}) => {
  const t_ids = t_id.split(",").map((e, i, array)=>{
    return '\"' + e + '\"'
  }).join(" ");
  return t_ids;
};
```

## Endpoint

http://ep.dbcls.jp/sparql71tmp

## `gm_tid`

```sparql
DEFINE sql:select-option "order"
prefix gmo: <http://purl.jp/bio/10/gmo/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix dcterms: <http://purl.org/dc/terms/>
prefix kegg: <http://www.kegg.jp/entry/>
prefix mccv: <http://purl.jp/bio/10/mccv#>
SELECT DISTINCT ?gm ?gm_label ?tid
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/0.18/>
FROM <http://growthmedium.org/cluster/jaccard/200>
FROM <http://purl.jp/bio/103/nite/culture/>
FROM <http://metadb.riken.jp/db/jcm/>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://kegg/tnumber/>
WHERE {
  VALUES ?tid { {{t_ids}} }
  BIND(IRI(CONCAT("http://www.kegg.jp/entry/", ?tid)) AS ?t)
  {
     ?cc mccv:MCCV_000073/mccv:MCCV_000018 ?gm .
     ?cc mccv:MCCV_000023|mccv:MCCV_000065 ?taxonomy .
     ?t rdfs:seeAlso ?taxonomy
  } UNION {
     ?gm gmo:GMO_000000 ?t
  }
  ?gm rdfs:label ?gm_label .
}
ORDER BY ?gm
```

## `gm_list`

```javascript
({gm_tid})=>{
  let list = gm_tid.results.bindings;
  let gms = {};
  for(let i = 0; i < list.length; i++){
    gms[list[i].gm.value.replace("http://purl.jp/bio/10/gm/", "gm:")] = 1;
  }
  return Object.keys(gms).join(" ");
};
```

## Endpoint

http://ep.dbcls.jp/sparql71tmp

## `gm_component`

```sparql
DEFINE sql:select-option "order"
prefix gm: <http://purl.jp/bio/10/gm/>
prefix gmo: <http://purl.jp/bio/10/gmo/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?gm ?component ?component_id ?c_label ?role ?role_label
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/0.18/>
FROM <http://growthmedium.org/cluster/jaccard/200>
FROM <http://purl.jp/bio/103/nite/culture/>
FROM <http://metadb.riken.jp/db/jcm/>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
WHERE {
  VALUES ?gm { {{gm_list}} }
  ?gm gmo:GMO_000104 ?component .
  ?component skos:prefLabel ?c_label .
  ?component dcterms:identifier ?component_id .
  OPTIONAL {
    ?component gmo:GMO_000112 ?role .
    ?role rdfs:label ?role_label
    FILTER(LANG(?role_label) = "en")
  }
}
ORDER BY ?gm
```

## Endpoint

http://ep.dbcls.jp/sparql71tmp

## `parent_component`

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?child ?parent ?label
FROM <http://growthmedium.org/media/>
FROM <http://growthmedium.org/gmo/0.18/>
WHERE {
  VALUES ?parent { gmo:GMO_000011 gmo:GMO_000012 gmo:GMO_000013 gmo:GMO_000019 gmo:GMO_001004 gmo:GMO_001006 
                                  gmo:GMO_001007 gmo:GMO_001008 gmo:GMO_001009 gmo:GMO_001012 gmo:GMO_001015 
                                  gmo:GMO_001017 gmo:GMO_001018 gmo:GMO_001019 gmo:GMO_001025 gmo:GMO_001026 
                                  gmo:GMO_001027 gmo:GMO_001028 gmo:GMO_001029 gmo:GMO_001030 gmo:GMO_001031 
                                  gmo:GMO_001032 gmo:GMO_001033 gmo:GMO_001034 gmo:GMO_001035 gmo:GMO_001037 
                                  gmo:GMO_001038 gmo:GMO_001045 gmo:GMO_001048 gmo:GMO_001049 gmo:GMO_001052 
                                  gmo:GMO_001053 gmo:GMO_001054 gmo:GMO_001055 gmo:GMO_001056 gmo:GMO_001058 
                                  gmo:GMO_001060 gmo:GMO_001061 gmo:GMO_001062 gmo:GMO_001063 gmo:GMO_001066 
                                  gmo:GMO_001067 gmo:GMO_001069 gmo:GMO_001070 gmo:GMO_001072 gmo:GMO_001073 
                                  gmo:GMO_001078 gmo:GMO_001080 gmo:GMO_001082 gmo:GMO_001083 gmo:GMO_001084 
                                  gmo:GMO_001086 gmo:GMO_001088 gmo:GMO_001090 gmo:GMO_001091 gmo:GMO_001092 
                                  gmo:GMO_001093 gmo:GMO_001094 gmo:GMO_001096 gmo:GMO_001098 gmo:GMO_001099 
                                  gmo:GMO_001100 gmo:GMO_001101 gmo:GMO_001103 gmo:GMO_001105 gmo:GMO_001107 
                                  gmo:GMO_001108 gmo:GMO_001109 gmo:GMO_001111 gmo:GMO_001112 gmo:GMO_001114 
                                  gmo:GMO_001118 gmo:GMO_001120 gmo:GMO_001121 gmo:GMO_001122 gmo:GMO_001123 
                                  gmo:GMO_001124 gmo:GMO_001126 gmo:GMO_001131 gmo:GMO_001132 gmo:GMO_001133 
                                  gmo:GMO_001134 gmo:GMO_001135 gmo:GMO_001136 gmo:GMO_001137 gmo:GMO_001138 
                                  gmo:GMO_001139 gmo:GMO_001141 gmo:GMO_001142 gmo:GMO_001143 gmo:GMO_001145 
                                  gmo:GMO_001147 gmo:GMO_001152 gmo:GMO_001153 gmo:GMO_001154 gmo:GMO_001156 
                                  gmo:GMO_001158 gmo:GMO_001159 gmo:GMO_001160 gmo:GMO_001161 gmo:GMO_001162 
                                  gmo:GMO_001165 gmo:GMO_001167 gmo:GMO_001170 gmo:GMO_001172 gmo:GMO_001173 
                                  gmo:GMO_001175 gmo:GMO_001177 gmo:GMO_001178 gmo:GMO_001179 gmo:GMO_001180 
                                  gmo:GMO_001181 gmo:GMO_001182 gmo:GMO_001184 gmo:GMO_001187 gmo:GMO_001188 
                                  gmo:GMO_001189 gmo:GMO_001190 gmo:GMO_001191 gmo:GMO_001192 gmo:GMO_001193 
                                  gmo:GMO_001195 gmo:GMO_001199 gmo:GMO_001200 gmo:GMO_001202 gmo:GMO_001203 
                                  gmo:GMO_001206 gmo:GMO_001207 gmo:GMO_001208 gmo:GMO_001210 gmo:GMO_001211 
                                  gmo:GMO_001212 gmo:GMO_001214 gmo:GMO_001215 gmo:GMO_001217 gmo:GMO_001218 
                                  gmo:GMO_001219 gmo:GMO_001221 gmo:GMO_001223 gmo:GMO_001225 gmo:GMO_001226 
                                  gmo:GMO_001230 gmo:GMO_001231 gmo:GMO_001233 gmo:GMO_001234 gmo:GMO_001236 
                                  gmo:GMO_001237 gmo:GMO_001239 gmo:GMO_001240 gmo:GMO_001241 gmo:GMO_001244 
                                  gmo:GMO_001245 gmo:GMO_001246 gmo:GMO_001247 gmo:GMO_001248 gmo:GMO_001250 
                                  gmo:GMO_001251 gmo:GMO_001252 gmo:GMO_001253 gmo:GMO_001255 gmo:GMO_001256 
                                  gmo:GMO_001258 gmo:GMO_001259 gmo:GMO_001261 gmo:GMO_001263 gmo:GMO_001264 
                                  gmo:GMO_001268 gmo:GMO_001269 gmo:GMO_001270 gmo:GMO_001271 gmo:GMO_001272 
                                  gmo:GMO_001273 gmo:GMO_001275 gmo:GMO_001280 gmo:GMO_001281 gmo:GMO_001283 
                                  gmo:GMO_001284 gmo:GMO_001288 gmo:GMO_001289 gmo:GMO_001292 gmo:GMO_001294 
                                  gmo:GMO_001296 gmo:GMO_001298 gmo:GMO_001299 gmo:GMO_001301 gmo:GMO_001303 
                                  gmo:GMO_001305 gmo:GMO_001307 gmo:GMO_001308 gmo:GMO_001309 gmo:GMO_001310 
                                  gmo:GMO_001311 gmo:GMO_001312 gmo:GMO_001314 gmo:GMO_001317 gmo:GMO_001318 
                                  gmo:GMO_001323 gmo:GMO_001324 gmo:GMO_001325 gmo:GMO_001326 gmo:GMO_001327 
                                  gmo:GMO_001328 gmo:GMO_001329 gmo:GMO_001330 gmo:GMO_001334 gmo:GMO_001335 
                                  gmo:GMO_001336 gmo:GMO_001337 gmo:GMO_001338 gmo:GMO_001341 gmo:GMO_001343 
                                  gmo:GMO_001345 gmo:GMO_001346 gmo:GMO_001347 gmo:GMO_001349 gmo:GMO_001350 
                                  gmo:GMO_001351 gmo:GMO_001352 gmo:GMO_001354 gmo:GMO_001356 gmo:GMO_001358 
                                  gmo:GMO_001361 gmo:GMO_001365 gmo:GMO_001368 gmo:GMO_001369 gmo:GMO_001371 
                                  gmo:GMO_001372 gmo:GMO_001373 gmo:GMO_001375 gmo:GMO_001378 gmo:GMO_001379 
                                  gmo:GMO_001380 gmo:GMO_001383 gmo:GMO_001385 gmo:GMO_001386 gmo:GMO_001388 
                                  gmo:GMO_001389 gmo:GMO_001391 gmo:GMO_001395 gmo:GMO_001398 gmo:GMO_001401 
                                  gmo:GMO_001402 gmo:GMO_001404 gmo:GMO_001405 gmo:GMO_001407 gmo:GMO_001409 
                                  gmo:GMO_001410 gmo:GMO_001411 gmo:GMO_001412 gmo:GMO_001414 gmo:GMO_001416 
                                  gmo:GMO_001418 gmo:GMO_001421 gmo:GMO_001422 gmo:GMO_001425 gmo:GMO_001426 
                                  gmo:GMO_001428 gmo:GMO_001429 gmo:GMO_001430 gmo:GMO_001431 gmo:GMO_001433 
                                  gmo:GMO_001436 gmo:GMO_001437 gmo:GMO_001441 gmo:GMO_001443 gmo:GMO_001444 
                                  gmo:GMO_001445 gmo:GMO_001452 gmo:GMO_001453 gmo:GMO_001461 gmo:GMO_001470 
                                  gmo:GMO_001474 gmo:GMO_001482 gmo:GMO_001495 gmo:GMO_001497 gmo:GMO_001503 
                                  gmo:GMO_001513 gmo:GMO_001515 gmo:GMO_001518 gmo:GMO_001526 gmo:GMO_001527 
                                  gmo:GMO_001528 gmo:GMO_001531 gmo:GMO_001533 gmo:GMO_001536 gmo:GMO_001537 
                                  gmo:GMO_001540 gmo:GMO_001541 gmo:GMO_001542 gmo:GMO_001544 gmo:GMO_001545 
                                  gmo:GMO_001546 gmo:GMO_001547 gmo:GMO_001554 gmo:GMO_001558 gmo:GMO_001559 
                                  gmo:GMO_001560 gmo:GMO_001564 gmo:GMO_001565 gmo:GMO_001566 gmo:GMO_001569 
                                  gmo:GMO_001573 gmo:GMO_001578 gmo:GMO_001581 gmo:GMO_001582 gmo:GMO_001583 
                                  gmo:GMO_001589 gmo:GMO_001598 gmo:GMO_001600 gmo:GMO_001601 gmo:GMO_001602 
                                  gmo:GMO_001608 gmo:GMO_001609 gmo:GMO_001611 gmo:GMO_001613 gmo:GMO_001614 
                                  gmo:GMO_001616 gmo:GMO_001617 gmo:GMO_001618 gmo:GMO_001628 gmo:GMO_001629 
                                  gmo:GMO_001632 gmo:GMO_001638 gmo:GMO_001639 gmo:GMO_001641 gmo:GMO_001642 
                                  gmo:GMO_001648 gmo:GMO_001649 gmo:GMO_001650 gmo:GMO_001651 gmo:GMO_001656 
                                  gmo:GMO_001657 gmo:GMO_001659 gmo:GMO_001660 gmo:GMO_001663 gmo:GMO_001664 
                                  gmo:GMO_001666 gmo:GMO_001675 gmo:GMO_001676 gmo:GMO_001679 gmo:GMO_001680 
                                  gmo:GMO_001683 gmo:GMO_001691 gmo:GMO_001692 gmo:GMO_001693 gmo:GMO_001694 
                                  gmo:GMO_001699 gmo:GMO_001701 gmo:GMO_001704 gmo:GMO_001706 gmo:GMO_001707 
                                  gmo:GMO_001710 gmo:GMO_001711 gmo:GMO_001712 gmo:GMO_001713 gmo:GMO_001714 
                                  gmo:GMO_001716 gmo:GMO_001717 gmo:GMO_001719 gmo:GMO_001722 gmo:GMO_001724 
                                  gmo:GMO_001725 gmo:GMO_001727 gmo:GMO_001728 gmo:GMO_001731 gmo:GMO_001732 
                                  gmo:GMO_001734 gmo:GMO_001748 gmo:GMO_001751 gmo:GMO_001756 gmo:GMO_001758 
                                  gmo:GMO_001762 gmo:GMO_001763 gmo:GMO_001764 gmo:GMO_001765 gmo:GMO_001769 
                                  gmo:GMO_001773 gmo:GMO_001775 gmo:GMO_001779 gmo:GMO_001782 gmo:GMO_001787 
                                  gmo:GMO_001790 gmo:GMO_001793 gmo:GMO_001796 gmo:GMO_001799 gmo:GMO_001802 
                                  gmo:GMO_001807 gmo:GMO_001810 gmo:GMO_001815 gmo:GMO_001816 gmo:GMO_001817 
                                  gmo:GMO_001820 gmo:GMO_001821 gmo:GMO_001822 gmo:GMO_001823 gmo:GMO_001824 
                                  gmo:GMO_001825 gmo:GMO_001829 gmo:GMO_001830 gmo:GMO_001831 gmo:GMO_001832 
                                  gmo:GMO_001834 gmo:GMO_001836 gmo:GMO_001839 gmo:GMO_001840 gmo:GMO_001841 
                                  gmo:GMO_001846 gmo:GMO_001852 gmo:GMO_001853 gmo:GMO_001854 gmo:GMO_001855 
                                  gmo:GMO_001856 gmo:GMO_001857 gmo:GMO_001860 gmo:GMO_001861 gmo:GMO_001863 
                                  gmo:GMO_001864 gmo:GMO_001865 gmo:GMO_001866 gmo:GMO_001868 gmo:GMO_001869 
                                  gmo:GMO_001874 gmo:GMO_001875 gmo:GMO_001877 gmo:GMO_001882 gmo:GMO_001883 
                                  gmo:GMO_001884 gmo:GMO_001885 gmo:GMO_001886 gmo:GMO_001887 gmo:GMO_001888 
                                  gmo:GMO_001890 gmo:GMO_001891 gmo:GMO_001893 gmo:GMO_001894 gmo:GMO_001897 
                                  gmo:GMO_001898 gmo:GMO_001902 gmo:GMO_001904 gmo:GMO_001905 gmo:GMO_001906 
                                  gmo:GMO_001907 gmo:GMO_001908 gmo:GMO_001910 gmo:GMO_001911 gmo:GMO_001912 
                                  gmo:GMO_001913 gmo:GMO_001915 gmo:GMO_001916 gmo:GMO_001917 gmo:GMO_001924 
                                  gmo:GMO_001926 gmo:GMO_001927 gmo:GMO_001928 gmo:GMO_001933 gmo:GMO_001934 
                                  gmo:GMO_001935 gmo:GMO_001937 gmo:GMO_001941 gmo:GMO_001944 gmo:GMO_001945 
                                  gmo:GMO_001946 gmo:GMO_001952 gmo:GMO_001953 gmo:GMO_001959 }
  ?child rdfs:subClassOf* ?parent .
  ?parent skos:prefLabel ?label .
}
```

## `kegg_tid_sp`

```javascript
async ({})=>{
  let kegg_api = "http://rest.kegg.jp/list/organism";
 // let kegg_api = "http://sparql-support.dbcls.jp/api/relay?endpoint=http://rest.kegg.jp/list/organism"; // for SPARQList support
  let options_text = {
    method: "get",
    mode:  "cors"
  };
  let text = await fetch(kegg_api, options_text).then(res => res.text());
  let list = text.split(/\n/);
  let r = {};
  for(let i = 0; i < list.length; i++){
    let tmp = list[i].split(/\t/);
    if(tmp[0]) r[tmp[0]] = tmp[2].replace(/ +\(.+$/, "");
  }
  return r;
};
```

## `Output`

```javascript
({gm_tid, gm_component, parent_component, kegg_tid_sp})=>{
    let array = gm_tid.results.bindings;
	let gm_obj = {};
    for (let elm of array) {
      let sp_label = "";
      if(kegg_tid_sp[elm.tid.value]) sp_label = kegg_tid_sp[elm.tid.value];
      if(!gm_obj[elm.gm.value]){
        gm_obj[elm.gm.value] = {
            label: elm.gm_label.value,        
            species: [{tid: elm.tid.value, label: sp_label}],
            components_group: {}
        }
      }else{
        gm_obj[elm.gm.value].species.push({tid: elm.tid.value, label: sp_label})
      }
    }

    array = parent_component.results.bindings;
    let comp2parent = {};
    for (let elm of array) {
      comp2parent[elm.child.value] = { parent: elm.parent.value, label: elm.label.value };
    }
  	array = gm_component.results.bindings;
    let component2role = {};
    let chk = {};
    for (let elm of array) {
      if(elm.role){
        if(component2role[elm.component.value] && !chk[elm.role.value]) component2role[elm.component.value].push({uri: elm.role.value, label: elm.role_label.value});
        else{
          component2role[elm.component.value] = [{uri: elm.role.value, label: elm.role_label.value}];
        }
        chk[elm.role.value] = 1;
      }
    }
    
  	let parent_count = {};
    chk = {};
    for (let elm of array) {
      if(chk[elm.gm.value + "_" + elm.component.value]) continue;
      let obj = {
        component: {
          uri: elm.component.value,
          label: elm.c_label.value
        }
      }
      if(component2role[elm.component.value]){
        obj.role = [...new Set(component2role[elm.component.value])]; // unique
      }
      let parent = {};
      if(comp2parent[elm.component.value]){ 
        parent.id = comp2parent[elm.component.value].parent;
        parent.label = comp2parent[elm.component.value].label;
      }else{ // no parent in GMO_001684, 001685 'Obsolete:' flag
        continue;
        //parent.id = elm.component.value;
        //parent.label = elm.c_label.value;
      }
      if(gm_obj[elm.gm.value].components_group[parent.id]) gm_obj[elm.gm.value].components_group[parent.id].elements.push(obj);
      else{ 
      	gm_obj[elm.gm.value].components_group[parent.id] = {
      	  label: parent.label,
          elements: [obj]
        }
      }
      chk[elm.gm.value + "_" + elm.component.value] = 1;
    }

    return {growth_media: Object.keys(gm_obj).map(function(gm){ return {uri: gm, label: gm_obj[gm].label, species: gm_obj[gm].species, components_group: gm_obj[gm].components_group}; })};
  };
```
