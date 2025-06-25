# Get  media and strain list by multiple media ids

## Parameters
* `gm_ids` list of medium id
  * default: M2794,M941
  * examples: SY4047,JCM_M900

## Endpoint
{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

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
## `result` retrieve media
```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX tax:  <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT DISTINCT ?medium_id ?original_media_id ?medium_name ?strain_id ?strain_name ?tax ?tax_name ?ancestor_tax ?ancestor_tax_name ?rank
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
  VALUES ?medium_no { {{media_values}} }
  VALUES ?rank { tax:Superkingdom  tax:Phylum tax:Class tax:Order tax:Family tax:Genus tax:Species }
  ?medium (dcterms:identifier | skos:altLabel) ?medium_no ;
    dcterms:identifier ?medium_id ;
    skos:altLabel ?original_media_id ;
    rdfs:label ?name ;
    gmo:GMO_000114/gmo:strain_id ?strain .
  ?strain a sio:SIO_010055 ;
    rdfs:label ?strain_name ;
    dcterms:identifier ?strain_id ;
    gmo:taxon ?tax .
  ?tax rdfs:label ?tax_name ;
    rdfs:subClassOf* ?ancestor_tax .
  ?ancestor_tax tax:rank  ?rank ;
    rdfs:label ?ancestor_tax_name .
  BIND (if(STR(?name) = "", "(Unnamed medium)",  ?name) AS ?medium_name)
} ORDER BY ?tax ?rank
```
## Output

```javascript
({
  json({result}) {
    const lineageRanks = ["superkingdom","phylum","class","order","family","genus","species","strain"];
    const output = [];
    result.results.bindings.forEach(row => {
        const existingMedium = output.find(item => item.gm_id === row.medium_id.value);
        const medium = existingMedium || {};
        if(!existingMedium) {
            medium.gm_id = row.medium_id.value;
            medium.label = row.medium_name.value;
            medium.original_media_id = row.original_media_id.value;
            medium.organisms = [];
            output.push(medium);
        }
        const existingOrganism = medium.organisms.find(o => o.strain.id === row.strain_id.value);
        const organism = existingOrganism || lineageRanks.reduce((accum, current) => {
            return current === "strain" ? {
                ...accum,
                strain: {id: row.strain_id.value, label: row.strain_name.value}
            } : {...accum, [current]: null}
        }, {})
        const rank = row.rank.value.split("/").pop().toLowerCase();
        if(rank !== "strain"){
          organism[rank] = {
			id: row.ancestor_tax.value.split("/").pop(),
			label: row.ancestor_tax_name.value
          }
        }
        if(!existingOrganism) {
            medium.organisms.push(organism)
        }
    })
    return output;
  }
})
```
