"外部モジュール"
import streamlit as st
import pandas as pd
import json
import os
import sys
from importlib import reload

"自作モジュール"
# 上位階層のフォルダを読み込むために、対象を増やす
sys.path.append("./src")
from convert_data import convert_data
reload(convert_data)

class streamlit_app:
    def __init__(self):
        self._read_data()
        self._make_app_base()
        self._convert_data()
        st.write(self.actual_pick_and_party)

    def _convert_data(self):
        """
        streamlit上で入力したデータを予測モデルで渡せるように、加工する
        """
        self.actual_pick_and_party = {0: dict()}
        self.actual_pick_and_party[0]["my_party"] = self.my_party_list
        
        # 自作モジュールを呼び出し、Dataframe形式に加工する
        convert_data_instance = convert_data.convert_data(mode = "streamlit_mode", streamlit_input = self.actual_pick_and_party)
        df = convert_data_instance.make_DataFrame(poke_name = self.opponent_party_list[0])
        st.write(df)

    def _read_data(self):
        """
        データを読み込む
        """
        # データが十分に集まったポケモンリストを読み込む
        self.data_enough_poke_list = pd.read_csv("./data/intermediate/1_preprocessed/enough_data_poke.csv")["poke_name"]
    
        # ポケモン図鑑
        with open(
            "./data/input/stock/pokedex/pokedex.json", "r", encoding="utf-8"
        ) as file:
            pokedex = json.load(file)
        self.pokedex = pokedex["Pokedex"]

    
    def _make_app_base(self):
        """
        アプリのインターフェイスを作る
        """
        # タイトル
        st.title("ダブルバトル選出予測")

        # 自分の構築を入力する
        my_party_list = []
        for i in range(6):
            # selectboxから入力する
            my_party_poke = st.sidebar.selectbox(
                key = "my_party_poke" + str(i),
                label = "自分の構築" + str(i + 1),
                options = self.pokedex.keys()
            )
            my_party_list.append(my_party_poke)
        self.my_party_list = my_party_list
                
        "横に2列並べる"
        col_0, col_1 = st.columns((1, 1))

        # 1列目
        with col_0:
            # 相手の構築を入力する
            opponent_party_list = []
            for i in range(6):
                # selectboxから入力する
                opponent_party_poke = st.selectbox(
                    key = "opponent_party_poke_" + str(i),
                    label = "相手の構築" + str(i + 1),
                    options = self.data_enough_poke_list
                )
                opponent_party_list.append(opponent_party_poke)
            self.opponent_party_list = opponent_party_list

instance = streamlit_app()

"""
# 合計ボタン
if st.button("合計"):
    # 合計ボタンが押されたら数値を合計し表示
    total = value_1 + value_2
    st.write(f"合計値: {total}")


"""