# Get an organism by a tax ID

Show information of the organism with the given NCBI taxonomy ID.

## Parameters

* `tax_id` NCBI taxID
  * default: 315405
  * examples: 201174(phylum rank), 246196(strain rank), 266117, 1209989, 543526, 315405, ...

## Endpoint

http://growthmedium.org/sparql

## `tax_name` retrieve organism information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT  ?scientific_name ?taxid ?rank ?authority_name
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
WHERE {
  VALUES ?tax_id { taxid:{{tax_id}} }
  ?tax_id a taxont:Taxon ;
    taxont:scientificName ?scientific_name;
    dcterms:identifier ?taxid ;
    taxont:rank ?rank .
  OPTIONAL { ?tax_id taxont:authority ?authority_name . }
}
```
## `type_material` retrieve organism information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?type_material
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
WHERE {
  VALUES ?tax_id { taxid:{{tax_id}} }
  ?tax_id a taxont:Taxon ;
    taxont:typeMaterial ?type_material .
}
```
## `lineage` retrieve organism information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT DISTINCT ?uri ?taxid ?label ?rank
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
WHERE {
  VALUES ?tax_id { taxid:{{tax_id}} }
  ?tax_id a taxont:Taxon ;
    rdfs:subClassOf* ?uri .
  ?uri taxont:rank ?rank_uri ;
    rdfs:label ?label ;
    dcterms:identifier ?taxid .
  ?rank_uri rdfs:label ?rank .
}
```

## Output
```javascript
({
  json({tax_name, type_material, lineage}) {
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


    let organism = parseSparqlObject(tax_name.results.bindings[0]);
    if (organism === null) {
      return null;
    }
    const rank_list = ["superkingdom" , "phylum", "class", "order", "family", "genus", "species"]
    let lineage_list = lineage.results.bindings.map((obj) => parseSparqlObject(obj));
    organism.lineage = [];
    rank_list.forEach((rank) => {
      let rank_tax_list = lineage_list.filter(lineage_tax => lineage_tax.rank === rank);
      if (rank_tax_list.length > 0) {
        organism.lineage.push(rank_tax_list[0]);
      } else {
        organism.lineage.push({uri: "NA", taxid: "NA",  label: "NA", rank: rank});
      }
    });
    organism.type_material = [];
    organism.other_type_material = [];
    let type_material_list = type_material.results.bindings.map((obj) => parseSparqlObject(obj));
    type_material_list.forEach((row) => {
      if (!row.type_material.match(/\[\[([\w\s\()]+)]]/)) {
        organism.type_material.push({"label": row.type_material});
      } else if (row.type_material.match(/^(.+)\[\[([\w\s\()]+)]]/)) {
        let tmp_label = RegExp.$1.trim();
        organism.other_type_material.push({"label": tmp_label,"name": RegExp.$2});
      }
    });
    return organism
  }
})
```