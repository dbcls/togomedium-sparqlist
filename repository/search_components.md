# Search components

Search components and return conditional Role and Property facet counts.

## Parameters

- `name` Case-insensitive literal substring of a preferred or alternative name. Empty means no name filter.
  - default: 
  - example: glucose, Dextrose
- `role_id` Role GMO ID, including all descendant Roles. Empty means no Role filter. Role facet counts ignore this parameter.
  - default: 
  - example: GMO\_000042
- `property_id` Directly assigned Property GMO ID. Empty means no Property filter. Property facet counts ignore this parameter.
  - default: 
  - example: GMO\_000050
- `sort` Sort key: name for the preferred label, id for the GMO ID, or medium\_count for the number of media whose recipes directly include the component.
  - default: medium\_count
  - example: name, id, medium\_count
- `order` Sort direction: asc for ascending or desc for descending.
  - default: desc
  - example: asc, desc
- `limit` Maximum number of components to return. Use a non-negative safe integer; 0 returns an empty list.
  - default: 20
  - example: 20, 0
- `offset` Number of components to skip. Use a non-negative safe integer.
  - default: 0
  - example: 0, 20

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
    "result": "list-components-with-properties.rq",
    "count": "count-components.rq",
    "roles": "count-components-by-role.rq",
    "properties": "count-components-by-property.rq"
  },
  "parameters": {
    "name": {
      "default": "",
      "pattern": "^[\\s\\S]*$",
      "description": "Case-insensitive literal substring of a preferred or alternative name. Empty means no name filter.",
      "examples": [
        "glucose",
        "Dextrose"
      ]
    },
    "role_id": {
      "default": "",
      "pattern": "^(?:GMO_[0-9]{6})?$",
      "description": "Role GMO ID, including all descendant Roles. Empty means no Role filter. Role facet counts ignore this parameter.",
      "examples": [
        "GMO_000042"
      ]
    },
    "property_id": {
      "default": "",
      "pattern": "^(?:GMO_[0-9]{6})?$",
      "description": "Directly assigned Property GMO ID. Empty means no Property filter. Property facet counts ignore this parameter.",
      "examples": [
        "GMO_000050"
      ]
    },
    "sort": {
      "default": "medium_count",
      "pattern": "^(?:name|medium_count|id)$",
      "description": "Sort key: name for the preferred label, id for the GMO ID, or medium_count for the number of media whose recipes directly include the component.",
      "examples": [
        "name",
        "id",
        "medium_count"
      ]
    },
    "order": {
      "default": "desc",
      "pattern": "^(?:asc|desc)$",
      "description": "Sort direction: asc for ascending or desc for descending.",
      "examples": [
        "asc",
        "desc"
      ]
    },
    "limit": {
      "type": "integer",
      "default": "20",
      "pattern": "^(?:0|[1-9][0-9]*)$",
      "description": "Maximum number of components to return. Use a non-negative safe integer; 0 returns an empty list.",
      "examples": [
        "20",
        "0"
      ]
    },
    "offset": {
      "type": "integer",
      "default": "0",
      "pattern": "^(?:0|[1-9][0-9]*)$",
      "description": "Number of components to skip. Use a non-negative safe integer.",
      "examples": [
        "0",
        "20"
      ]
    }
  },
  "queryVariants": {
    "list-components-with-properties.rq": {
      "parameter": "sort",
      "cases": {
        "medium_count": "list-components-by-medium-count.rq"
      }
    }
  }
}, prepare, select);
}
```

## `result`

```sparql
{{#if prepared.variants.result.case0}}
# Select one label per component; paginate before expanding properties and roles.
# Pagination parameters: limit (default 20), offset (default 0).
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT ?gmo_id ?component ?label ?alias ?matched_name ?medium_count
       ?property ?property_id ?property_label_en
       ?role ?role_id ?role_label_en ?role_parent ?role_parent_id
FROM <http://togomedium.org/gmo>
FROM NAMED <http://togomedium.org/media>
WHERE {
  {
    SELECT ?gmo_id ?component ?label
           (COUNT(DISTINCT ?medium) AS ?medium_count)
    WHERE {
      {
        SELECT ?gmo_id (?gmo AS ?component) (STR(?l) AS ?label)
        WHERE {
          ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
               dcterms:identifier ?gmo_id ;
               skos:prefLabel ?l .
          FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
          FILTER({{{prepared.literals.name}}} = "" || EXISTS {
            ?gmo (skos:prefLabel|skos:altLabel) ?search_label .
            FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
          })
          FILTER({{{prepared.literals.role_id}}} = "" || EXISTS {
            ?gmo gmo:GMO_000112 ?assigned_filter_role .
            ?assigned_filter_role rdfs:subClassOf* ?filter_role .
            ?filter_role rdfs:subClassOf+ gmo:GMO_000037 ;
                         dcterms:identifier {{{prepared.literals.role_id}}} .
          })
          FILTER({{{prepared.literals.property_id}}} = "" || EXISTS {
            ?gmo gmo:GMO_000113 ?filter_property .
            ?filter_property rdfs:subClassOf gmo:GMO_000039 ;
                             dcterms:identifier {{{prepared.literals.property_id}}} .
          })
          # Prefer English, then the lexically first label and language tag.
          FILTER NOT EXISTS {
            ?gmo skos:prefLabel ?other_label .
            FILTER(
              (LANGMATCHES(LANG(?other_label), "en") && !LANGMATCHES(LANG(?l), "en")) ||
              (LANGMATCHES(LANG(?other_label), "en") = LANGMATCHES(LANG(?l), "en") &&
                (STR(?other_label) < STR(?l) ||
                 (STR(?other_label) = STR(?l) && LANG(?other_label) < LANG(?l))))
            )
          }

        }
        GROUP BY ?gmo_id ?gmo ?l
      }
      OPTIONAL {
        GRAPH <http://togomedium.org/media> {
          ?medium olo:slot/olo:item ?component_table .
          ?component_table rdf:type gmo:Component ;
                           gmo:has_component ?recipe_component .
          ?recipe_component gmo:gmo_id ?component .
        }
      }
    }
    GROUP BY ?gmo_id ?component ?label
    ORDER BY
      ASC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "asc", ?label, ""))
      DESC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "desc", ?label, ""))
      ASC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "asc", ?gmo_id, ""))
      DESC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "desc", ?gmo_id, ""))
      ASC(IF({{{prepared.literals.sort}}} = "medium_count" && {{{prepared.literals.order}}} = "asc", COUNT(DISTINCT ?medium), ""))
      DESC(IF({{{prepared.literals.sort}}} = "medium_count" && {{{prepared.literals.order}}} = "desc", COUNT(DISTINCT ?medium), ""))
      ?gmo_id
    LIMIT {{{prepared.values.limit}}}
    OFFSET {{{prepared.values.offset}}}
  }
  OPTIONAL {
    {
      ?component gmo:GMO_000113 ?property .
      ?property dcterms:identifier ?property_id ;
                rdfs:label ?property_label_en .
      FILTER(LANG(?property_label_en) = "en")
    }
    UNION
    { ?component skos:altLabel ?alias . }
    UNION
    {
      FILTER({{{prepared.literals.name}}} != "")
      ?component (skos:prefLabel|skos:altLabel) ?matched_name .
      FILTER(CONTAINS(LCASE(STR(?matched_name)), LCASE({{{prepared.literals.name}}})))
    }
    UNION
    {
      ?component gmo:GMO_000112 ?role .
      ?role dcterms:identifier ?role_id ;
            rdfs:label ?role_label_en .
      FILTER(LANG(?role_label_en) = "en")
      OPTIONAL {
        ?role rdfs:subClassOf ?role_parent .
        ?role_parent rdfs:subClassOf* gmo:GMO_000037 .
        OPTIONAL { ?role_parent dcterms:identifier ?role_parent_id . }
      }
    }
  }
}
ORDER BY
  ASC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "asc", ?label, ""))
  DESC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "desc", ?label, ""))
  ASC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "asc", ?gmo_id, ""))
  DESC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "desc", ?gmo_id, ""))
  ASC(IF({{{prepared.literals.sort}}} = "medium_count" && {{{prepared.literals.order}}} = "asc", ?medium_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "medium_count" && {{{prepared.literals.order}}} = "desc", ?medium_count, ""))
  ?gmo_id
  ?property_id ?property_label_en ?role_id ?role_label_en ?alias ?matched_name

