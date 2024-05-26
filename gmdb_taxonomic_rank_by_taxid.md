# Get a taxonomic rank by a tax ID

Show information of the taxonomic rank with the given NCBI taxonomy ID.

## Parameters

* `tax_id` NCBI taxID for a rank
  * default: 91061
  * examples: 1239, 186826, 1300, ...

## Endpoint

http://togomedium.org/sparql

## `result` retrieve organism information

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>


SELECT DISTINCT *
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023> 
WHERE {
  taxid:{{tax_id}} dcterms:identifier ?taxid ;
    ddbj-tax:rank ?rank ;
    ddbj-tax:scientificName ?name .
  OPTIONAL {
    taxid:{{tax_id}} rdfs:subClassOf+ ?genus .
    ?genus ddbj-tax:rank ddbj-tax:Genus ;
           rdfs:label ?genus_label ;
           dcterms:identifier ?genus_taxid
  }
  OPTIONAL {
    taxid:{{tax_id}} rdfs:subClassOf+ ?family .
    ?family ddbj-tax:rank ddbj-tax:Family ;
            rdfs:label ?family_label ;
            dcterms:identifier ?family_taxid
  }
  OPTIONAL {
    taxid:{{tax_id}} rdfs:subClassOf+ ?order .
    ?order  ddbj-tax:rank ddbj-tax:Order ;
            rdfs:label ?order_label ;
            dcterms:identifier ?order_taxid .
  }
  OPTIONAL {
    taxid:{{tax_id}} rdfs:subClassOf+ ?class .
    ?class  ddbj-tax:rank ddbj-tax:Class ;
            rdfs:label ?class_label ;
            dcterms:identifier ?class_taxid .
  }
  OPTIONAL {
    taxid:{{tax_id}} rdfs:subClassOf+ ?phylum .
    ?phylum ddbj-tax:rank ddbj-tax:Phylum ;
            rdfs:label ?phylum_label ;
            dcterms:identifier ?phylum_taxid .
  }
  OPTIONAL {
    taxid:{{tax_id}} rdfs:subClassOf+ ?superkingdom .
    ?superkingdom ddbj-tax:rank ddbj-tax:Superkingdom ;
                  rdfs:label ?superkingdom_label ;
                  dcterms:identifier ?superkingdom_taxid .
  }
  OPTIONAL {
    taxid:{{tax_id}} ddbj-tax:authority ?authority_name .
  }
  OPTIONAL {
    taxid:{{tax_id}} ddbj-tax:typeMaterial ?typematerial .
  }
}
```

## Output

```javascript
({
  json({result}) {
    let rows = result.results.bindings ;
    let rank = {} ;

    rank.scientific_name = rows[0].name.value ;
    rank.taxid = rows[0].taxid.value ;
    rank.rank = rows[0].rank.value ;
    if (rows[0].authority_name) {
      rank.authority_name = rows[0].authority_name.value ;
    }
    rank.lineage = [] ;

    let superkingdom = {};
    superkingdom.rank = "superkingdom" ;
    if (rows[0].superkingdom) {
      superkingdom.label = rows[0].superkingdom_label.value ;
      superkingdom.uri = rows[0].superkingdom.value ;
      superkingdom.taxid = rows[0].superkingdom_taxid.value ;
    } else {
      superkingdom.label = "NA" ;
      superkingdom.uri= "NA" ;
      superkingdom.taxid = "NA" ;
    }
    rank.lineage.push(superkingdom) ;

    let phylum = {};
    phylum.rank = "phylum" ;
    if (rows[0].phylum) {
      phylum.label = rows[0].phylum_label.value ;
      phylum.uri = rows[0].phylum.value ;
      phylum.taxid = rows[0].phylum_taxid.value ;
    } else {
      phylum.label = "NA" ;
      phylum.uri= "NA" ;
      phylum.taxid = "NA" ;
    }
    rank.lineage.push(phylum) ;

    let klass = {};
    klass.rank = "class" ;
    if (rows[0].class) {
      klass.label = rows[0].class_label.value ;
      klass.uri = rows[0].class.value ;
      klass.taxid = rows[0].class_taxid.value ;
    } else {
      klass.label = "NA" ;
      klass.uri= "NA" ;
      klass.taxid = "NA" ;
    }
    rank.lineage.push(klass) ;

    let order = {};
    order.rank = "order" ;
    if (rows[0].order) {
      order.label = rows[0].order_label.value ;
      order.uri = rows[0].order.value ;
      order.taxid = rows[0].order_taxid.value ;
    } else {
      order.label = "NA" ;
      order.uri= "NA" ;
      order.taxid = "NA" ;
    }
    rank.lineage.push(order) ;

    let family = {} ;
    family.rank = "family"
    if (rows[0].family) {
      family.label = rows[0].family_label.value ;
      family.uri= rows[0].family.value ;
      family.taxid = rows[0].family_taxid.value ;
    } else {
      family.label = "NA" ;
      family.uri= "NA" ;
      family.taxid = "NA" ;
    }
    rank.lineage.push(family) ;

    let genus = {} ;
    genus.rank = "genus"
    if (rows[0].genus) {
      genus.label = rows[0].genus_label.value ;
      genus.uri= rows[0].genus.value ;
      genus.taxid = rows[0].genus_taxid.value ;
    } else {
      genus.label = "NA" ;
      genus.uri= "NA" ;
      genus.taxid = "NA" ;
    }
    rank.lineage.push(genus) ;

    if (rows[0].typematerial) {
      let type_materials = [] ;
      let other_type_materials = [] ;
      for (let i = 0; i < rows.length; i++) {
        if (rows[i].typematerial) {
         　if (!rows[i].typematerial.value.match(/:/)) {
             type_materials.push(rows[i].typematerial.value);
          }
        }
      };
      type_materials = [...new Set(type_materials)] ;
      rank.type_material = [];
      rank.other_type_material = [];
      for (let i = 0; i < type_materials.length; i++) {

        if (!type_materials[i].match(/\[\[([\w\s]+)\]\]/)) {
          rank.type_material.push({"label": type_materials[i]});
        } else if (type_materials[i].match(/^(.+)\[\[([\w\s]+)\]\]/)) {
          let tmp_label = RegExp.$1.trim();
          rank.other_type_material.push({"label": tmp_label,
                                         "name": RegExp.$2});
        }
      };
    }

    return rank ;
  }
})
```