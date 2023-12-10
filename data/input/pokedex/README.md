# フォルダ概要
https://github.com/smogon/pokemon-showdown/blob/master/data/pokedex.ts
から、ポケモン情報を取得する。
元データは.tsで書かれているので、Pythonで読み込めるようにjsonファイルに変換する。
変換された結果は本階層に保存する（手動）。

# 手順
1. TypeScriptファイルをJavaScriptファイルにコンパイル
npx tsc pokedex.ts

2. JavaScriptファイルをNode.jsで実行してJSONファイルに変換
node -e "const Pokedex = require('./pokedex'); console.log(JSON.stringify(Pokedex));" > pokedex.json

