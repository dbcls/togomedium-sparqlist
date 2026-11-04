# Search GMO components for media filtering

Global name and GMO ID substring search, limited to components whose own or descendant inclusion matches at least one valid medium. Independent of other selected filters.

## Parameters

- `q` Literal name, alternative name or GMO ID substring, 1 to 200 characters, not whitespace-only.
  - default: glucose
  - example: glucose, GMO\_001815, グルコース
- `limit` Maximum candidates, 1 to 50. has\_more indicates further matches.
  - default: 20
  - example: 20, 50

## Output

```javascript
({ async json(context) {
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
  const definitions = {"q":{"default":"glucose","pattern":"^(?=[\\s\\S]{1,200}$)(?=[\\s\\S]*\\S)[\\s\\S]*$","description":"Literal name, alternative name or GMO ID substring, 1 to 200 characters, not whitespace-only.","examples":["glucose","GMO_001815","グルコース"]},"limit":{"default":"20","type":"integer","pattern":"^(?:[1-9]|[1-4][0-9]|50)$","description":"Maximum candidates, 1 to 50. has_more indicates further matches.","examples":["20","50"]}};
  const supplied = Object.fromEntries(Object.keys(definitions).filter(name => Object.hasOwn(context, name)).map(name => [name, context[name]]));
  const parameters = prepare(definitions, supplied).values;
  const endpoint = context.SPARQLIST_TOGOMEDIUM_ENDPOINT;
  if (typeof endpoint !== "string" || !/^https?:\/\//.test(endpoint)) throw new Error("SPARQLIST_TOGOMEDIUM_ENDPOINT is required.");
  const execute = async function json({ parameters, endpoint, queries }) {
  const request = async (query) => {
    const response = await fetch(endpoint + (endpoint.includes("?") ? "&" : "?") + "format=json", {
      method: "POST",
      headers: {
        Accept: "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "query=" + encodeURIComponent(query),
    });
    if (!response.ok) throw new Error(`SPARQL HTTP ${response.status}`);
    const state = response.headers.get("X-SQL-State");
    if (state && state !== "00000") throw new Error(`Incomplete SPARQL response ${state}`);
    const data = await response.json();
    if (!Array.isArray(data?.results?.bindings)) throw new Error("Invalid SPARQL response");
    return data.results.bindings;
  };
  const q = parameters.q,
    limit = Number(parameters.limit);
  if (
    typeof q !== "string" ||
    q.length > 200 ||
    !q.trim() ||
    !Number.isInteger(limit) ||
    limit < 1 ||
    limit > 50
  )
    throw new Error("Invalid candidate parameters");
  const rows = await request(
    queries.candidates
      .replaceAll('"{{q}}"', JSON.stringify(q))
      .replaceAll('"{{limit}}"', JSON.stringify(String(limit))),
  );
  const candidates = rows
    .filter((row) => row.gmo_id)
    .map((row) => {
      if (!/^GMO_[0-9]{6}$/.test(row.gmo_id.value) || !row.name?.value)
        throw new Error("Invalid component candidate");
      return { gmo_id: row.gmo_id.value, name: row.name.value };
    });
  if (!candidates.length) return { items: [], limit, has_more: false };
  const included = await request(queries.included);
  const parents = await request(queries.parents);
  const parentMap = new Map();
  for (const row of parents) {
    const child = row.child?.value,
      parent = row.parent?.value;
    if (!child || !parent) throw new Error("Invalid component hierarchy");
    if (!parentMap.has(child)) parentMap.set(child, new Set());
    parentMap.get(child).add(parent);
  }
  const linked = new Set();
  const pending = included.map((row) => {
    if (!row.included?.value) throw new Error("Invalid included component");
    return row.included.value;
  });
  while (pending.length) {
    const uri = pending.pop();
    if (linked.has(uri)) continue;
    linked.add(uri);
    for (const parent of parentMap.get(uri) ?? []) pending.push(parent);
  }
  const items = candidates.filter((item) => linked.has("http://purl.jp/bio/10/gmo/" + item.gmo_id));
  const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  items.sort(
    (a, b) => compare(a.name.toLowerCase(), b.name.toLowerCase()) || compare(a.gmo_id, b.gmo_id),
  );
  return { items: items.slice(0, limit), limit, has_more: items.length > limit };
};
  return await execute({parameters, endpoint, queries: {"candidates":"PREFIX gmo: <http://purl.jp/bio/10/gmo/>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX skos: <http://www.w3.org/2004/02/skos/core#>\nPREFIX dct: <http://purl.org/dc/terms/>\nSELECT ?gmo_id ?name (\"{{limit}}\" AS ?limit)\nWHERE {\n  OPTIONAL {\n    SELECT ?gmo_id (MIN(STR(?preferred)) AS ?name)\n    WHERE {\n      GRAPH <http://togomedium.org/gmo> {\n        ?component (dct:identifier|skos:prefLabel|skos:altLabel|rdfs:label) ?search_name .\n        FILTER(CONTAINS(LCASE(STR(?search_name)), LCASE(\"{{q}}\")))\n        ?component rdfs:subClassOf+ gmo:GMO_000002 ; dct:identifier ?gmo_id ; skos:prefLabel ?preferred .\n        FILTER(REGEX(STR(?gmo_id), \"^GMO_[0-9]{6}$\"))\n      }\n    } GROUP BY ?gmo_id\n  }\n}\n","included":"PREFIX gmo: <http://purl.jp/bio/10/gmo/>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX dct: <http://purl.org/dc/terms/>\nPREFIX olo: <http://purl.org/ontology/olo/core#>\nSELECT DISTINCT ?included WHERE {\n GRAPH <http://togomedium.org/media> {\n  ?medium a gmo:GMO_000001; dct:identifier ?medium_id; rdfs:label ?medium_name; olo:length ?paragraph_length .\n  FILTER(?paragraph_length > 0)\n }\n GRAPH <http://togomedium.org/media/components> { ?medium gmo:included_component ?included }\n}\n","parents":"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nSELECT ?child ?parent FROM <http://togomedium.org/gmo> WHERE { ?child rdfs:subClassOf ?parent }\n"}});
} })
```
