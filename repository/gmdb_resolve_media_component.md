# Resolve a GMO component

Resolve an exact GMO component ID independently of candidate limits. Missing IDs produce explicit not\_found.

## Parameters

- `gmo_id` Exact GMO component ID.
  - default: GMO\_001815
  - example: GMO\_001815

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
    "result": "resolve-component.rq"
  },
  "parameters": {
    "gmo_id": {
      "default": "GMO_001815",
      "pattern": "^GMO_[0-9]{6}$",
      "description": "Exact GMO component ID.",
      "examples": [
        "GMO_001815"
      ]
    }
  }
}, prepare, select);
}
```

## `result`

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ({{{prepared.literals.gmo_id}}} AS ?requested_gmo_id) ?gmo_id ?name
WHERE {
  OPTIONAL {
    SELECT ?gmo_id (MIN(STR(?preferred)) AS ?name)
    WHERE {
      GRAPH <http://togomedium.org/gmo> {
        ?component rdfs:subClassOf+ gmo:GMO_000002 ; dct:identifier ?gmo_id ; skos:prefLabel ?preferred .
        FILTER(?gmo_id = {{{prepared.literals.gmo_id}}})
      }
    } GROUP BY ?gmo_id
    HAVING(COUNT(?preferred) > 0)
  }
}
```

## Output

```javascript
({
  json: function json({ result }) {
  const rows = result?.results?.bindings;
  if (!Array.isArray(rows) || rows.length !== 1)
    throw new Error("Invalid component resolution result.");
  const row = rows[0];
  const requested_gmo_id = row.requested_gmo_id?.value;
  if (!/^GMO_[0-9]{6}$/.test(requested_gmo_id ?? ""))
    throw new Error("Invalid requested component ID.");
  if (!row.gmo_id) return { requested_gmo_id, status: "not_found", component: null };
  if (row.gmo_id.value !== requested_gmo_id || !row.name?.value)
    throw new Error("Invalid resolved component.");
  return {
    requested_gmo_id,
    status: "found",
    component: { gmo_id: row.gmo_id.value, name: row.name.value },
  };
}
})
```
