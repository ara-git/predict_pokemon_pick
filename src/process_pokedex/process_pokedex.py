"""
showdown GithubリポジトリからDLしたポケモン図鑑データを加工し、csvにする。
"""

import pandas as pd
import json


def process_pokedex():
    # JSONファイルを読み込む
    with open("./data/input/pokedex.json", "r", encoding="utf-8") as file:
        pokedex = json.load(file)

    result_list = []
    for key, value in pokedex["Pokedex"].items():
        result_list.append([value["name"]] + value["types"])

    result_df = pd.DataFrame(result_list, columns=["name", "type1", "type2"])

    return result_df


if __name__ == "__main__":
    pokedex_df = process_pokedex()
    pokedex_df.to_csv("./data/intermediate/pokedex.csv")
