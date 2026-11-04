# Search registered NCBI taxonomy candidates

Search scientific names by literal case-insensitive substring, or exact numeric Taxonomy ID, in the existing filtered\_has\_strain graph. Not all NCBI taxa are included.

## Parameters

- `q` Scientific-name literal substring, or an all-digit exact Taxonomy ID; 1 to 200 characters, not whitespace-only.
  - default: coli
  - example: coli, Escherichia, 562
- `limit` Maximum candidates, 1 to 50. has\_more reports further matches.
  - default: 20
  - example: 20, 50

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
    "result": "search-taxa.rq"
  },
  "parameters": {
    "q": {
      "default": "coli",
      "pattern": "^(?=[\\s\\S]{1,200}$)(?=[\\s\\S]*\\S)[\\s\\S]*$",
      "description": "Scientific-name literal substring, or an all-digit exact Taxonomy ID; 1 to 200 characters, not whitespace-only.",
      "examples": [
        "coli",
        "Escherichia",
        "562"
      ]
    },
    "limit": {
      "type": "integer",
      "default": "20",
      "pattern": "^(?:[1-9]|[1-4][0-9]|50)$",
      "description": "Maximum candidates, 1 to 50. has_more reports further matches.",
      "examples": [
        "20",
        "50"
      ]
    }
  }
}, prepare, select);
}
```

## `result`

```sparql
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?tax_id ?name ?rank ({{{prepared.literals.limit}}} AS ?limit)
WHERE {
  OPTIONAL {
    SELECT DISTINCT ?tax_id ?name ?rank ?priority
    WHERE {
      GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {
        ?tax taxo:scientificName ?name .
        OPTIONAL { ?tax taxo:rank ?rank }
      }
      BIND(STRAFTER(STR(?tax), "http://identifiers.org/taxonomy/") AS ?tax_id)
      FILTER(REGEX(?tax_id, "^[1-9][0-9]*$"))
      FILTER(IF(REGEX({{{prepared.literals.q}}}, "^[0-9]+$"),
        ?tax_id = {{{prepared.literals.q}}}, CONTAINS(LCASE(STR(?name)), LCASE({{{prepared.literals.q}}}))))
      BIND(IF(LCASE(?name) = LCASE({{{prepared.literals.q}}}), 0,
        IF(STRSTARTS(LCASE(?name), LCASE({{{prepared.literals.q}}})), 1, 2)) AS ?priority)
    }
    ORDER BY ?priority LCASE(?name) xsd:integer(?tax_id)
    LIMIT 51
  }
}
ORDER BY ?priority LCASE(?name) xsd:integer(?tax_id)
```

## Output

```javascript
({
  json: function json({ result }) {
  if (!Array.isArray(result?.results?.bindings) || result.results.bindings.length === 0) {
    throw new Error("Invalid taxonomy SPARQL result: metadata row required.");
  }
  const rows = result.results.bindings;
  const limit = Number(rows[0].limit?.value);
  if (!Number.isInteger(limit) || limit < 1 || limit > 50) {
    throw new Error("Invalid taxonomy candidate limit.");
  }
  const items = rows
    .filter((row) => row.tax_id)
    .map((row) => {
      if (!/^[1-9][0-9]{0,19}$/.test(row.tax_id.value) || !row.name?.value) {
        throw new Error("Invalid taxonomy candidate.");
      }
      const rankIri = row.rank?.value;
      return {
        tax_id: row.tax_id.value,
        name: row.name.value,
        rank: rankIri ? rankIri.split("/").pop() : null,
      };
    });
  return { items: items.slice(0, limit), limit, has_more: items.length > limit };
}
})
```
