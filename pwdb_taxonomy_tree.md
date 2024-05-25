# Returns the tree structure of all taxonomy, or TaxonomyID is specified, only the pathways associated with that Taxonomy

## Parameters

* `pathway_id` PathwayID
  * examples: '399.28.3', '289.248.136', 'rTCA_cycle_variant_1'

## Endpoint

http://togomedium.org/sparql

## `taxonomy_list` count results

```sparql
PREFIX pathway: <http://togomedium.org/pathway/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT DISTINCT ?ancestor_tax AS ?id ?label ?parent COUNT(?pathway) AS ?count
FROM <http://growthmedium.org/pathway>
FROM <http://growthmedium.org/taxonomy/filterd_has_pathway>
{
  {{#if pathway_id}}
  pathway:{{pathway_id}} obo:RO_0002175 ?tax_id .
  {{/if}}
  ?tax_id a ddbj-tax:Taxon ;
    rdfs:subClassOf* ?ancestor_tax  .
  ?ancestor_tax rdfs:label ?label .
  ?ancestor_tax rdfs:subClassOf ?parent .
  OPTIONAL {
    ?pathway obo:RO_0002175 ?ancestor_tax .
  }
}
```

## Output

```javascript
({
  json({taxonomy_list}) {
    const parseSparqlObject = (obj) => {
      const result = {};
      try {
        Object.entries(obj).forEach(([key, item]) => {
          switch (item.datatype) {
            case "http://www.w3.org/2001/XMLSchema#decimal":
              result[key] = parseFloat(item["value"]);
              break;
            case "http://www.w3.org/2001/XMLSchema#integer":
              result[key] = parseInt(item["value"], 10);
              break;
            default:
              result[key] = item["value"];
          }
        });
      } catch (e) {
      }
      return Object.entries(result).length ? result : null;
    };
    //再帰的に辿ってtree構造データを作成
    function retrieve_tree(current_data, all_list) {
      let children = all_list.filter(child => child["parent"] === current_data["id"]);
      if (children.length > 0) {
        children.forEach(child =>{
          retrieve_tree(child, all_list);
        })
        current_data["children"] = children;
      }
    };
     // 有効なデータ数を追加
    function count_num_of_data(current_data) {
      if (current_data["children"]) {
        let children = current_data["children"];
        let sum_num_of_data = 0;
        children.forEach(child =>{
          count_num_of_data(child);
          sum_num_of_data += child["num_of_data"];
        });
        current_data["num_of_data"] = sum_num_of_data;
      } else {
        return null;
      }
    };
    
     // データ数が50個以下なら、それより下位のtaxは全てフラット(階層にしない)にデータ再構築する
    function truncate(current_data) {
      // 上位階層および、下位に50個以上のtaxがあれば、再帰的に下位を辿る
      if ( (["1","131567", "2","2157", "2759"].includes(current_data["id"])) || current_data["num_of_data"] > 50) {
        current_data["children"].forEach(child =>{
          truncate(child);
        })
      } else {
        let new_children = [];
        flatten(current_data, new_children);
        current_data["children"] = new_children;
      }
      delete current_data["parent"];
      delete current_data["count"];
      if (current_data["id"] === "1") { //"cellular organisms" は無意味なので、削除してbacteria等をrootの直下に置く
        current_data["children"] = current_data["children"][0]["children"];
      }
    };
  
    // 指定データ以下のデータについて、データあるもの(count > 0)だけのリストを生成する
    function flatten(current_data, list) {
      if (current_data["children"]) {
        current_data["children"].forEach(child =>{
          if (child["count"] > 0) {
            list.push(child);
          }
          flatten(child, list);
          child["num_of_data"] = 1; //下位の総計をしていたものを1に戻す
          delete child["children"];
          delete child["parent"];
          delete child["count"];
        })
      }
    };
    
    let result_taxonomy_list = taxonomy_list.results.bindings.map((obj) => parseSparqlObject(obj));
    result_taxonomy_list.map((obj) => {
       obj["id"] = obj["id"].substring(obj["id"].lastIndexOf('/') + 1);
       obj["parent"] = obj["parent"].substring(obj["parent"].lastIndexOf('/') + 1);
       // 紐づくpathwayがあれば 1とし UI側 で選択できるように'selectable'フラグを立てる
       obj["num_of_data"] = 0;
       obj["selectable"] = false;
       if (obj["count"] > 0) {
         obj["num_of_data"] = 1;
         obj["selectable"] = true;
       }
    });
    let root_data = {"id": "1", "label": "root", "num_of_data": 0, "selectable": false};
    retrieve_tree(root_data, result_taxonomy_list);
    count_num_of_data(root_data);
    truncate(root_data);
    // TODO: flatten で展開した後に num_of_data は再計算しないと、若干少なめの値になる(中間階層の有効データ分を再カウントする必要がある)
    return root_data;
  }
})
```