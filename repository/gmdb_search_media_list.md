# Search media with species and strain counts

Search names and identifiers, taxonomy and inferred collection. Taxonomy filters media only; species and strain counts and sorting always cover all organisms registered to each matching medium. No collection specified does not assert curator origin.

## Parameters

- `name` Case-insensitive literal substring of medium name, GM ID or original ID. Empty means no text filter.
  - default: 
  - example: mrs, M1406, NBRC\_M1
- `taxonomy_id` Up to five comma-separated positive NCBI Taxonomy IDs, combined with AND at medium level. Each ID includes descendants; different strains may satisfy different IDs. Duplicate IDs are equivalent to one. Empty means no filter. Counts always cover the whole medium.
  - default: 
  - example: 1386, 1386,561, 561,562, 83333
- `collection` Inferred collection ID. Empty means Any; none means No collection specified.
  - default: 
  - example: JCM, none
- `sort` Count to sort after aggregating all matching media. Ties: other count descending, then lexical GM ID ascending.
  - default: species\_count
  - example: species\_count, strain\_count
- `order` Sort direction.
  - default: desc
  - example: asc, desc
- `limit` Maximum media per page, 1 to 100.
  - default: 20
  - example: 20, 50, 100
- `offset` Number of matching media to skip, 0 to 9900. The conservative cap keeps offset plus any accepted limit within Virtuoso's 10000-row sorted-page limit.
  - default: 0
  - example: 0, 20, 2925, 9900

## Endpoint

{{SPARQLIST_TOGOMEDIUM_ENDPOINT}}

## `prepared` Validate parameters and select queries