{{else}}
# Select one label per component; paginate before expanding properties and roles.
# Pagination parameters: limit (default 20), offset (default 0).
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT ?gmo_id ?component ?label ?alias ?matched_name ?medium_count
       ?property ?property_id ?property_label_en
       ?role ?role_id ?role_label_en ?role_parent ?role_parent_id
FROM <http://togomedium.org/gmo>
FROM NAMED <http://togomedium.org/media>
WHERE {
  {
    SELECT ?gmo_id ?component ?label
           (COUNT(DISTINCT ?medium) AS ?medium_count)
    WHERE {
      {
        SELECT ?gmo_id (?gmo AS ?component) (STR(?l) AS ?label)
        WHERE {
          ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
               dcterms:identifier ?gmo_id ;
               skos:prefLabel ?l .
          FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
          FILTER({{{prepared.literals.name}}} = "" || EXISTS {
            ?gmo (skos:prefLabel|skos:altLabel) ?search_label .
            FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
          })
          FILTER({{{prepared.literals.role_id}}} = "" || EXISTS {
            ?gmo gmo:GMO_000112 ?assigned_filter_role .
            ?assigned_filter_role rdfs:subClassOf* ?filter_role .
            ?filter_role rdfs:subClassOf+ gmo:GMO_000037 ;
                         dcterms:identifier {{{prepared.literals.role_id}}} .
          })
          FILTER({{{prepared.literals.property_id}}} = "" || EXISTS {
            ?gmo gmo:GMO_000113 ?filter_property .
            ?filter_property rdfs:subClassOf gmo:GMO_000039 ;
                             dcterms:identifier {{{prepared.literals.property_id}}} .
          })
          # Prefer English, then the lexically first label and language tag.
          FILTER NOT EXISTS {
            ?gmo skos:prefLabel ?other_label .
            FILTER(
              (LANGMATCHES(LANG(?other_label), "en") && !LANGMATCHES(LANG(?l), "en")) ||
              (LANGMATCHES(LANG(?other_label), "en") = LANGMATCHES(LANG(?l), "en") &&
                (STR(?other_label) < STR(?l) ||
                 (STR(?other_label) = STR(?l) && LANG(?other_label) < LANG(?l))))
            )
          }

        }
        GROUP BY ?gmo_id ?gmo ?l
        ORDER BY
          ASC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "asc", STR(?l), ""))
          DESC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "desc", STR(?l), ""))
          ASC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "asc", ?gmo_id, ""))
          DESC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "desc", ?gmo_id, ""))
          ?gmo_id
        LIMIT {{{prepared.values.limit}}}
        OFFSET {{{prepared.values.offset}}}
      }
      OPTIONAL {
        GRAPH <http://togomedium.org/media> {
          ?medium olo:slot/olo:item ?component_table .
          ?component_table rdf:type gmo:Component ;
                           gmo:has_component ?recipe_component .
          ?recipe_component gmo:gmo_id ?component .
        }
      }
    }
    GROUP BY ?gmo_id ?component ?label
  }
  OPTIONAL {
    {
      ?component gmo:GMO_000113 ?property .
      ?property dcterms:identifier ?property_id ;
                rdfs:label ?property_label_en .
      FILTER(LANG(?property_label_en) = "en")
    }
    UNION
    { ?component skos:altLabel ?alias . }
    UNION
    {
      FILTER({{{prepared.literals.name}}} != "")
      ?component (skos:prefLabel|skos:altLabel) ?matched_name .
      FILTER(CONTAINS(LCASE(STR(?matched_name)), LCASE({{{prepared.literals.name}}})))
    }
    UNION
    {
      ?component gmo:GMO_000112 ?role .
      ?role dcterms:identifier ?role_id ;
            rdfs:label ?role_label_en .
      FILTER(LANG(?role_label_en) = "en")
      OPTIONAL {
        ?role rdfs:subClassOf ?role_parent .
        ?role_parent rdfs:subClassOf* gmo:GMO_000037 .
        OPTIONAL { ?role_parent dcterms:identifier ?role_parent_id . }
      }
    }
  }
}
ORDER BY
  ASC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "asc", ?label, ""))
  DESC(IF({{{prepared.literals.sort}}} = "name" && {{{prepared.literals.order}}} = "desc", ?label, ""))
  ASC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "asc", ?gmo_id, ""))
  DESC(IF({{{prepared.literals.sort}}} = "id" && {{{prepared.literals.order}}} = "desc", ?gmo_id, ""))
  ASC(IF({{{prepared.literals.sort}}} = "medium_count" && {{{prepared.literals.order}}} = "asc", ?medium_count, ""))
  DESC(IF({{{prepared.literals.sort}}} = "medium_count" && {{{prepared.literals.order}}} = "desc", ?medium_count, ""))
  ?gmo_id
  ?property_id ?property_label_en ?role_id ?role_label_en ?alias ?matched_name

