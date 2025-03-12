# histgram for media by taxon
Function for plotting histogram of media by number of culturable species

## Parameters


## Endpoint

http://togomedium.org/sparql

## `result` count results

```sparql
DEFINE sql:select-option "order"
PREFIX gmo: <http://purl.jp/bio/10/gmo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ddbj-tax: <http://ddbj.nig.ac.jp/ontologies/taxonomy/>
PREFIX taxid: <http://identifiers.org/taxonomy/>
PREFIX gtdb: <http://identifiers.org/gtdb/>
PREFIX sio: <http://semanticscience.org/resource/>

SELECT
  REPLACE(STR(?medium), "http://togomedium.org/medium/", "") AS ?medium_id
  COUNT(DISTINCT ?species_tax) AS ?num_of_species
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain>
FROM <http://ddbj.nig.ac.jp/ontologies/taxonomy/filtered_has_strain/2023>
FROM <http://togohmedium.org/gtdb/filterd_has_strain>
FROM <http://togomedium.org/media>
FROM <http://growthmedium.org/strain/2023>
FROM <http://growthmedium.org/strain/2024>
WHERE {
  ?medium rdf:type  gmo:GMO_000001 ;
    gmo:GMO_000114 ?culture_for .
  ?culture_for gmo:strain_id ?strain .
  ?strain a sio:SIO_010055 ;
    gmo:taxon ?tax .
  ?tax rdfs:subClassOf* ?species_tax .
  ?species_tax ddbj-tax:rank ddbj-tax:Species .
} GROUP BY ?medium ORDER BY DESC(?num_of_species)
```

## Output

```javascript
({
  json({result}) {
    const parseSparqlObject = (obj) => {
      const result = {};
      try {
        Object.entries(obj).forEach(([key, item]) => {
          result[key] = item["value"];
        });
      } catch (e) {
      }
      return Object.entries(result).length ? result : null;
    };

    const data = [];
    result.results.bindings.forEach(row => {
      data.push(parseSparqlObject(row));
    });
    console.log(data[0]);
 
    // binの設定
    const bins = [
      { label: "1", min: 1, max: 1 },
      { label: "2", min: 2, max: 2 },
      { label: "3", min: 3, max: 3 },
      { label: "4", min: 4, max: 4 },
      { label: "5", min: 5, max: 5 },
      { label: "6", min: 6, max: 6 },
      { label: "7", min: 7, max: 7 },
      { label: "8", min: 8, max: 8 },
      { label: "9", min: 9, max: 9 },
      { label: "10", min: 10, max: 10 },
      { label: "11-20", min: 11, max: 20 },
      { label: "21-30", min: 21, max: 30 },
      { label: "31-40", min: 31, max: 40 },
      { label: "41-50", min: 41, max: 50 },
      { label: "51-100", min: 51, max: 100 },
      { label: "101-1000", min: 101, max: 1000 },
      { label: "1001-2000", min: 1001, max: 2000 }
    ];
    
    // 初期状態のヒストグラム（各ビンの頻度を 0 で初期化）
    const histogram = bins.map(bin => ({
      bin: bin.label,
      frequency: 0
    }));
 
    // 各データの count を該当するビンに振り分ける
    data.forEach(record => {
      const count = record.num_of_species;
      // 定義された bins の順に探し、最初に該当したビンにカウントする
      const bin = bins.find(b => count >= b.min && count <= b.max);
      if (bin) {
        // histogram 配列内の該当オブジェクトを探してカウントアップ
        const histItem = histogram.find(h => h.bin === bin.label);
        if (histItem) {
          histItem.frequency++;
        }
      }
    });
    return histogram;
  }
})
```