```javascript
(context) => {
  const prepare = (definitions = {}, supplied = {}) => {
  const reserved = new Set(["prepared", "__proto__", "prototype", "constructor"]);
  const validName = (name) =>
    typeof name === "string" && /^[A-Za-z_][A-Za-z0-9_]*$/.test(name) && !reserved.has(name);
  const values = {};
  const literals = {};
  const lists = {};
  const integers = {};
  const aliases = new Set();
  for (const name of Object.keys(supplied)) {
    if (!Object.hasOwn(definitions, name)) throw new Error(`Unknown parameter: ${name}`);
  }
  for (const [name, definition] of Object.entries(definitions)) {
    if (!validName(name)) throw new Error(`Unsupported parameter name: ${name}`);
    const type = definition.type ?? "string";
    if (!["string", "integer", "string-list"].includes(type)) {
      throw new Error(`Unsupported parameter type: ${name}`);
    }
    if (definition.placeholder !== undefined && type !== "string-list") {
      throw new Error(`placeholder requires string-list type: ${name}`);
    }
    const value = Object.hasOwn(supplied, name) ? supplied[name] : definition.default;
    if (
      typeof value !== "string" ||
      (definition.pattern === undefined && type !== "string-list") ||
      (definition.pattern !== undefined &&
        (typeof definition.pattern !== "string" || !new RegExp(definition.pattern).test(value)))
    ) {
      throw new Error(`Invalid parameter: ${name}`);
    }
    values[name] = value;
    if (type === "string-list") {
      const placeholder = definition.placeholder ?? name;
      if (
        !validName(placeholder) ||
        aliases.has(placeholder) ||
        (placeholder !== name && Object.hasOwn(definitions, placeholder))
      ) {
        throw new Error(`Invalid or conflicting placeholder: ${placeholder}`);
      }
      aliases.add(placeholder);
      // JSON escapes used here are also valid in SPARQL double-quoted string literals.
      lists[placeholder] = value
        .split(",")
        .map((item) => JSON.stringify(item.trim()))
        .join(" ");
    } else {
      literals[name] = JSON.stringify(value);
      if (type === "integer") {
        if (
          !Number.isSafeInteger(Number(value)) ||
          Number(value) < 0 ||
          String(Number(value)) !== value
        ) {
          throw new Error(`Invalid integer parameter: ${name}`);
        }
        integers[name] = value;
      }
    }
  }
  return { values, literals, lists, integers };
};
  const select = (file, config = {}, supplied = {}) => {
  const variant = config.queryVariants?.[file];
  if (!variant) return file;
  if (!Object.hasOwn(config.parameters ?? {}, variant.parameter)) {
    throw new Error("Query variant must reference a defined parameter.");
  }
  const selected = supplied[variant.parameter] ?? config.parameters[variant.parameter].default;
  if (!Object.hasOwn(variant.cases ?? {}, selected)) return file;
  const selectedFile = variant.cases[selected];
  if (typeof selectedFile !== "string" || !/^[A-Za-z0-9_-]+\.rq$/.test(selectedFile)) {
    throw new Error("Query variant must be a local .rq filename.");
  }
  return selectedFile;
};
  return ((context, config, prepare, select) => {
  const supplied = Object.fromEntries(
    Object.keys(config.parameters ?? {})
      .filter((name) => Object.hasOwn(context, name))
      .map((name) => [name, context[name]]),
  );
  const prepared = prepare(config.parameters, supplied);
  const variants = Object.fromEntries(
    Object.entries(config.inputs).map(([name, file]) => {
      const selected = select(file, config, supplied);
      return [
        name,
        Object.fromEntries(
          Object.values(config.queryVariants?.[file]?.cases ?? {}).map((candidate, index) => [
            `case${index}`,
            candidate === selected,
          ]),
        ),
      ];
    }),
  );
  return { ...prepared, variants };
})(context, {
  "inputs": {
    "result": "list-media.rq",
    "count": "count-media.rq"
  },
  "parameters": {
    "name": {
      "default": "",
      "pattern": "^[\\s\\S]{0,200}$",
      "description": "Case-insensitive literal substring of medium name, GM ID or original ID. Empty means no text filter.",
      "examples": [
        "mrs",
        "M1406",
        "NBRC_M1"
      ]
    },
    "taxonomy_id": {
      "default": "",
      "type": "string-list",
      "placeholder": "taxonomy_values",
      "pattern": "^(?:[1-9][0-9]{0,19}(?:,[1-9][0-9]{0,19}){0,4})?$",
      "description": "Up to five comma-separated positive NCBI Taxonomy IDs, combined with AND at medium level. Each ID includes descendants; different strains may satisfy different IDs. Duplicate IDs are equivalent to one. Empty means no filter. Counts always cover the whole medium.",
      "examples": [
        "1386",
        "1386,561",
        "561,562",
        "83333"
      ]
    },
    "collection": {
      "default": "",
      "pattern": "^(?:JCM|NBRC|DSMZ|ATCC|NIES|none)?$",
      "description": "Inferred collection ID. Empty means Any; none means No collection specified.",
      "examples": [
        "JCM",
        "none"
      ]
    },
    "sort": {
      "default": "species_count",
      "pattern": "^(?:species_count|strain_count)$",
      "description": "Count to sort after aggregating all matching media. Ties: other count descending, then lexical GM ID ascending.",
      "examples": [
        "species_count",
        "strain_count"
      ]
    },
    "order": {
      "default": "desc",
      "pattern": "^(?:asc|desc)$",
      "description": "Sort direction.",
      "examples": [
        "asc",
        "desc"
      ]
    },
    "limit": {
      "default": "20",
      "type": "integer",
      "pattern": "^(?:[1-9]|[1-9][0-9]|100)$",
      "description": "Maximum media per page, 1 to 100.",
      "examples": [
        "20",
        "50",
        "100"
      ]
    },
    "offset": {
      "default": "0",
      "type": "integer",
      "pattern": "^(?:0|[1-9][0-9]{0,2}|[1-8][0-9]{3}|9[0-8][0-9]{2}|9900)$",
      "description": "Number of matching media to skip, 0 to 9900. The conservative cap keeps offset plus any accepted limit within Virtuoso's 10000-row sorted-page limit.",
      "examples": [
        "0",
        "20",
        "2925",
        "9900"
      ]
    }
  },
  "queryVariants": {
    "list-media.rq": {
      "parameter": "taxonomy_id",
      "cases": {
        "": "list-media-all-taxa.rq"
      }
    },
    "count-media.rq": {
      "parameter": "taxonomy_id",
      "cases": {
        "": "count-media-all-taxa.rq"
      }
    }
  }
}, prepare, select);
}
```

## `result`

