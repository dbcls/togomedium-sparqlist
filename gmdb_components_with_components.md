# Get components co-occurrence
Searches for media containing the specified components. Return all the components in those media.

## Parameters

* `gmo_ids` GMO ID (multiple)
  * default: GMO_001331,GMO_001001

## Endpoint

http://togomedium.org/sparql

## `gmo_subquery_text`
```javascript
({
  json(params) {
    if (params.gmo_ids) {
      let subquery_text = "{ \n  select distinct ?medium \n  {"
      subquery_text +=  params["gmo_ids"].split(",").map((gmo_id) => {
        return "\n   ?medium olo:slot/olo:item/gmo:has_component/gmo:gmo_id gmo:" + gmo_id.trim()  + "."
      }).join("");
      subquery_text += "\n  }\n }";
      return subquery_text;
   } else {
     return "";
   }
  }
})
```

## `result` retrieve media

```sparql
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX olo: <http://purl.org/ontology/olo/core#>

SELECT DISTINCT ?gmo_id ?name
 (GROUP_CONCAT(DISTINCT ?label_ja; SEPARATOR = ", ") AS ?name_ja)
FROM <http://togomedium.org/media>
FROM <http://togomedium.org/gmo>
WHERE {
  {{gmo_subquery_text}}
  ?medium dcterms:identifier ?media_id .
  ?medium olo:slot/olo:item/gmo:has_component/gmo:gmo_id ?gmo_id .
  ?gmo_id rdfs:label ?name .
  FILTER (lang(?name) = 'en')
  OPTIONAL {
    ?gmo_id rdfs:label ?label_ja .
    FILTER (lang(?label_ja) = 'ja')
  }
}
GROUP BY ?gmo_id ?name
ORDER BY ?name
```

## Output

```javascript
({
  json({result}) {
	return result.results.bindings.map((item) => {
      return {
        "gmo_id": item.gmo_id.value.split("/").pop(),
        "name": item.name.value,
        "japanese_name": item.name_ja.value
      }
    });
  }
})
```