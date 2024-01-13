# 外部モジュール
import streamlit as st
import pandas as pd
import json
import os
import sys
import pickle
from sklearn.linear_model import LogisticRegression
import plotly.express as px

# from importlib import reload

# 自作モジュール
# 上位階層のフォルダを読み込むために、対象を増やす
sys.path.append("./src")
from convert_data import convert_data

# from split_train_test_data import split_train_test

# reload(convert_data)


class streamlit_app:
    def __init__(self):
        # jsonファイルなどの外部データを読み込む
        self._read_data()
        # アプリのベースを作る
        self._make_app_base()
        # アプリ上で入力した情報を加工して、DataFrame化する
        self._convert_data()
        # アプリで入力した情報を基に、選出されるか予測する
        self._predict_pick()
        # 予測値をアプリ上に出力する
        with self.col_1:
            st.subheader("選出確率と先発確率")
            ## Plotlyを使って棒グラフを作成する
            fig = px.bar(self.pred_result_df, y=["pick", "first_pick"], barmode="group")
            fig.update_layout(xaxis=dict(title=""), yaxis=dict(title=""))
            st.plotly_chart(fig)

    def _convert_data(self):
        """
        streamlit上で入力したデータを予測モデルで渡せるように、加工する
        """
        self.actual_pick_and_party = {0: dict()}
        self.actual_pick_and_party[0]["my_party"] = self.my_party_list

        # 自作モジュールを呼び出し、Dataframe形式に加工する
        convert_data_instance = convert_data.convert_data(
            mode="streamlit_mode", streamlit_input=self.actual_pick_and_party
        )
        self.converted_streamlit_input_df = convert_data_instance.make_DataFrame()

    def _read_data(self):
        """
        データを読み込む
        """
        # データが十分に集まったポケモンリストを読み込む
        self.data_enough_poke_list = pd.read_csv(
            "./data/intermediate/1_preprocessed/enough_data_poke.csv"
        )["poke_name"]

        # ポケモン図鑑
        with open(
            "./data/input/stock/pokedex/pokedex.json", "r", encoding="utf-8"
        ) as file:
            pokedex = json.load(file)
        self.pokedex = pokedex["Pokedex"]

        # 日英対応表
        self.poke_name_JP_EN = pd.read_csv(
            "./data/input/stock/pokedex/pokename_JP_EN.csv"
        )
        self.poke_name_JP_to_EN_dict = dict(
            zip(self.poke_name_JP_EN["日本語名"], self.poke_name_JP_EN["英語名"])
        )
        # キーと値を反転版
        self.poke_name_EN_to_JP_dict = {
            v: k for k, v in self.poke_name_JP_to_EN_dict.items()
        }
        # st.write(self.poke_name_EN_to_JP_dict)

    def _make_app_base(self):
        """
        アプリのインターフェイスを作る
        """
        # タイトル
        st.title("ポケモンSV ダブルバトル選出予測")

        # 自分の構築を入力する
        my_party_list = []
        for i in range(6):
            # selectboxから入力する
            my_party_poke = st.sidebar.selectbox(
                key="my_party_poke" + str(i),
                label="自分のポケモン" + str(i + 1),
                options=self.poke_name_JP_to_EN_dict.keys(),
            )
            # 日本語の入力を英語に変換
            my_party_poke = self.poke_name_JP_to_EN_dict[my_party_poke]
            my_party_list.append(my_party_poke)
        self.my_party_list = my_party_list

        # 横に2列並べる
        self.col_0, self.col_1 = st.columns((1, 2))

        # 1列目
        with self.col_0:
            # 相手の構築を入力する
            opponent_party_list = []
            for i in range(6):
                # selectboxから入力する
                opponent_party_poke = st.selectbox(
                    key="opponent_party_poke_" + str(i),
                    label="相手のポケモン" + str(i + 1),
                    options=[
                        self.poke_name_EN_to_JP_dict[poke_name]
                        for poke_name in self.data_enough_poke_list
                    ],
                )
                # 日本語の入力を英語に変換する
                opponent_party_poke = self.poke_name_JP_to_EN_dict[opponent_party_poke]
                opponent_party_list.append(opponent_party_poke)
            self.opponent_party_list = opponent_party_list

            # 重複するデータは消去する（順序はそのまま）
            self.opponent_party_list = list(dict.fromkeys(self.opponent_party_list))

    def _predict_pick(self):
        """
        選出確率を予測する
        """
        # 結果を格納するDF
        self.pred_result_df = pd.DataFrame(
            [],
            index=[self.poke_name_EN_to_JP_dict[x] for x in self.opponent_party_list],
        )

        # 予測対象とする変数を変えながら予測
        for predict_object_column in ["start_pick", "picked"]:
            # 予測結果を格納するリスト
            pred_result_list = []

            # 被説明変数を選択
            y = self.converted_streamlit_input_df.loc[:, predict_object_column]

            # 予測対象とするポケモンを変えながら予測
            for object_poke_name in self.opponent_party_list:
                # 説明変数を選択
                X = self.converted_streamlit_input_df.drop(
                    ["start_pick", "picked", "my_party", "mean_speed"], axis=1
                )

                # Logistic Regression
                # 標準化に使うScalerを解凍
                scaler_X = pickle.load(
                    open("./data/LR_scaler/scaler_" + object_poke_name + ".pkl", "rb")
                )
                # 説明変数を標準化
                X = scaler_X.transform(X)
                # 予測器を解凍
                LR_model = pickle.load(
                    open(
                        "./data/trained_models/LR_model_"
                        + predict_object_column
                        + "_"
                        + object_poke_name
                        + ".pkl",
                        "rb",
                    )
                )

                # 予測（確率で返す）
                y_pred = LR_model.predict_proba(X)[0][1]
                pred_result_list.append(y_pred)

            self.pred_result_df[predict_object_column] = pred_result_list

            # ［一時的処理］列名を変える
            self.pred_result_df.rename(
                {"start_pick": "first_pick", "picked": "pick"}, axis=1, inplace=True
            )


# アプリを実行
instance = streamlit_app()
