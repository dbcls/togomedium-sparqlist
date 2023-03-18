# List infraspecific taxons by a taxonomy id


## Parameters
fraspecific
* `tax_id`
  * default: 1386
  * example: 2, 2157
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

SELECT  (COUNT(DISTINCT ?tax) AS ?total)  ?limit ?offset
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
FROM <http://growthmedium.org/media/2023>
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
  ?tax ddbj-tax:scientificName ?name ;
    ddbj-tax:rank ?rank_uri .
  ?rank_uri rdfs:label ?rank .
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
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>

SELECT  DISTINCT ?tax ?name ?rank
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
FROM <http://growthmedium.org/media/2023>
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
  ?tax ddbj-tax:scientificName ?name ;
    ddbj-tax:rank ?rank_uri .
  ?rank_uri rdfs:label ?rank .
  FILTER(!REGEX(?name, "Candidatus"))
} ORDER BY ?name
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
    const getIdFromUri = (str) => {
      return str.split("/").pop();
    };
    //
    const info = parseSparqlObject(count.results.bindings[0]);
    const total = !!info ? parseInt(info.total) : 0;
    const offset = !!info ? parseInt(info.offset) : 0;
    const limit = !!info ? parseInt(info.limit) : 0;
    //
    const KEY_ID = "id";
    const KEY_RANK = "rank";
    const KEY_NAME = "name";
    const columns = [
      {key: KEY_ID, label: "TAX ID"},
      {key: KEY_RANK, label: "Rank"},
      {key: KEY_NAME, label: "Name"},
    ];
    const contents = result.results.bindings
      .map((r) => parseSparqlObject(r))
      .map((r) => ({...r, id: getIdFromUri(r.tax)}))
      .map((r) => ({
        [KEY_ID]: {
          label: r.id,
          href: `/taxon/${r.id}`,
        },
        [KEY_RANK]: r.rank,
        [KEY_NAME]: r.name,
      }));
    //
    return {total, offset, limit, contents, columns};
  }
})
```