{{/if}}
```

## `count`

```sparql
# Count all matching components, with the same filters as the list, independently of pagination.
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?gmo_id) AS ?total) ({{{prepared.literals.limit}}} AS ?limit) ({{{prepared.literals.offset}}} AS ?offset)
FROM <http://togomedium.org/gmo>
WHERE {
  ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
       dcterms:identifier ?gmo_id ;
       skos:prefLabel ?label .
  FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
  FILTER({{{prepared.literals.name}}} = "" || EXISTS {
    ?gmo (skos:prefLabel|skos:altLabel) ?search_label .
    FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
  })
  FILTER({{{prepared.literals.role_id}}} = "" || EXISTS {
    ?gmo gmo:GMO_000112 ?assigned_filter_role .
    ?assigned_filter_role rdfs:subClassOf* ?filter_role .
    ?filter_role rdfs:subClassOf+ gmo:GMO_000037 ;
                 dcterms:identifier {{{prepared.literals.role_id}}} .
  })
  FILTER({{{prepared.literals.property_id}}} = "" || EXISTS {
    ?gmo gmo:GMO_000113 ?filter_property .
    ?filter_property rdfs:subClassOf gmo:GMO_000039 ;
                     dcterms:identifier {{{prepared.literals.property_id}}} .
  })
}
```

## `roles`

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT ?role ?id ?label ?parent ?parent_id (COUNT(DISTINCT ?gmo_id) AS ?count)
FROM <http://togomedium.org/gmo>
WHERE {
  ?role rdfs:subClassOf+ gmo:GMO_000037 ; dcterms:identifier ?id ; rdfs:label ?label .
  FILTER(LANG(?label) = "en")
  FILTER(REGEX(STR(?id), "^GMO_[0-9]{6}$"))
  OPTIONAL {
    ?role rdfs:subClassOf ?parent .
    ?parent rdfs:subClassOf* gmo:GMO_000037 .
    OPTIONAL { ?parent dcterms:identifier ?parent_id . }
  }
  OPTIONAL {
    ?component rdfs:subClassOf+ gmo:GMO_000002 ;
               dcterms:identifier ?gmo_id ; skos:prefLabel ?preferred_label .
    ?assigned_role rdfs:subClassOf* ?role .
    ?component gmo:GMO_000112 ?assigned_role .
    FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
    FILTER({{{prepared.literals.name}}} = "" || EXISTS {
      ?component (skos:prefLabel|skos:altLabel) ?search_label .
      FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
    })
    FILTER({{{prepared.literals.property_id}}} = "" || EXISTS {
      ?component gmo:GMO_000113 ?filter_property .
      ?filter_property rdfs:subClassOf gmo:GMO_000039 ;
                       dcterms:identifier {{{prepared.literals.property_id}}} .
    })
  }
}
GROUP BY ?role ?id ?label ?parent ?parent_id
ORDER BY ?label ?id
```

