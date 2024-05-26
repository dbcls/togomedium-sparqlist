# List strainss by a taxonomy id

## Parameters
* `tax_id`
  * default: 1386
  * example: 315405, 2, 2157
* `limit` limit
  * default: 10
* `offset` offset
  * default: 0

## Endpoint

http://togomedium.org/sparql

## `count`

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT  (COUNT(DISTINCT ?strain) AS ?total)  ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
FROM <http://togomedium.org/media>
FROM <http://growthmedium.org/strain/2023>
WHERE {
  VALUES ?search_tax_id { taxid:{{tax_id}} }
  ?search_tax_id rdf:type ddbj-tax:Taxon .
  ?infraxpecific_tax rdfs:subClassOf* ?search_tax_id .
  ?infraxpecific_tax ddbj-tax:rank ddbj-tax:Species .
  ?tax rdfs:subClassOf* ?infraxpecific_tax .
  ?strain gmo:taxon ?tax .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 . #exist media
  ?tax ddbj-tax:scientificName ?name .
  FILTER(!REGEX(?name, "Candidatus"))
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## `result`

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT  DISTINCT ?strain_id ?strain_name
 (GROUP_CONCAT(DISTINCT ?original_strain_id; SEPARATOR = ", ") AS ?original_strain_ids)
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
FROM <http://togomedium.org/media>
FROM <http://growthmedium.org/strain/2023>
WHERE {
  VALUES ?search_tax_id { taxid:{{tax_id}} }
  ?search_tax_id rdf:type ddbj-tax:Taxon .
  ?infraxpecific_tax rdfs:subClassOf* ?search_tax_id .
  ?infraxpecific_tax ddbj-tax:rank ddbj-tax:Species .
  ?tax rdfs:subClassOf* ?infraxpecific_tax .
  ?strain gmo:taxon ?tax ;
    rdfs:label ?strain_name ;
    dcterms:identifier ?strain_id ;
    gmo:origin_strain/dcterms:identifier ?original_strain_id .
  ?culture_for gmo:strain_id ?strain .
  ?medium gmo:GMO_000114 ?culture_for ;
    rdf:type  gmo:GMO_000001 . #exist media
  ?tax ddbj-tax:scientificName ?name .
  FILTER(!REGEX(?name, "Candidatus"))
} GROUP BY ?strain_id ?strain_name
ORDER BY ?strain_name
LIMIT {{limit}}
OFFSET {{offset}}
```

## Output

```javascript
({
  json({result, count}) {
    const parseSparqlObject = (obj) => {
      const result = {};
      try {
        Object.entries(obj).forEach(([key, item]) => {
          result[key] = item["value"];
        });
      } catch (e) {
      }
      return Object.entries(result).length ? result : null;
    };
    //
    const info = parseSparqlObject(count.results.bindings[0]);
    const total = !!info ? parseInt(info.total) : 0;
    const offset = !!info ? parseInt(info.offset) : 0;
    const limit = !!info ? parseInt(info.limit) : 0;
    //
    const KEY_ID = "id";
    const KEY_NAME = "name";
    const KEY_OTHER_IDS = "other_ids";
    const columns = [
      {key: KEY_ID, label: "Strain ID"},
      {key: KEY_NAME, label: "Name"},
      {key: KEY_OTHER_IDS, label: "Other IDs"},
    ];
    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((r) => ({
        [KEY_ID]: {
          label: r.strain_id,
          href: `/strain/${r.strain_id}`,
        },
        [KEY_NAME]: r.strain_name,
        [KEY_OTHER_IDS]: r.original_strain_ids,
      }));
    //
    return {total, offset, limit, contents, columns};
  }
})
```

