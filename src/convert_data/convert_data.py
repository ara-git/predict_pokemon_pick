import numpy as np
import pandas as pd
import json
import collections


class convert_data:
    def __init__(self) -> None:
        # jsonファイルを読み込む
        self._read_json_files()

        # 計算対象とする、データが十分に集まったポケモンを調べる
        self._extract_major_poke()

        print("データが十分に集まったポケモン:", self.major_poke_list)
        return

    def _read_json_files(self):
        """JSONファイルを読み込む"""
        # ポケモン図鑑
        with open(
            "./data/input/stock/pokedex/pokedex.json", "r", encoding="utf-8"
        ) as file:
            pokedex = json.load(file)
        self.pokedex = pokedex["Pokedex"]

        with open(
            "./data/input/stock/pokedex/all_types.json", "r", encoding="utf-8"
        ) as file:
            all_types = json.load(file)
        # ポケモン全タイプのリスト
        self.all_types = all_types["all_types"]

        # 選出
        # JSONファイルを読み込む
        with open(
            "./data/intermediate/0_original/pick_and_party_data.json",
            "r",
            encoding="utf-8",
        ) as file:
            self.pick_and_party = json.load(file)

    def _get_type(self, poke_name):
        """
        ポケモン名を入力として、タイプのリストを返す
        """
        # ポケモン名を正規化
        poke_name = self._standardize_poke_name(poke_name)

        if poke_name == "urshifu":
            # ウーラオスは例外処理として、3タイプ分計上
            return ["Dark", "Water", "Fighting"]

        if poke_name in self.pokedex.keys():
            return self.pokedex[poke_name]["types"]
        else:
            print(poke_name, "は図鑑にないポケモンです")

    def _get_speed(self, poke_name):
        """
        ポケモン名を入力として、タイプのリストを返す
        """
        # ポケモン名を正規化
        poke_name = self._standardize_poke_name(poke_name)

        if poke_name in self.pokedex.keys():
            return self.pokedex[poke_name]["baseStats"]["spe"]
        else:
            print(poke_name, "は図鑑にないポケモンです")

    def _get_abilities(self, poke_name):
        """
        ポケモン名を入力として、特性のリストを返す
        """
        # ポケモン名を正規化
        poke_name = self._standardize_poke_name(poke_name)

        if poke_name in self.pokedex.keys():
            return self.pokedex[poke_name]["abilities"].values
        else:
            print(poke_name, "は図鑑にないポケモンです")

    def _standardize_poke_name(self, poke_name):
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

        if "tatsugiri" in poke_name:
            poke_name = "tatsugiri"
        return poke_name

    def _extract_major_poke(self):
        """
        データが十分に集まったポケモンを抽出する
        """
        # 全構築データ内のポケモンをリスト化して集計
        poke_list = []
        for data_index, data in self.pick_and_party.items():
            poke_list += data["opponent_party"]

        # データ数の辞書に直す
        poke_dict = collections.Counter(poke_list)

        major_poke_list = []

        for key, value in poke_dict.items():
            # データが50個以上存在しているなら、計算対象とする
            if value >= 50:
                major_poke_list.append(key)

        self.major_poke_list = major_poke_list

        # csvファイルとして保存する
        pd.DataFrame(self.major_poke_list, columns = ["poke_name"]).to_csv("./data/intermediate/1_preprocessed/major_poke.csv")

    def make_DataFrame(self, poke_name):
        """
        対戦データをDataframe形式に変換する
        poke_name: 分析対象（選出予測する対象となる）ポケモン
        """
        picked_TF_df = pd.DataFrame([])
        start_picked_TF_df = pd.DataFrame([])
        type_count_df = pd.DataFrame([])
        max_speed_df = pd.DataFrame([])
        mean_speed_df = pd.DataFrame([])
        min_speed_df = pd.DataFrame([])
        ChienPao_Dragonite_df = pd.DataFrame([])
        Tornadus_Urshifu_df = pd.DataFrame([])
        FlutterMane_ChiYu_df = pd.DataFrame([])
        Indeedee_Armarouge_df = pd.DataFrame([])
        my_party_df = pd.DataFrame([])

        # 対戦単位ごとに読み込み、特徴量を作成する
        for data_index, data in self.pick_and_party.items():
            # 構築に入っているかどうかを判定
            if poke_name in data["opponent_party"]:
                "選出されたかどうか"
                picked_TF = int(poke_name in data["opponent_pick"])

                "初手に選出されたかどうか"
                start_picked_TF = int(poke_name in data["opponent_start_pick"])

                "自構築内のタイプの数をカウントする"
                type_count_dict = dict(zip(self.all_types, [0] * len(self.all_types)))
                for my_poke in data["my_party"]:
                    my_poke_type = self._get_type(my_poke)
                    for each_my_poke_type in my_poke_type:
                        # タイプのvalueを加算する
                        type_count_dict[each_my_poke_type] += 1

                "素早さ種族値について"
                my_team_speed_list = []
                for my_poke in data["my_party"]:
                    my_poke_speed = self._get_speed(my_poke)
                    my_team_speed_list.append(my_poke_speed)

                # 最大値
                max_speed = max(my_team_speed_list)
                # 平均値
                mean_speed = np.mean(my_team_speed_list)
                # 最小値
                min_speed = min(my_team_speed_list)

                "特定の並びの存在"
                # パオカイリュー
                ChienPao_Dragonite_TF = int(
                    ("Chien-Pao" in data["my_party"])
                    and ("Dragonite" in data["my_party"])
                )

                # トルネウーラ
                Tornadus_Urshifu_TF = int(
                    ("Tornadus" in data["my_party"]) and ("Urshifu" in data["my_party"])
                )

                # カミイーユイ
                FlutterMane_ChiYu_TF = int(
                    ("Flutter Mane" in data["my_party"])
                    and ("Chi-Yu" in data["my_party"])
                )

                # グレンアルマイエッサン
                Indeedee_Armarouge_TF = int(
                    ("Indeedee-F" in data["my_party"])
                    and ("Armarouge" in data["my_party"])
                )

            else:
                continue

            "DataFrameに変換し、下に蓄積する"
            # 選出されたかどうか
            picked_TF_df = pd.concat([picked_TF_df, pd.DataFrame([picked_TF])])

            # 初手に選出されたかどうか
            start_picked_TF_df = pd.concat(
                [start_picked_TF_df, pd.DataFrame([start_picked_TF])]
            )
            # タイプカウント
            type_count_df = pd.concat(
                [type_count_df, pd.DataFrame([type_count_dict])], axis=0
            )
            # 素早さ最大値
            max_speed_df = pd.concat([max_speed_df, pd.DataFrame([max_speed])], axis=0)
            # 素早さ平均値
            mean_speed_df = pd.concat(
                [mean_speed_df, pd.DataFrame([mean_speed])], axis=0
            )
            # 素早さ最小値
            min_speed_df = pd.concat([min_speed_df, pd.DataFrame([min_speed])], axis=0)

            # 特定の並び
            ChienPao_Dragonite_df = pd.concat(
                [ChienPao_Dragonite_df, pd.DataFrame([ChienPao_Dragonite_TF])]
            )
            Tornadus_Urshifu_df = pd.concat(
                [Tornadus_Urshifu_df, pd.DataFrame([Tornadus_Urshifu_TF])]
            )
            FlutterMane_ChiYu_df = pd.concat(
                [FlutterMane_ChiYu_df, pd.DataFrame([FlutterMane_ChiYu_TF])]
            )
            Indeedee_Armarouge_df = pd.concat(
                [Indeedee_Armarouge_df, pd.DataFrame([Indeedee_Armarouge_TF])]
            )
            # 自分の構築を参考情報として残す
            my_party_df = pd.concat([my_party_df, pd.DataFrame([str(data["my_party"])])], axis=0)

        # 手直し
        picked_TF_df.columns = ["picked"]
        start_picked_TF_df.columns = ["start_pick"]
        max_speed_df.columns = ["max_speed"]
        mean_speed_df.columns = ["mean_speed"]
        min_speed_df.columns = ["min_speed"]
        ChienPao_Dragonite_df.columns = ["ChienPao_Dragonite"]
        Tornadus_Urshifu_df.columns = ["Tornadus_Urshifu"]
        FlutterMane_ChiYu_df.columns = ["FlutterMane_ChiYu"]
        Indeedee_Armarouge_df.columns = ["Indeedee_Armarouge"]
        my_party_df.columns = ["my_party"]

        # 特徴量のデータフレームを横に結合する
        result_df = pd.concat(
            [
                picked_TF_df,
                start_picked_TF_df,
                type_count_df,
                max_speed_df,
                mean_speed_df,
                min_speed_df,
                ChienPao_Dragonite_df,
                Tornadus_Urshifu_df,
                FlutterMane_ChiYu_df,
                Indeedee_Armarouge_df,
                my_party_df
            ],
            axis=1,
        )

        # indexを振りなおす
        result_df.reset_index(inplace=True, drop=True)
        return result_df


if __name__ == "__main__":
    instance = convert_data()

    for object_poke_name in instance.major_poke_list:
        df = instance.make_DataFrame(poke_name=object_poke_name)
        df.to_csv(
            "./data/intermediate/1_preprocessed/preprocessed_"
            + object_poke_name
            + ".csv"
        )
