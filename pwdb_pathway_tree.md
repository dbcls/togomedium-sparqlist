# Returns the tree structure of all pathways, or TaxonomyID is specified, only the pathways associated with that Taxonomy

## Parameters

* `tax_id` TaxononyID
  * examples: 1665

## Endpoint

http://togomedium.org/sparql

## `pathway_list` count results

```sparql
PREFIX pathway: <http://togomedium.org/pathway/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT DISTINCT ?ancestor AS ?id ?label ?parent COUNT(?tax_id) AS ?count
FROM <http://togomedium.org/pathway>
{
  VALUES ?types { pathway:Pathway pathway:PathwayVariant }
  {{#if tax_id}}
  ?pathway obo:RO_0002175 taxid:{{tax_id}} .
  {{/if}}
  ?pathway rdf:type ?types .
  ?pathway rdfs:subClassOf* ?ancestor . # tax_id指定時に親を取得するために必要
  ?ancestor rdfs:label ?label .
  ?ancestor rdfs:subClassOf ?parent .
  OPTIONAL {
    ?ancestor obo:RO_0002175 ?tax_id
  }
} ORDER BY ?id
```

## Output

```javascript
({
  json({pathway_list}) {
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
    // 再帰的に辿ってtree構造データを作成
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
    // 不要なプロパティを削除
    function truncate(current_data) {
      if (current_data["children"]) {
        current_data["children"].forEach(child =>{
            truncate(child);
        });
      }
      delete current_data["parent"];
      delete current_data["count"];
    };
  
    
    // 
    let result_pathway_list = pathway_list.results.bindings.map((obj) => parseSparqlObject(obj));
    result_pathway_list.map((obj) => {
       obj["id"] = obj["id"].substring(obj["id"].lastIndexOf('/') + 1);
       obj["parent"] = obj["parent"].substring(obj["parent"].lastIndexOf('/') + 1);
       // 紐づくpathway_idがあれば 1
       obj["num_of_data"] = 0;
       obj["selectable"] = false;
       if (obj["count"] > 0) {
         obj["num_of_data"] = 1;
         obj["selectable"] = true;
       }
    });
    let root_data = {"id": "root", "label": "root", "num_of_data": 0,  "selectable": false };
    retrieve_tree(root_data, result_pathway_list);
    count_num_of_data(root_data);
    truncate(root_data);
    return root_data;
  }
})
```