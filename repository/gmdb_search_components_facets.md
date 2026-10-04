# Search component facets

Return Role and Property options with conditional counts, excluding the selected filter of each facet. No pagination or sorting.

## Parameters

- `name` Case-insensitive literal substring of an all-language preferred/alternative name or GMO ID. Empty means no search filter.
  - default: 
  - example: glucose, GMO\_001009, 001009
- `role_id` Role GMO ID, including all descendant Roles. Empty means no Role filter. Role facet counts ignore this parameter. none selects components without any assignment of the classification predicate, independent of labels.
  - default: 
  - example: GMO\_000042, none
- `property_id` Directly assigned Property GMO ID. Empty means no Property filter. Property facet counts ignore this parameter. none selects components without any assignment of the classification predicate, independent of labels.
  - default: 
  - example: GMO\_000050, none

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
    "roles": "count-components-by-role.rq",
    "properties": "count-components-by-property.rq",
    "role_none": "count-components-without-role.rq",
    "property_none": "count-components-without-property.rq"
  },
  "parameters": {
    "name": {
      "default": "",
      "pattern": "^[\\s\\S]*$",
      "description": "Case-insensitive literal substring of an all-language preferred/alternative name or GMO ID. Empty means no search filter.",
      "examples": [
        "glucose",
        "GMO_001009",
        "001009"
      ]
    },
    "role_id": {
      "default": "",
      "pattern": "^(?:GMO_[0-9]{6}|none)?$",
      "description": "Role GMO ID, including all descendant Roles. Empty means no Role filter. Role facet counts ignore this parameter. none selects components without any assignment of the classification predicate, independent of labels.",
      "examples": [
        "GMO_000042",
        "none"
      ]
    },
    "property_id": {
      "default": "",
      "pattern": "^(?:GMO_[0-9]{6}|none)?$",
      "description": "Directly assigned Property GMO ID. Empty means no Property filter. Property facet counts ignore this parameter. none selects components without any assignment of the classification predicate, independent of labels.",
      "examples": [
        "GMO_000050",
        "none"
      ]
    }
  }
}, prepare, select);
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
    FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?gmo_id)), LCASE({{{prepared.literals.name}}})) || EXISTS {
      ?component (skos:prefLabel|skos:altLabel) ?search_label .
      FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
    })
    FILTER({{{prepared.literals.property_id}}} = "" || ({{{prepared.literals.property_id}}} = "none" && NOT EXISTS { ?component gmo:GMO_000113 ?missing_assignment . }) || ({{{prepared.literals.property_id}}} != "none" && EXISTS {
      ?component gmo:GMO_000113 ?filter_property .
      ?filter_property rdfs:subClassOf gmo:GMO_000039 ;
                       dcterms:identifier {{{prepared.literals.property_id}}} .
    }))
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
    FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?gmo_id)), LCASE({{{prepared.literals.name}}})) || EXISTS {
      ?component (skos:prefLabel|skos:altLabel) ?search_label .
      FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
    })
    FILTER({{{prepared.literals.role_id}}} = "" || ({{{prepared.literals.role_id}}} = "none" && NOT EXISTS { ?component gmo:GMO_000112 ?missing_assignment . }) || ({{{prepared.literals.role_id}}} != "none" && EXISTS {
      ?component gmo:GMO_000112 ?assigned_filter_role .
      ?assigned_filter_role rdfs:subClassOf* ?filter_role .
      ?filter_role rdfs:subClassOf+ gmo:GMO_000037 ;
                   dcterms:identifier {{{prepared.literals.role_id}}} .
    }))
  }
}
GROUP BY ?property ?id ?label
ORDER BY ?label ?id
```

## `role_none`

```sparql
# Count all matching components, with the same filters as the list, independently of pagination.
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?gmo_id) AS ?count)
FROM <http://togomedium.org/gmo>
WHERE {
  ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
       dcterms:identifier ?gmo_id ;
       skos:prefLabel ?label .
  FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
  FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?gmo_id)), LCASE({{{prepared.literals.name}}})) || EXISTS {
    ?gmo (skos:prefLabel|skos:altLabel) ?search_label .
    FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
  })
  FILTER({{{prepared.literals.property_id}}} = "" || ({{{prepared.literals.property_id}}} = "none" && NOT EXISTS { ?gmo gmo:GMO_000113 ?missing_assignment . }) || ({{{prepared.literals.property_id}}} != "none" && EXISTS {
    ?gmo gmo:GMO_000113 ?filter_property .
    ?filter_property rdfs:subClassOf gmo:GMO_000039 ;
                     dcterms:identifier {{{prepared.literals.property_id}}} .
  }))
  FILTER NOT EXISTS { ?gmo gmo:GMO_000112 ?assignment . }
}
```

## `property_none`

```sparql
# Count all matching components, with the same filters as the list, independently of pagination.
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX gmo: <http://purl.jp/bio/10/gmo/>

SELECT (COUNT(DISTINCT ?gmo_id) AS ?count)
FROM <http://togomedium.org/gmo>
WHERE {
  ?gmo rdfs:subClassOf+ gmo:GMO_000002 ;
       dcterms:identifier ?gmo_id ;
       skos:prefLabel ?label .
  FILTER(REGEX(STR(?gmo_id), "^GMO_[0-9]{6}$"))
  FILTER({{{prepared.literals.name}}} = "" || CONTAINS(LCASE(STR(?gmo_id)), LCASE({{{prepared.literals.name}}})) || EXISTS {
    ?gmo (skos:prefLabel|skos:altLabel) ?search_label .
    FILTER(CONTAINS(LCASE(STR(?search_label)), LCASE({{{prepared.literals.name}}})))
  })
  FILTER({{{prepared.literals.role_id}}} = "" || ({{{prepared.literals.role_id}}} = "none" && NOT EXISTS { ?gmo gmo:GMO_000112 ?missing_assignment . }) || ({{{prepared.literals.role_id}}} != "none" && EXISTS {
    ?gmo gmo:GMO_000112 ?assigned_filter_role .
    ?assigned_filter_role rdfs:subClassOf* ?filter_role .
    ?filter_role rdfs:subClassOf+ gmo:GMO_000037 ;
                 dcterms:identifier {{{prepared.literals.role_id}}} .
  }))
  FILTER NOT EXISTS { ?gmo gmo:GMO_000113 ?assignment . }
}
```

## Output

```javascript
({
  json: function json({ roles, properties, role_none, property_none }) {
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

  const noneCount = (result) => {
    const raw = result.results.bindings[0]?.count?.value;
    const count = Number(raw);
    if (!/^(?:0|[1-9][0-9]*)$/.test(raw ?? "") || !Number.isSafeInteger(count)) {
      throw new Error("Invalid unassigned classification count.");
    }
    return count;
  };
  return {
    role_none_count: noneCount(role_none),
    property_none_count: noneCount(property_none),
    roles: facet(roles.results.bindings, true),
    properties: facet(properties.results.bindings, false),
  };
}
})
```