```sparql
{{#if prepared.variants.result.case0}}
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
# Generated by build-queries.mjs from the shared collection table; do not edit.
SELECT ?id ?name ?collection_id ?collection_label ?ph ?strain_count ?species_count
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM NAMED <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
{
SELECT ?id (MIN(STR(?raw_name)) AS ?name) (MIN(STR(?raw_ph)) AS ?ph) (MIN(IF(STRSTARTS(COALESCE(STR(?origin), ""), "JCM_"), 0, IF(STRSTARTS(COALESCE(STR(?origin), ""), "NBRC_"), 1, IF(STRSTARTS(COALESCE(STR(?origin), ""), "DSMZ_"), 2, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://www.atcc.org/") || STRSTARTS(COALESCE(STR(?source), ""), "https://www.atcc.org/"), 3, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://mcc.nies.go.jp/") || STRSTARTS(COALESCE(STR(?source), ""), "https://mcc.nies.go.jp/"), 4, 5)))))) AS ?collection_rank)
       (COUNT(DISTINCT ?strain) AS ?strain_count) (COUNT(DISTINCT ?species) AS ?species_count)
WHERE {
  ?medium a gmo:GMO_000001 ; dct:identifier ?id ; rdfs:label ?raw_name ; olo:length ?paragraph_length .
  FILTER(?paragraph_length > 0)
  OPTIONAL { ?medium skos:altLabel ?origin . }
  OPTIONAL { ?medium gmo:GMO_000108 ?source . }
  OPTIONAL { ?medium gmo:ph ?raw_ph . }
  FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?id)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(STR(?raw_name)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(COALESCE(STR(?origin), "")), LCASE({{{prepared.literals.name}}})))

OPTIONAL { ?medium gmo:GMO_000114/gmo:strain_id ?strain . OPTIONAL {
  ?strain gmo:taxon ?taxon .
  GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {
    ?taxon rdfs:subClassOf* ?species . ?species tax:rank tax:Species .
  }
} }
}
GROUP BY ?id
}
VALUES (?collection_rank ?collection_id ?collection_label) {
  (0 "JCM" "JCM")
  (1 "NBRC" "NBRC")
  (2 "DSMZ" "DSMZ")
  (3 "ATCC" "ATCC")
  (4 "NIES" "NIES")
  (5 "none" "No collection specified")
}
FILTER({{{prepared.literals.collection}}} = "" || ?collection_id = {{{prepared.literals.collection}}})
}
ORDER BY
  ASC(IF({{{prepared.literals.sort}}} = "species_count" && {{{prepared.literals.order}}} = "asc", ?species_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "species_count" && {{{prepared.literals.order}}} = "desc", ?species_count, ""))
  ASC(IF({{{prepared.literals.sort}}} = "strain_count" && {{{prepared.literals.order}}} = "asc", ?strain_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "strain_count" && {{{prepared.literals.order}}} = "desc", ?strain_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "species_count", ?strain_count, ?species_count)) ASC(?id)
LIMIT {{{prepared.values.limit}}}
OFFSET {{{prepared.values.offset}}}

{{else}}
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
# Generated by build-queries.mjs from the shared collection table; do not edit.
SELECT ?id ?name ?collection_id ?collection_label ?ph ?strain_count ?species_count
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM NAMED <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
{
SELECT ?id (MIN(STR(?raw_name)) AS ?name) (MIN(STR(?raw_ph)) AS ?ph) (MIN(IF(STRSTARTS(COALESCE(STR(?origin), ""), "JCM_"), 0, IF(STRSTARTS(COALESCE(STR(?origin), ""), "NBRC_"), 1, IF(STRSTARTS(COALESCE(STR(?origin), ""), "DSMZ_"), 2, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://www.atcc.org/") || STRSTARTS(COALESCE(STR(?source), ""), "https://www.atcc.org/"), 3, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://mcc.nies.go.jp/") || STRSTARTS(COALESCE(STR(?source), ""), "https://mcc.nies.go.jp/"), 4, 5)))))) AS ?collection_rank)
       (COUNT(DISTINCT ?strain) AS ?strain_count) (COUNT(DISTINCT ?species) AS ?species_count)
WHERE {
  ?medium a gmo:GMO_000001 ; dct:identifier ?id ; rdfs:label ?raw_name ; olo:length ?paragraph_length .
  FILTER(?paragraph_length > 0)
  OPTIONAL { ?medium skos:altLabel ?origin . }
  OPTIONAL { ?medium gmo:GMO_000108 ?source . }
  OPTIONAL { ?medium gmo:ph ?raw_ph . }
  FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?id)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(STR(?raw_name)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(COALESCE(STR(?origin), "")), LCASE({{{prepared.literals.name}}})))
{
  SELECT ?medium WHERE {
    { SELECT (COUNT(DISTINCT ?input_tax_id) AS ?input_taxon_count) WHERE {
      VALUES ?input_tax_id { {{{prepared.lists.taxonomy_values}}} }
    } }
    VALUES ?required_tax_id { {{{prepared.lists.taxonomy_values}}} }
    ?medium gmo:GMO_000114/gmo:strain_id ?filter_strain .
    ?filter_strain gmo:taxon ?filter_taxon .
    GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {
      ?requested_taxon tax:scientificName ?requested_name .
      ?filter_taxon rdfs:subClassOf* ?requested_taxon .
      FILTER(STR(?requested_taxon) = CONCAT("http://identifiers.org/taxonomy/", ?required_tax_id))
    }
  }
  GROUP BY ?medium ?input_taxon_count
  HAVING(COUNT(DISTINCT ?required_tax_id) = ?input_taxon_count)
}
OPTIONAL { ?medium gmo:GMO_000114/gmo:strain_id ?strain . OPTIONAL {
  ?strain gmo:taxon ?taxon .
  GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {
    ?taxon rdfs:subClassOf* ?species . ?species tax:rank tax:Species .
  }
} }
}
GROUP BY ?id
}
VALUES (?collection_rank ?collection_id ?collection_label) {
  (0 "JCM" "JCM")
  (1 "NBRC" "NBRC")
  (2 "DSMZ" "DSMZ")
  (3 "ATCC" "ATCC")
  (4 "NIES" "NIES")
  (5 "none" "No collection specified")
}
FILTER({{{prepared.literals.collection}}} = "" || ?collection_id = {{{prepared.literals.collection}}})
}
ORDER BY
  ASC(IF({{{prepared.literals.sort}}} = "species_count" && {{{prepared.literals.order}}} = "asc", ?species_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "species_count" && {{{prepared.literals.order}}} = "desc", ?species_count, ""))
  ASC(IF({{{prepared.literals.sort}}} = "strain_count" && {{{prepared.literals.order}}} = "asc", ?strain_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "strain_count" && {{{prepared.literals.order}}} = "desc", ?strain_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "species_count", ?strain_count, ?species_count)) ASC(?id)
LIMIT {{{prepared.values.limit}}}
OFFSET {{{prepared.values.offset}}}

{{/if}}
```

