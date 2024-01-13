import bs4
import pandas as pd
import glob
import pickle
import json


def retrieve_party_from_html():
    """
    DLしたローカルのhtmlファイル（showdownの対戦リプレイデータ）から、ウーラオス入りの構築データを取得する。
    Augs:

    Returns:
    """
    # フォルダ内部のファイル一覧を取得する
    files_list = glob.glob("data/input/stock/ShowDown_html/*")

    # （自分の選出、自分の先発、相手の構築）をまとめたデータの格納先辞書
    result_dict = {}

    # データ数のカウント
    count = 0

    for i in range(len(files_list)):
        print("処理したhtmlの数:", i)
        # ファイルを開く
        soup = bs4.BeautifulSoup(open(files_list[i], encoding="utf-8"), "html.parser")
        # バトルデータのstringを読み込む
        battle_log_str = soup.find("script", class_="battle-log-data").string

        pick_dict = {}

        for side in ["my", "opponent"]:
            "両サイドの構築を取り出す"
            # print("side:", side)
            party_list = get_party_data_from_html(battle_log_str, side=side)

            # 選出されたポケモンを取り出す
            start_picked_poke_list, picked_poke_list = get_poke_pick(
                battle_log_str, side
            )
            # サイドをキー、（構築、選出、初期選出）を値とした辞書を作成
            pick_dict[side] = (party_list, picked_poke_list, start_picked_poke_list)

        for side in ["my", "opponent"]:
            "データを整形する"
            if side == "my":
                "my 側で考える"
                # 相手の選出・構築と自分の構築を取得
                my_party_list = pick_dict["my"][0]
                opponent_party_list = pick_dict["opponent"][0]
                opponent_pick_list = pick_dict["opponent"][1]
                opponent_start_pick_list = pick_dict["opponent"][2]

            else:
                "opponent 側で考える"
                # 相手の選出・構築と自分の構築を取得
                my_party_list = pick_dict["opponent"][0]
                opponent_party_list = pick_dict["my"][0]
                opponent_pick_list = pick_dict["my"][1]
                opponent_start_pick_list = pick_dict["my"][2]

            # データを格納する
            result_dict[count] = {
                "opponent_pick": opponent_pick_list,
                "opponent_start_pick": opponent_start_pick_list,
                "my_party": my_party_list,
                "opponent_party": opponent_party_list,
            }
            count += 1

    return result_dict


def get_party_data_from_html(battle_log_str, side):
    """
    バトルデータのstringから構築のリストを抽出する
    Augs:
    """
    if side == "my":
        # 自構築を抜き出す
        party_list = [
            x.split(",")[0][9:] for x in battle_log_str.split("\n") if "|poke|p1|" in x
        ]
    elif side == "opponent":
        # 相手構築を抜き出す
        party_list = [
            x.split(",")[0][9:] for x in battle_log_str.split("\n") if "|poke|p2|" in x
        ]

    # ポケモン名を正規化する
    party_list = [standardize_poke_name(poke_name) for poke_name in party_list]
    return party_list


def get_poke_pick(battle_log_str, side):
    """
    選出データをとる
    """
    picked_poke_list = []
    for row in battle_log_str.split("\n"):
        # 行を分割
        if "|switch|" not in row:
            # 交代に関する記述がなければ次の行に行く
            continue

        if side == "my":
            # 自チーム
            if "p1" not in row:
                continue

        if side == "opponent":
            # 相手チーム
            if "p2" not in row:
                continue

        # "|"で分割し、選出されたポケモンを抽出する
        element = row.split("|")[3].split(",")[0]
        picked_poke_list.append(element)

    # イルカマン（ヒーロー）等、途中で名称が変わるポケモンは削除する
    for exception_poke in [
        "Palafin-Hero",
        "Ogerpon-Teal-Tera",
        "Ogerpon-Wellspring-Tera",
        "Ogerpon-Cornerstone-Tera",
        "Ogerpon-Hearthflame-Tera",
    ]:
        if exception_poke in picked_poke_list:
            picked_poke_list.remove(exception_poke)

    # 先発ポケモンのリストは別で持つ
    start_picked_poke_list = picked_poke_list[:2]

    # 複数回交代が起こると重複が起こるので、削除する
    picked_poke_list = list(set(picked_poke_list))

    # ポケモン名を正規化する
    start_picked_poke_list = [
        standardize_poke_name(poke_name) for poke_name in start_picked_poke_list
    ]
    picked_poke_list = [
        standardize_poke_name(poke_name) for poke_name in picked_poke_list
    ]

    return start_picked_poke_list, picked_poke_list


def standardize_poke_name(poke_name):
    """
    ポケモンの名前を正規化する
    """
    # ポケモン名を正規化
    poke_name = poke_name.replace("-", "")
    poke_name = poke_name.replace(" ", "")
    poke_name = poke_name.lower()

    "例外処理"
    # トリトドン
    if "gastrodon" in poke_name:
        poke_name = "gastrodon"

    # フラージェス
    if "florges" in poke_name:
        poke_name = "florges"

    # ゲッコウガ
    if "greninja" in poke_name:
        poke_name = "greninja"

    # シャリタツ
    if "tatsugiri" in poke_name:
        poke_name = "tatsugiri"

    # ノココッチ
    if "dudunsparce" in poke_name:
        poke_name = "dudunsparce"

    # メブキジカ
    if "sawsbuck" in poke_name:
        poke_name = "sawsbuck"

    # マホイップ
    if "alcremie" in poke_name:
        poke_name = "alcremie"

    # ウーラオス
    if "urshifu" in poke_name:
        poke_name = "urshifu"

    return poke_name


if __name__ == "__main__":
    # リプレイのhtmlから構築と選出を抽出し、DataFrameにまとめる
    result_dict = retrieve_party_from_html()

    # 構築と選出の情報をcsvで出力する
    with open("./data/intermediate/0_original/pick_and_party_data.json", mode="w") as f:
        d = json.dumps(result_dict)
        f.write(d)
