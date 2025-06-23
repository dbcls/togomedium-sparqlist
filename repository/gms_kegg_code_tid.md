# kegg org code to t_number : moriyta (gm, growth_media, KEGG API)

## `kegg_api`
```javascript
async ({})=>{
  let kegg_api = "http://rest.kegg.jp/list/organism";
  let options_text = {
    method: "get",
    mode:  "cors"
  };
  let text = await fetch(kegg_api, options_text).then(res => res.text());
  let list = text.split(/\n/);
  let r = {};
  for(let i = 0; i < list.length; i++){
    let tmp = list[i].split(/\t/);
    if(tmp[0]){
      let name = tmp[2].replace(/ +\(.+$/, "");
      r[tmp[1]] = {tid: tmp[0], label: name}
    }
  }
  return r;
};