## `count`

```sparql
{{#if prepared.variants.count.case0}}
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
# Generated by build-queries.mjs; same filters as list-media.rq.
SELECT (COUNT(DISTINCT ?medium) AS ?total) ({{{prepared.literals.limit}}} AS ?limit) ({{{prepared.literals.offset}}} AS ?offset)
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM NAMED <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
{
  SELECT ?medium ?id (MIN(STR(?raw_name)) AS ?name) (MIN(STR(?raw_ph)) AS ?ph) (MIN(IF(STRSTARTS(COALESCE(STR(?origin), ""), "JCM_"), 0, IF(STRSTARTS(COALESCE(STR(?origin), ""), "NBRC_"), 1, IF(STRSTARTS(COALESCE(STR(?origin), ""), "DSMZ_"), 2, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://www.atcc.org/") || STRSTARTS(COALESCE(STR(?source), ""), "https://www.atcc.org/"), 3, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://mcc.nies.go.jp/") || STRSTARTS(COALESCE(STR(?source), ""), "https://mcc.nies.go.jp/"), 4, 5)))))) AS ?collection_rank)
  WHERE {
    ?medium a gmo:GMO_000001 ; dct:identifier ?id ; rdfs:label ?raw_name ; olo:length ?paragraph_length .
    FILTER(?paragraph_length > 0)
    OPTIONAL { ?medium skos:altLabel ?origin . }
    OPTIONAL { ?medium gmo:GMO_000108 ?source . }
    OPTIONAL { ?medium gmo:ph ?raw_ph . }
    FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?id)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(STR(?raw_name)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(COALESCE(STR(?origin), "")), LCASE({{{prepared.literals.name}}})))
  } GROUP BY ?medium ?id
}
VALUES (?collection_rank ?collection_id ?collection_label) {
  (0 "JCM" "JCM")
  (1 "NBRC" "NBRC")
  (2 "DSMZ" "DSMZ")
  (3 "ATCC" "ATCC")
  (4 "NIES" "NIES")
  (5 "none" "No collection specified")
}

FILTER({{{prepared.literals.collection}}} = "" || ?collection_id = {{{prepared.literals.collection}}})
}

{{else}}
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
# Generated by build-queries.mjs; same filters as list-media.rq.
SELECT (COUNT(DISTINCT ?medium) AS ?total) ({{{prepared.literals.limit}}} AS ?limit) ({{{prepared.literals.offset}}} AS ?offset)
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/strain>
FROM NAMED <http://togomedium.org/taxonomy/filtered_has_strain>
WHERE {
{
  SELECT ?medium ?id (MIN(STR(?raw_name)) AS ?name) (MIN(STR(?raw_ph)) AS ?ph) (MIN(IF(STRSTARTS(COALESCE(STR(?origin), ""), "JCM_"), 0, IF(STRSTARTS(COALESCE(STR(?origin), ""), "NBRC_"), 1, IF(STRSTARTS(COALESCE(STR(?origin), ""), "DSMZ_"), 2, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://www.atcc.org/") || STRSTARTS(COALESCE(STR(?source), ""), "https://www.atcc.org/"), 3, IF(STRSTARTS(COALESCE(STR(?source), ""), "http://mcc.nies.go.jp/") || STRSTARTS(COALESCE(STR(?source), ""), "https://mcc.nies.go.jp/"), 4, 5)))))) AS ?collection_rank)
  WHERE {
    ?medium a gmo:GMO_000001 ; dct:identifier ?id ; rdfs:label ?raw_name ; olo:length ?paragraph_length .
    FILTER(?paragraph_length > 0)
    OPTIONAL { ?medium skos:altLabel ?origin . }
    OPTIONAL { ?medium gmo:GMO_000108 ?source . }
    OPTIONAL { ?medium gmo:ph ?raw_ph . }
    FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?id)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(STR(?raw_name)), LCASE({{{prepared.literals.name}}})) || CONTAINS(LCASE(COALESCE(STR(?origin), "")), LCASE({{{prepared.literals.name}}})))
  } GROUP BY ?medium ?id
}
VALUES (?collection_rank ?collection_id ?collection_label) {
  (0 "JCM" "JCM")
  (1 "NBRC" "NBRC")
  (2 "DSMZ" "DSMZ")
  (3 "ATCC" "ATCC")
  (4 "NIES" "NIES")
  (5 "none" "No collection specified")
}
{
  SELECT ?medium WHERE {
    { SELECT (COUNT(DISTINCT ?input_tax_id) AS ?input_taxon_count) WHERE {
      VALUES ?input_tax_id { {{{prepared.lists.taxonomy_values}}} }
    } }
    VALUES ?required_tax_id { {{{prepared.lists.taxonomy_values}}} }
    ?medium gmo:GMO_000114/gmo:strain_id ?filter_strain .
    ?filter_strain gmo:taxon ?filter_taxon .
    GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {
      ?requested_taxon tax:scientificName ?requested_name .
      ?filter_taxon rdfs:subClassOf* ?requested_taxon .
      FILTER(STR(?requested_taxon) = CONCAT("http://identifiers.org/taxonomy/", ?required_tax_id))
    }
  }
  GROUP BY ?medium ?input_taxon_count
  HAVING(COUNT(DISTINCT ?required_tax_id) = ?input_taxon_count)
}
FILTER({{{prepared.literals.collection}}} = "" || ?collection_id = {{{prepared.literals.collection}}})
}

{{/if}}
```

