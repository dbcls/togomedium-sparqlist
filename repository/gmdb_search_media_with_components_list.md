# Search media with species and strain counts with component filtering

Search names and identifiers, taxonomy and inferred collection. Taxonomy filters media only; species and strain counts and sorting always cover all organisms registered to each matching medium. No collection specified does not assert curator origin. Component IDs are combined with AND using recorded inclusion and GMO descendants.

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
- `sort` Whole-medium count to sort before pagination. Component-count ties: species descending, strains descending, lexical GM ID ascending. Other sorts retain their existing tie order.
  - default: strain\_count
  - example: species\_count, strain\_count, component\_count
- `order` Sort direction.
  - default: desc
  - example: asc, desc
- `limit` Maximum media per page, 1 to 100.
  - default: 20
  - example: 20, 50, 100
- `offset` Number of matching media to skip, 0 to 9900. The conservative cap keeps offset plus any accepted limit within Virtuoso's 10000-row sorted-page limit.
  - default: 0
  - example: 0, 20, 2925, 9900
- `component_ids` Comma-separated GMO IDs combined with AND; each includes descendants. Maximum 4096 characters bounds request size, not a five-component selection limit.
  - default: 
  - example: GMO\_001815, GMO\_001001,GMO\_001002

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
  const definitions = {"name":{"default":"","pattern":"^[\\s\\S]{0,200}$","description":"Case-insensitive literal substring of medium name, GM ID or original ID. Empty means no text filter.","examples":["mrs","M1406","NBRC_M1"]},"taxonomy_id":{"default":"","type":"string-list","placeholder":"taxonomy_values","pattern":"^(?:[1-9][0-9]{0,19}(?:,[1-9][0-9]{0,19}){0,4})?$","description":"Up to five comma-separated positive NCBI Taxonomy IDs, combined with AND at medium level. Each ID includes descendants; different strains may satisfy different IDs. Duplicate IDs are equivalent to one. Empty means no filter. Counts always cover the whole medium.","examples":["1386","1386,561","561,562","83333"]},"collection":{"default":"","pattern":"^(?:JCM|NBRC|DSMZ|ATCC|NIES|none)?$","description":"Inferred collection ID. Empty means Any; none means No collection specified.","examples":["JCM","none"]},"sort":{"default":"strain_count","pattern":"^(?:species_count|strain_count|component_count)$","description":"Whole-medium count to sort before pagination. Component-count ties: species descending, strains descending, lexical GM ID ascending. Other sorts retain their existing tie order.","examples":["species_count","strain_count","component_count"]},"order":{"default":"desc","pattern":"^(?:asc|desc)$","description":"Sort direction.","examples":["asc","desc"]},"limit":{"default":"20","type":"integer","pattern":"^(?:[1-9]|[1-9][0-9]|100)$","description":"Maximum media per page, 1 to 100.","examples":["20","50","100"]},"offset":{"default":"0","type":"integer","pattern":"^(?:0|[1-9][0-9]{0,2}|[1-8][0-9]{3}|9[0-8][0-9]{2}|9900)$","description":"Number of matching media to skip, 0 to 9900. The conservative cap keeps offset plus any accepted limit within Virtuoso's 10000-row sorted-page limit.","examples":["0","20","2925","9900"]},"component_ids":{"default":"","type":"string-list","placeholder":"component_values","pattern":"^(?=.{0,4096}$)(?:GMO_[0-9]{6}(?:,GMO_[0-9]{6})*)?$","description":"Comma-separated GMO IDs combined with AND; each includes descendants. Maximum 4096 characters bounds request size, not a five-component selection limit.","examples":["GMO_001815","GMO_001001,GMO_001002"]}};
  const supplied = Object.fromEntries(Object.keys(definitions).filter(name => Object.hasOwn(context, name)).map(name => [name, context[name]]));
  const parameters = prepare(definitions, supplied).values;
  const endpoint = context.SPARQLIST_TOGOMEDIUM_ENDPOINT;
  if (typeof endpoint !== "string" || !/^https?:\/\//.test(endpoint)) throw new Error("SPARQLIST_TOGOMEDIUM_ENDPOINT is required.");
  const execute = async function json({ parameters: params, endpoint, queries }) {
  const componentFilter = (value = "") => {
    if (value.length > 4096 || !/^(?:GMO_[0-9]{6}(?:,GMO_[0-9]{6})*)?$/.test(value))
      throw new Error("Invalid component_ids");
    if (!value) return "";
    const ids = [...new Set(value.split(","))];
    return queries.components
      .replace("__COMPONENT_IRIS__", ids.map((id) => `<http://purl.jp/bio/10/gmo/${id}>`).join(" "))
      .replace("__COMPONENT_COUNT__", String(ids.length));
  };
  const listOutput = function json({ result, count }) {
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
  };
  const request = async (label, query) => {
    const response = await fetch(endpoint + (endpoint.includes("?") ? "&" : "?") + "format=json", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Accept: "application/sparql-results+json",
      },
      body: "query=" + encodeURIComponent(query),
    });
    if (!response.ok) throw new Error(label + ": HTTP " + response.status);
    const state = response.headers.get("X-SQL-State");
    if (state && state !== "00000")
      throw new Error(`${label}: incomplete SPARQL response (${state})`);
    const result = await response.json();
    if (!Array.isArray(result?.results?.bindings))
      throw new Error(`${label}: invalid SPARQL response`);
    return result;
  };
  const components = params.component_ids || "",
    taxonomy = params.taxonomy_id || "",
    name = params.name || "",
    collection = params.collection || "",
    sort = params.sort || "strain_count",
    order = params.order || "desc";
  if (
    !/^(?:[1-9][0-9]{0,19}(?:,[1-9][0-9]{0,19})*)?$/.test(taxonomy) ||
    name.length > 200 ||
    !/^(?:JCM|NBRC|DSMZ|ATCC|NIES|none)?$/.test(collection) ||
    !/^(species_count|strain_count|component_count)$/.test(sort) ||
    !/^(asc|desc)$/.test(order)
  )
    throw new Error("Invalid parameters");
  const limit = Number(params.limit || 20),
    offset = Number(params.offset || 0);
  if (
    !Number.isInteger(limit) ||
    limit < 1 ||
    limit > 100 ||
    !Number.isInteger(offset) ||
    offset < 0 ||
    offset > 9900
  )
    throw new Error("Invalid pagination");
  const mediumUris = (result) =>
    result.results.bindings.map((row) => {
      const uri = row.medium?.value;
      if (!/^http:\/\/togomedium\.org\/medium\/M[0-9]+$/.test(uri ?? ""))
        throw new Error("Invalid medium URI");
      return uri;
    });
  let componentSet = null,
    taxonSet = null;
  const filter = componentFilter(components);
  if (filter) {
    const selectedIds = [...new Set(components.split(","))];
    const validRows = await request(
      "selected components",
      queries.selectedComponents.replace(
        "__COMPONENT_IDS__",
        selectedIds.map((id) => JSON.stringify(id)).join(","),
      ),
    );
    const validIds = new Set(
      validRows.results.bindings.map((row) => {
        const id = row.gmo_id?.value;
        if (!/^GMO_[0-9]{6}$/.test(id ?? "") || !selectedIds.includes(id))
          throw new Error("Invalid selected component result");
        return id;
      }),
    );
    if (selectedIds.some((id) => id === "GMO_000002" || !validIds.has(id))) {
      componentSet = new Set();
    } else {
      componentSet = new Set(mediumUris(await request("components", filter)));
    }
  }
  const taxa = [...new Set(taxonomy.split(",").filter(Boolean))];
  if (taxa.length && (!componentSet || componentSet.size))
    taxonSet = new Set(
      mediumUris(
        await request(
          "taxa",
          queries.taxa
            .replace(
              "__TAXON_IRIS__",
              taxa.map((id) => `<http://identifiers.org/taxonomy/${id}>`).join(" "),
            )
            .replace("__TAXON_COUNT__", String(taxa.length)),
        ),
      ),
    );
  const selected =
    componentSet && taxonSet
      ? new Set([...componentSet].filter((uri) => taxonSet.has(uri)))
      : componentSet || taxonSet;
  let contents = [];
  if (!selected || selected.size) {
    let query = queries.details.split('"__NAME__"').join(JSON.stringify(name));
    if (selected) {
      const values = [...selected]
        .map((uri) => {
          if (!/^http:\/\/togomedium\.org\/medium\/M[0-9]+$/.test(uri))
            throw new Error("Invalid medium URI");
          return "<" + uri + ">";
        })
        .join(" ");
      query = query.replace(
        "?medium a gmo:GMO_000001",
        "VALUES ?medium { " + values + " }\n?medium a gmo:GMO_000001",
      );
    }
    const result = await request("details", query);
    contents = listOutput({
      result,
      count: {
        results: {
          bindings: [
            {
              total: { value: String(result.results.bindings.length) },
              limit: { value: "100" },
              offset: { value: "0" },
            },
          ],
        },
      },
    }).contents;
  }
  const filtered = collection
    ? contents.filter((item) => (item.collection?.id || "none") === collection)
    : contents;
  if (filtered.length) {
    let query = queries.componentCounts;
    // Avoid large VALUES lists; the compact whole-medium count table is faster for broad searches.
    if (filtered.length <= 100) {
      const ids = filtered.map(({ id }) => {
        if (!/^M[0-9]+$/.test(id)) throw new Error("Invalid medium ID");
        return JSON.stringify(id);
      });
      query = query.replace(
        "?medium a gmo:GMO_000001",
        `VALUES ?id { ${ids.join(" ")} }\n?medium a gmo:GMO_000001`,
      );
    }
    const result = await request("component counts", query);
    const counts = new Map();
    for (const row of result.results.bindings) {
      const id = row.id?.value;
      const raw = row.component_count?.value;
      const count = Number(raw);
      if (
        !/^M[0-9]+$/.test(id ?? "") ||
        counts.has(id) ||
        !/^(0|[1-9][0-9]*)$/.test(raw ?? "") ||
        !Number.isSafeInteger(count)
      )
        throw new Error("Invalid component count result");
      counts.set(id, count);
    }
    for (const item of filtered) {
      if (!counts.has(item.id)) throw new Error(`Missing component count for ${item.id}`);
      item.component_count = counts.get(item.id);
    }
  }
  const other = sort === "species_count" ? "strain_count" : "species_count";
  filtered.sort(
    (a, b) =>
      (order === "asc" ? 1 : -1) * (a[sort] - b[sort]) ||
      b[other] - a[other] ||
      (sort === "component_count" ? b.strain_count - a.strain_count : 0) ||
      (a.id < b.id ? -1 : a.id > b.id ? 1 : 0),
  );
  return {
    contents: filtered.slice(offset, offset + limit),
    total: filtered.length,
    limit,
    offset,
  };
};
  return await execute({parameters, endpoint, queries: {"components":"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX gmo: <http://purl.jp/bio/10/gmo/>\nSELECT ?medium FROM NAMED <http://togomedium.org/media/components> FROM NAMED <http://togomedium.org/gmo> WHERE { VALUES ?required_component { __COMPONENT_IRIS__ } GRAPH <http://togomedium.org/gmo> { ?included rdfs:subClassOf* ?required_component } GRAPH <http://togomedium.org/media/components> { ?medium gmo:included_component ?included } } GROUP BY ?medium HAVING(COUNT(DISTINCT ?required_component) = __COMPONENT_COUNT__)\n","taxa":"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX gmo: <http://purl.jp/bio/10/gmo/>\nSELECT ?medium FROM <http://togomedium.org/strain> FROM NAMED <http://togomedium.org/taxonomy/filtered_has_strain> WHERE { VALUES ?requested { __TAXON_IRIS__ } ?medium gmo:GMO_000114/gmo:strain_id/gmo:taxon ?taxon . GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> { ?taxon rdfs:subClassOf* ?requested } } GROUP BY ?medium HAVING(COUNT(DISTINCT ?requested)=__TAXON_COUNT__)\n","details":"PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX skos: <http://www.w3.org/2004/02/skos/core#>\nPREFIX dct: <http://purl.org/dc/terms/>\nPREFIX gmo: <http://purl.jp/bio/10/gmo/>\nPREFIX olo: <http://purl.org/ontology/olo/core#>\nPREFIX tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>\n# Based on search-media-list/list-media-all-taxa.rq; maintained here for staged aggregation.\nSELECT ?id ?name ?collection_id ?collection_label ?ph ?strain_count ?species_count\nFROM <http://togomedium.org/media>\nFROM <http://togomedium.org/strain>\nFROM NAMED <http://togomedium.org/taxonomy/filtered_has_strain>\nWHERE {\n{\nSELECT ?id (MIN(STR(?raw_name)) AS ?name) (MIN(STR(?raw_ph)) AS ?ph) (MIN(IF(STRSTARTS(COALESCE(STR(?origin), \"\"), \"JCM_\"), 0, IF(STRSTARTS(COALESCE(STR(?origin), \"\"), \"NBRC_\"), 1, IF(STRSTARTS(COALESCE(STR(?origin), \"\"), \"DSMZ_\"), 2, IF(STRSTARTS(COALESCE(STR(?source), \"\"), \"http://www.atcc.org/\") || STRSTARTS(COALESCE(STR(?source), \"\"), \"https://www.atcc.org/\"), 3, IF(STRSTARTS(COALESCE(STR(?source), \"\"), \"http://mcc.nies.go.jp/\") || STRSTARTS(COALESCE(STR(?source), \"\"), \"https://mcc.nies.go.jp/\"), 4, 5)))))) AS ?collection_rank)\n       (COUNT(DISTINCT ?strain) AS ?strain_count) (COUNT(DISTINCT ?species) AS ?species_count)\nWHERE {\n  ?medium a gmo:GMO_000001 ; dct:identifier ?id ; rdfs:label ?raw_name ; olo:length ?paragraph_length .\n  FILTER(?paragraph_length > 0)\n  OPTIONAL { ?medium skos:altLabel ?origin . }\n  OPTIONAL { ?medium gmo:GMO_000108 ?source . }\n  OPTIONAL { ?medium gmo:ph ?raw_ph . }\n  FILTER(\"__NAME__\" = \"\" || CONTAINS(LCASE(STR(?id)), LCASE(\"__NAME__\")) || CONTAINS(LCASE(STR(?raw_name)), LCASE(\"__NAME__\")) || CONTAINS(LCASE(COALESCE(STR(?origin), \"\")), LCASE(\"__NAME__\")))\n\nOPTIONAL { ?medium gmo:GMO_000114/gmo:strain_id ?strain . OPTIONAL {\n  ?strain gmo:taxon ?taxon .\n  GRAPH <http://togomedium.org/taxonomy/filtered_has_strain> {\n    ?taxon rdfs:subClassOf* ?species . ?species tax:rank tax:Species .\n  }\n} }\n}\nGROUP BY ?id\n}\nVALUES (?collection_rank ?collection_id ?collection_label) {\n  (0 \"JCM\" \"JCM\")\n  (1 \"NBRC\" \"NBRC\")\n  (2 \"DSMZ\" \"DSMZ\")\n  (3 \"ATCC\" \"ATCC\")\n  (4 \"NIES\" \"NIES\")\n  (5 \"none\" \"No collection specified\")\n}\nFILTER(\"\" = \"\" || ?collection_id = \"\")\n}\nORDER BY\n  ASC(IF(\"species_count\" = \"species_count\" && \"desc\" = \"asc\", ?species_count, \"\"))\n  DESC(IF(\"species_count\" = \"species_count\" && \"desc\" = \"desc\", ?species_count, \"\"))\n  ASC(IF(\"species_count\" = \"strain_count\" && \"desc\" = \"asc\", ?strain_count, \"\"))\n  DESC(IF(\"species_count\" = \"strain_count\" && \"desc\" = \"desc\", ?strain_count, \"\"))\n  DESC(IF(\"species_count\" = \"species_count\", ?strain_count, ?species_count)) ASC(?id)\n","selectedComponents":"PREFIX gmo: <http://purl.jp/bio/10/gmo/>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nPREFIX skos: <http://www.w3.org/2004/02/skos/core#>\nPREFIX dct: <http://purl.org/dc/terms/>\nSELECT DISTINCT ?gmo_id WHERE { GRAPH <http://togomedium.org/gmo> {\n ?component rdfs:subClassOf+ gmo:GMO_000002; dct:identifier ?gmo_id; skos:prefLabel ?preferred .\n FILTER(?gmo_id IN (__COMPONENT_IDS__))\n} }\n","componentCounts":"PREFIX gmo: <http://purl.jp/bio/10/gmo/>\nPREFIX dct: <http://purl.org/dc/terms/>\nPREFIX olo: <http://purl.org/ontology/olo/core#>\nSELECT ?id (COUNT(DISTINCT ?component) AS ?component_count)\nFROM <http://togomedium.org/media>\nFROM NAMED <http://togomedium.org/media/components>\nWHERE {\n  ?medium a gmo:GMO_000001 ; dct:identifier ?id ; olo:length ?length .\n  FILTER(?length > 0)\n  OPTIONAL {\n    GRAPH <http://togomedium.org/media/components> {\n      ?medium gmo:included_component ?component .\n    }\n  }\n}\nGROUP BY ?id\n"}});
} })
```
