# Get growth medium by a growth medium ID

Retrieve a growth medium with the given growth medium ID.

## Parameters

* `gm_id` Growth medium ID
  * default: M1470
  * examples: NBRC_M249, M6, JCM_M1, NBRC_M1039, SY1, HM_D00088_mse, ...

## Endpoint

http://togomedium.org/sparql

## `metadata` retrieve medium metadata

```sparql
PREFIX gmo:     <http://purl.jp/bio/10/gmo/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?gm ?name ?original_media_id ?src_url ?ph
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
{
  VALUES ?gm_no { "{{gm_id}}" }
  ?gm (dcterms:identifier | skos:altLabel) ?gm_no ;
    rdfs:label ?media_name ;
    gmo:GMO_000108 ?src_url .
  OPTIONAL {
    ?gm skos:altLabel ?original_media_id .
    FILTER (strStarts(?original_media_id, "JCM") || strStarts(?original_media_id, "NBRC") )
  }
  BIND (if(STR(?media_name) = "", "(Unnamed medium)", ?media_name) AS ?name)
  OPTIONAL { ?gm gmo:ph ?ph }
}
```
## `component_table`retrieve medium component table paragraph

```sparql
DEFINE sql:select-option "order"
PREFIX gm:     <http://togomedium.org/>
PREFIX gmo:     <http://purl.jp/bio/10/gmo/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
PREFIX olo:     <http://purl.org/ontology/olo/core#>
PREFIX sio:     <http://semanticscience.org/resource/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?paragraph_index ?subcomponent_name ?component_name ?volume ?unit ?conc_value ?conc_unit ?gmo ?gmo_id ?label ?property_id ?property ?property_label ?role_id ?role ?role_label ?reference_media_id
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
FROM <http://growthmedium.org/uo>
{
  VALUES ?medium_no { "{{gm_id}}" }
  ?medium (dcterms:identifier | skos:altLabel) ?medium_no ;
    olo:slot ?slot.
  ?slot olo:index ?paragraph_index ;
   olo:item ?component_table .
  ?component_table rdf:type gmo:Component .
  OPTIONAL { ?component_table rdfs:label ?subcomponent_name }
  ?component_table gmo:has_component ?component .
  ?component rdfs:label ?component_name .
  OPTIONAL  {
    ?component sio:SIO_000216/sio:SIO_000300 ?volume ;
      sio:SIO_000216/sio:SIO_000221 ?unit_class .
      ?unit_class <oboInOwl:hasExactSynonym> ?unit .
  }
  OPTIONAL  {
    ?component gmo:has-concentration-value/sio:SIO_000300 ?conc_value ;
      gmo:has-concentration-value/sio:SIO_000221 ?conc_unit_class .
      ?conc_unit_class <oboInOwl:hasExactSynonym> ?conc_unit .
  }
  OPTIONAL  {
    ?component gmo:gmo_id ?gmo .
      ?gmo rdfs:label ?label ;
      dcterms:identifier ?gmo_id .
     FILTER (lang(?label) = "en")
    OPTIONAL {
      ?gmo gmo:GMO_000113 ?property .
      ?property rdfs:label ?property_label .
      ?property dcterms:identifier ?property_id
    }
    OPTIONAL {
      ?gmo gmo:GMO_000112 ?role .
      ?role rdfs:label ?role_label .
      ?role dcterms:identifier ?role_id
      FILTER(LANG(?role_label) = "en")
    }
  }
  OPTIONAL {
    ?component gmo:reference ?reference_paragraph .
    BIND (replace(replace(str(?reference_paragraph), "_[0-9]+$", ""), "http://togomedium.org/medium/", "") AS ?reference_media_id)
  }
} ORDER BY ?paragraph_index
```

## `comment_list` retrieve medium comment paragraph
```sparql
DEFINE sql:select-option "order"
prefix gmo:     <http://purl.jp/bio/10/gmo/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
prefix olo:     <http://purl.org/ontology/olo/core#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?paragraph_index ?comment
FROM <http://growthmedium.org/media/2023>
FROM <http://growthmedium.org/gmo/v0.24>
{
  VALUES ?medium_no { "{{gm_id}}" }
  ?medium (dcterms:identifier | skos:altLabel) ?medium_no ;
    olo:slot ?slot.
  ?slot olo:index ?paragraph_index ;
   olo:item ?paragraph .
  ?paragraph rdf:type gmo:Comment;
    rdfs:comment ?comment .
} ORDER BY ?paragraph_index
```

## Output
```javascript
({
  json({metadata, component_table, comment_list}) {
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
    const reduceComponentParagraphs = (accum, current) => {
      const index = accum.findIndex((item) => item.paragraph_index === current.paragraph_index);
      if (index === -1) {
        accum.push({
          paragraph_index: current.paragraph_index,
          subcomponent_name: current.subcomponent_name,
          items: [processComponentItem(current)],
        });
      } else {
        accum[index].items.push(processComponentItem(current));
      }
      return accum;
    };
    const processComponentItem = (item) => {
      const result = {
        ...item,
        properties: item.property_id
          ? [
            {
              id: item.property_id,
              uri: item.property,
              label: item.property_label,
            },
          ]
          : [],
        roles: item.role_id
          ? [{id: item.role_id, uri: item.role, label: item.role_label}]
          : [],
      };
      delete result.paragraph_index;
      delete result.subcomponent_name;
      delete result.property;
      delete result.property_id;
      delete result.property_label;
      delete result.role;
      delete result.role_id;
      delete result.role_label;
      return result;
    };
    const reduceComponentItems = (accum, current) => {
      const hasGmoId = !!current.gmo_id;
      const index = hasGmoId
        ? accum.findIndex((item) => item.gmo_id === current.gmo_id)
        : -1;
      if (index === -1) {
        accum.push(current);
      } else {
        const target = accum[index];
        if (current.properties.length) {
          const currentPropId = current.properties[0].id;
          if (target.properties.findIndex((prop) => prop.id === currentPropId) === -1) {
            target.properties = [...target.properties, ...current.properties];
          }
        }
        if (current.roles.length) {
          const currentRoleId = current.roles[0].id;
          if (target.roles.findIndex((role) => role.id === currentRoleId) ===
            -1) {
            target.roles = [...target.roles, ...current.roles];
          }
        }
      }
      return accum;
    };
    const meta = parseSparqlObject(metadata.results.bindings[0]);
    const components = component_table.results.bindings
      .map((obj) => parseSparqlObject(obj))
      .reduce((accum, current) => reduceComponentParagraphs(accum, current), [])
      .map((obj) => ({
        ...obj,
        items: obj.items.reduce((accum, current) => reduceComponentItems(accum, current), []),
      }));
    const comments = comment_list.results.bindings.map((obj) => parseSparqlObject(obj));
    return {meta, components, comments};
  }
})
```