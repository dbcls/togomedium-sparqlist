# Get strain information by a Strain ID

Strain information with the given TogoMedium Strain ID.

## Parameters

* `strain_id` TogoMedium strainID
  * default: S602
  * examples: S36358(no link to tax), S39940(multiple other strains), S26316(missing family rank)...

## Endpoint

http://growthmedium.org/sparql



## `strain` retrieve organism information

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?strain_id ?strain_name ?other_strain_id ?other_strain_link
FROM <http://growthmedium.org/strain/2023>
WHERE {
  VALUES ?search_strain_id { "{{strain_id}}" }
  ?strain dcterms:identifier ?search_strain_id ;
    rdf:type sio:SIO_010055 ;
    dcterms:identifier ?strain_id ;
    rdfs:label ?strain_name ;
    gmo:origin_strain ?original_strain .
  ?original_strain dcterms:identifier ?other_strain_id ;
    rdfs:seeAlso ?other_strain_link .
}
```

## `tax_name` retrieve organism information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT  ?scientific_name ?taxid ?rank ?authority_name
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain/2023>
WHERE {
  VALUES ?search_strain_id { "{{strain_id}}" }
  ?strain dcterms:identifier ?search_strain_id ;
    rdf:type sio:SIO_010055 ;
    gmo:taxon ?taxon_url .
  ?taxon_url a taxont:Taxon ;
    taxont:scientificName ?scientific_name;
    dcterms:identifier ?taxid ;
    taxont:rank ?rank_uri .
  ?rank_uri rdfs:label ?rank .
  OPTIONAL { ?taxon_url taxont:authority ?authority_name . }
}
```

## `lineage` retrieve organism information

```sparql
PREFIX taxont: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT DISTINCT ?uri ?taxid ?label ?rank
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
FROM <http://growthmedium.org/strain/2023>
WHERE {
  VALUES ?search_strain_id { "{{strain_id}}" }
  ?strain dcterms:identifier ?search_strain_id ;
    rdf:type sio:SIO_010055 ;
    gmo:taxon ?taxon_url .
  ?taxon_url a taxont:Taxon ;
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
  json({strain, tax_name, lineage}) {
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

    if (strain.results.bindings.length == 0) {
      return null;
    }
    console.log(strain.results.bindings)
    let strain_info =  {
      strain_id: parseSparqlObject(strain.results.bindings[0]).strain_id,
      strain_name: parseSparqlObject(strain.results.bindings[0]).strain_name
    }
    strain_info["other_strain_id_list"] = strain.results.bindings.map((obj) => {
      let other_id = parseSparqlObject(obj);
      delete other_id['strain_id'];
      delete other_id['strain_name'];
      return other_id;
    });
    if (tax_name.results.bindings.length == 0) {
      return {"strain": strain_info, "taxonomy": null}
    }
    let organism = parseSparqlObject(tax_name.results.bindings[0]);
    organism["rank"] = organism["rank"].charAt(0).toUpperCase() + organism["rank"].slice(1).toLowerCase(); // capitalize
    const rank_list = ["superkingdom" , "phylum", "class", "order", "family", "genus", "species"] // "strain"を持つデータは無し
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
    return {"strain": strain_info, "taxonomy": organism}
  }
})
```