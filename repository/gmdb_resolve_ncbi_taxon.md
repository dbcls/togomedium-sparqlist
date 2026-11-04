# Resolve a registered NCBI taxonomy ID

Resolve an exact ID in filtered\_has\_strain independently of autocomplete candidates. not\_found means absent from this graph; merged/deleted status is not available.

## Parameters

- `tax_id` Positive decimal NCBI Taxonomy ID, at most 20 digits, without leading zeroes.
  - default: 562
  - example: 562, 2, 511145

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
    "result": "resolve-taxon.rq"
  },
  "parameters": {
    "tax_id": {
      "default": "562",
      "pattern": "^[1-9][0-9]{0,19}$",
      "description": "Positive decimal NCBI Taxonomy ID, at most 20 digits, without leading zeroes.",
      "examples": [
        "562",
        "2",
        "511145"
      ]
    }
  }
}, prepare, select);
}
```

## `result`

```sparql
PREFIX taxo: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>

SELECT ({{{prepared.literals.tax_id}}} AS ?requested_tax_id) ?tax_id ?name ?rank
WHERE {
  OPTIONAL {
    SELECT ?tax_id (MIN(STR(?scientific_name)) AS ?name) (MIN(STR(?rank_iri)) AS ?rank)
    WHERE {
      BIND(IRI(CONCAT("http://identifiers.org/taxonomy/", {{{prepared.literals.tax_id}}})) AS ?tax)
      GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {
        ?tax taxo:scientificName ?scientific_name .
        OPTIONAL { ?tax taxo:rank ?rank_iri }
      }
      BIND({{{prepared.literals.tax_id}}} AS ?tax_id)
    }
    GROUP BY ?tax_id
    HAVING (COUNT(?scientific_name) > 0)
  }
}
```

## Output

```javascript
({
  json: function json({ result }) {
  if (!Array.isArray(result?.results?.bindings) || result.results.bindings.length !== 1) {
    throw new Error("Invalid taxonomy resolution SPARQL result.");
  }
  const row = result.results.bindings[0];
  const requested_tax_id = row.requested_tax_id?.value;
  if (!/^[1-9][0-9]{0,19}$/.test(requested_tax_id ?? "")) {
    throw new Error("Invalid requested taxonomy ID.");
  }
  if (!row.tax_id) return { requested_tax_id, status: "not_found", taxon: null };
  if (row.tax_id.value !== requested_tax_id || !row.name?.value) {
    throw new Error("Invalid resolved taxonomy record.");
  }
  const rankIri = row.rank?.value;
  return {
    requested_tax_id,
    status: "found",
    taxon: {
      tax_id: row.tax_id.value,
      name: row.name.value,
      rank: rankIri ? rankIri.split("/").pop() : null,
    },
  };
}
})
```
