 # Interview form query example 2

Linked information from ChEMBL database

## Parameters

* `limit` limit
  * default: 10
* `offset` offset
  * default: 0
  
## Endpoint

http://sparql.med2rdf.org/sparql

## Count `count`

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cco: <http://rdf.ebi.ac.uk/terms/chembl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ifo: <http://med2rdf.org/ontology/ifo/>

SELECT (COUNT(?drug) AS ?total) ?offset ?limit
WHERE {
  GRAPH <http://med2rdf.org/graph/if> {
    ?if ifo:drug ?drug .
    ?drug rdf:type ifo:Drug .
    ?drug rdfs:seeAlso ?chembl .
  }
  SERVICE <https://integbio.jp/rdf/mirror/ebi/sparql> {
    GRAPH <http://rdf.ebi.ac.uk/dataset/chembl> {
      ?chembl sio:SIO_000008 [
        a sio:CHEMINF_000216 ;
        sio:SIO_000300 ?mol_weight
      ] .
    }
  }
  BIND("{{limit}}" AS ?limit)
  BIND("{{offset}}" AS ?offset)
}
```

## Query `results`

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cco: <http://rdf.ebi.ac.uk/terms/chembl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX ifo: <http://med2rdf.org/ontology/ifo/>

SELECT ?if ?drug ?chembl ?mol_weight
WHERE {
  GRAPH <http://med2rdf.org/graph/if> {
    ?if ifo:drug ?drug .
    ?drug rdf:type ifo:Drug .
    ?drug rdfs:seeAlso ?chembl .
  }
  SERVICE <https://integbio.jp/rdf/mirror/ebi/sparql> {
    GRAPH <http://rdf.ebi.ac.uk/dataset/chembl> {
      ?chembl sio:SIO_000008 [
        a sio:CHEMINF_000216 ;
        sio:SIO_000300 ?mol_weight
      ] .
    }
  }
}
LIMIT {{limit}}
OFFSET {{offset}}
```

```javascript
({
  json({results, count}) {
    let result_rows = results.results.bindings ;
    let count_rows = count.results.bindings[0] ;
    let result = {} ;
    result.contents = [];

    for (let i = 0; i < result_rows.length ;i++) {
      result.contents.push({
        if: result_rows[i].if.value,
        drug: result_rows[i].drug.value,
        chembl: result_rows[i].chembl.value,
        mol_weight: result_rows[i].mol_weight.value,
      });
    }
    
    result.columns = [];
    result.columns.push({key: "if", label: "IF"});
    result.columns.push({key: "drug", label: "Drug"});
    result.columns.push({key: "chembl", label: "ChEMBL"});
    result.columns.push({key: "mol_weight", label: "Mol. weight"});
    result.total = count_rows.total.value ;
    result.limit = count_rows.limit.value ;
    result.offset = count_rows.offset.value ;
    return result;
  }
})


```