## `properties`

```sparql
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT ?property ?id ?label (COUNT(DISTINCT ?gmo_id) AS ?count)
FROM <http://togomedium.org/gmo>
WHERE {
  ?property rdfs:subClassOf gmo:GMO_000039 ; dcterms:identifier ?id ; rdfs:label ?label .
  FILTER(LANG(?label) = "en")
  FILTER(REGEX(STR(?id), "^GMO_[0-9]{6}$"))
  OPTIONAL {
    ?component rdfs:subClassOf+ gmo:GMO_000002 ;
               dcterms:identifier ?gmo_id ; skos:prefLabel ?preferred_label .
    ?component gmo:GMO_000113 ?property .
    FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
    FILTER({{{prepared.literals.name}}} = "" || EXISTS {
      ?component (skos:prefLabel|skos:altLabel) ?search_label .
      FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
    })
    FILTER({{{prepared.literals.role_id}}} = "" || EXISTS {
      ?component gmo:GMO_000112 ?assigned_filter_role .
      ?assigned_filter_role rdfs:subClassOf* ?filter_role .
      ?filter_role rdfs:subClassOf+ gmo:GMO_000037 ;
                   dcterms:identifier {{{prepared.literals.role_id}}} .
    })
  }
}
GROUP BY ?property ?id ?label
ORDER BY ?label ?id
```

