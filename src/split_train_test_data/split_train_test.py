import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import pickle


class split_train_test:
    def __init__(self, poke_name):
        self.poke_name = poke_name
        # csvファイルを読み込む
        self._read_csv()

    def _read_csv(self):
        """
        加工済みのポケモンcsv対戦データを読み込む
        Args
            poke_name: 対象とするポケモン名
        """
        self.df = pd.read_csv("./data/intermediate/1_preprocessed/preprocessed_" + self.poke_name + ".csv", index_col = 0)

    def split_data(self, test_size = 0.2, predict_object_column = "start_pick"):
        """
        データを分割し、学習データとテストデータとする
        Args
            test_size: テストデータのサイズ
            predict_object_column: 予測対象とする列（デフォルトは先発）
        """
        # 説明変数を選択(不要な列を削除)
        X = self.df.drop(['start_pick', "picked", "my_party"] ,axis=1)

        # 被説明変数を選択
        y = self.df.loc[:, predict_object_column]

        # データを分割する
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size = test_size, random_state = 0) 

    def _standardize_data(self):
        #説明変数は標準化しておく(あとで回帰係数を比較するため)
        scaler_X = StandardScaler()
        self.X_train = scaler_X.fit_transform(self.X_train)
        self.X_test = scaler_X.transform(self.X_test)

    def train_data_logistic(self):
        """
        ロジスティック回帰を行い、データを学習する
        """
        # 学習データを標準化しておく
        self._standardize_data()

        #モデルの構築と学習
        self.LR_model = LogisticRegression() 
        self.LR_model.fit(self.X_train, self.y_train)
        
        # pklファイルとして出力する
        pickle.dump(self.LR_model, open("./data/trained_models/LR_model_" + self.poke_name + ".pkl", 'wb'))

    def predict_data(self):
        """
        作成した予測モデルを使って、予測する
        """
        # 訓練データ,テストデータに対する予測を行う
        self.y_pred_train = self.LR_model.predict(self.X_train)
        self.y_pred_test = self.LR_model.predict(self.X_test)
        
    def evaluate_test(self):
        """
        予測結果を評価する
        """
        "コンフュージョンマトリックスを作成し、出力する"
        # 訓練データ
        confusion_matrix_train = confusion_matrix(y_true=self.y_train, y_pred=self.y_pred_train)
        confusion_matrix_train = pd.DataFrame(confusion_matrix_train, index = ["true_0", "true_1"], columns = ["pred_0", "pred_1"])
        print('confusion matrix for train data = \n', confusion_matrix_train)

        #テストデータ
        confusion_matrix_test = confusion_matrix(y_true=self.y_test, y_pred=self.y_pred_test)
        confusion_matrix_test = pd.DataFrame(confusion_matrix_test, index = ["true_0", "true_1"], columns = ["pred_0", "pred_1"])
        print('confusion matrix for test data = \n', confusion_matrix_test)


if __name__ == "__main__":
    # 対象のポケモンについて、インスタンスを作成
    instance = split_train_test("Incineroar")

    # データを分割
    instance.split_data()

    # データ学習
    instance.train_data_logistic()

    # 予測を行う
    instance.predict_data()

    # 結果を評価する
    instance.evaluate_test()