## Output

```javascript
({
  json: function json({ result, count }) {
  const integer = (raw, field) => {
    const number = Number(raw);
    if (!/^(?:0|[1-9][0-9]*)$/.test(raw ?? "") || !Number.isSafeInteger(number))
      throw new Error(`Invalid ${field}.`);
    return number;
  };
  if (count.results.bindings.length !== 1) throw new Error("Expected one pagination result.");
  const pagination = count.results.bindings[0];
  const ids = new Set();
  const contents = result.results.bindings.map((row) => {
    const id = row.id.value;
    if (ids.has(id)) throw new Error(`Duplicate medium ${id}.`);
    ids.add(id);
    return {
      id,
      name: row.name.value.trim() ? row.name.value : "(Unnamed medium)",
      collection:
        row.collection_id.value === "none"
          ? null
          : { id: row.collection_id.value, label: row.collection_label.value },
      species_count: integer(row.species_count.value, "species_count"),
      strain_count: integer(row.strain_count.value, "strain_count"),
      ph: row.ph?.value?.trim() ? row.ph.value : null,
    };
  });
  return {
    contents,
    total: integer(pagination.total?.value, "total"),
    limit: integer(pagination.limit?.value, "limit"),
    offset: integer(pagination.offset?.value, "offset"),
  };
}
})
```