## Output

```javascript
({
  json: function json({ result, count, roles, properties }) {
  const pagination = count.results.bindings[0];
  if (!pagination) throw new Error("Count result is missing.");

  const components = new Map();
  const parents = new Map();
  for (const row of result.results.bindings) {
    const id = row.gmo_id.value;
    if (!components.has(id)) {
      components.set(id, {
        id,
        name: row.label.value,
        aliases: [],
        matched_names: [],
        medium_count: Number(row.medium_count?.value ?? 0),
        properties: [],
        roles: [],
      });
    }

    if (row.role_id && row.role_parent) {
      const key = row.role_id.value;
      const previous = parents.get(key);
      if (previous && previous.uri !== row.role_parent.value) {
        throw new Error(`Multiple parents found for Role ${key}.`);
      }
      const parent = previous ?? { uri: row.role_parent.value, id: null };
      if (row.role_parent_id) parent.id = row.role_parent_id.value;
      parents.set(key, parent);
    }
    const component = components.get(id);
    if (row.alias && !component.aliases.includes(row.alias.value)) {
      component.aliases.push(row.alias.value);
    }
    if (row.matched_name && !component.matched_names.includes(row.matched_name.value)) {
      component.matched_names.push(row.matched_name.value);
    }
    for (const [key, idKey, labelKey] of [
      ["properties", "property_id", "property_label_en"],
      ["roles", "role_id", "role_label_en"],
    ]) {
      if (!row[idKey] || !row[labelKey]) continue;
      const item = { gmo_id: row[idKey].value, label_en: row[labelKey].value };
      if (
        !component[key].some(
          (existing) => existing.gmo_id === item.gmo_id && existing.label_en === item.label_en,
        )
      ) {
        component[key].push(item);
      }
    }
  }

  for (const component of components.values()) {
    for (const role of component.roles) {
      const parent = parents.get(role.gmo_id);
      role.parent =
        !parent || parent.uri === "http://purl.jp/bio/10/gmo/GMO_000037" ? null : parent.id;
    }
  }

  const facet = (bindings, isRole) => {
    const items = new Map();
    const facetParents = new Map();
    for (const row of bindings) {
      const id = row.id.value;
      const count = Number(row.count.value);
      if (!/^(?:0|[1-9][0-9]*)$/.test(row.count.value) || !Number.isSafeInteger(count)) {
        throw new Error(`Invalid facet count for ${id}.`);
      }
      const key = `${id}\u0000${row.label.value}`;
      const previous = items.get(key);
      if (previous && previous.count !== count) throw new Error(`Conflicting counts for ${id}.`);
      const item = previous ?? { gmo_id: id, label_en: row.label.value, count };
      if (isRole) {
        if (row.parent) {
          const previousParent = facetParents.get(id);
          if (previousParent && previousParent !== row.parent.value) {
            throw new Error(`Multiple parents found for Role ${id}.`);
          }
          facetParents.set(id, row.parent.value);
        }
        item.parent =
          !row.parent || row.parent.value === "http://purl.jp/bio/10/gmo/GMO_000037"
            ? null
            : (row.parent_id?.value ?? null);
      }
      items.set(key, item);
    }
    return [...items.values()];
  };

  return {
    contents: [...components.values()],
    // Preserve the original API's string-valued pagination fields.
    total: pagination.total.value,
    limit: pagination.limit.value,
    offset: pagination.offset.value,
    facets: {
      roles: facet(roles.results.bindings, true),
      properties: facet(properties.results.bindings, false),
    },
  };
}
})
```
