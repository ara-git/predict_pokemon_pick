import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import pickle
import lightgbm as lgb

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
        self.predict_object_column = predict_object_column 
        # 説明変数を選択(不要な列を削除)
        X = self.df.drop(['start_pick', "picked", "my_party"] ,axis=1)
        X = self.df.drop(['start_pick', "picked", "my_party", "mean_speed"] ,axis=1)
        self.X = X
        # 被説明変数を選択
        y = self.df.loc[:, predict_object_column]
        self.y = y

        # データを分割する
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size = test_size, random_state = 0) 

    def _standardize_data(self):
        #説明変数は標準化しておく(あとで回帰係数を比較するため)
        scaler_X = StandardScaler()
        self.X_train = scaler_X.fit_transform(self.X_train)
        self.X_test = scaler_X.transform(self.X_test)

    def train_data(self, model):
        """
        データを学習する
        """
        self.model = model
        if self.model == "LR":
            self._train_data_LR()
        elif self.model == "GBDT":
            self._train_data_GBDT()

    def _train_data_LR(self):
        """
        ロジスティック回帰を行い、データを学習する
        """
        # 学習データを標準化しておく
        self._standardize_data()

        #モデルの構築と学習
        self.LR_model = LogisticRegression() 
        self.LR_model.fit(self.X_train, self.y_train)
        
        # pklファイルとして出力する
        pickle.dump(self.LR_model, open("./data/trained_models/LR_model_" + self.predict_object_column + "_" +  self.poke_name + ".pkl", 'wb'))

    def _train_data_GBDT(self):
        """
        勾配ブースティング木でデータを予測する
        """
        # LightGBM のハイパーパラメータ
        params = {
            # 二値分類問題
            'objective': 'binary',
            # AUC の最大化を目指す
            'metric': 'auc',
            # Fatal の場合出力
            'verbosity': -1,
        }

        # 訓練データを更に、LightGBM用の訓練データとテストデータに分割する
        X_train, X_test, y_train, y_test = train_test_split(self.X_train, self.y_train, test_size = 0.3)

        # データセットを生成する
        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

        # 上記のパラメータでモデルを学習する
        self.GBDT_model = lgb.train(params, lgb_train, valid_sets=lgb_eval,
                        num_boost_round=1000,  # 最大イテレーション回数指定

                        )

        
    def predict_data(self):
        """
        作成した予測モデルを使って、予測する
        """
        # 訓練データ,テストデータに対する予測を行う
        if self.model == "LR":
            self.y_pred_train = self.LR_model.predict(self.X_train)
            self.y_pred_test = self.LR_model.predict(self.X_test)

        elif self.model == "GBDT":
            self.y_pred_train = self.GBDT_model.predict(self.X_train, num_iteration=self.GBDT_model.best_iteration)
            self.y_pred_test = self.GBDT_model.predict(self.X_test, num_iteration=self.GBDT_model.best_iteration)
            # 0,1に変換する
            self.y_pred_train = np.where(self.y_pred_train >= 0.5, 1, 0)
            self.y_pred_test = np.where(self.y_pred_test >= 0.5, 1, 0)

    def analyze_model(self):
        """
        作成したモデルを分析する
        """
        if self.model == "LR":
            #回帰係数を格納したpandasDataFrameの表示
            df_coef =  pd.DataFrame({'coefficient':self.LR_model.coef_.flatten()}, index=self.X.columns)
            df_coef['coef_abs'] = abs(df_coef['coefficient'])
            df_coef.sort_values(by='coef_abs', ascending=True,inplace=True)
            df_coef = df_coef.iloc[-10:,:]

            #グラフの作成
            plt.clf()
            x_pos = np.arange(len(df_coef))

            fig = plt.figure(figsize=(6,6))
            ax1 = fig.add_subplot(1, 1, 1)
            ax1.barh(x_pos, df_coef['coefficient'], color='b')
            ax1.set_title('coefficient of variables',fontsize=18)
            ax1.set_yticks(x_pos)
            ax1.set_yticks(np.arange(-1,len(df_coef.index))+0.5, minor=True)
            ax1.set_yticklabels(df_coef.index, fontsize=14)
            ax1.set_xticks(np.arange(-10,11,2)/10)
            ax1.set_xticklabels(np.arange(-10,11,2)/10,fontsize=12)
            ax1.grid(which='minor',axis='y',color='black',linestyle='-', linewidth=1)
            ax1.grid(which='major',axis='x',linestyle='--', linewidth=1)
            plt.savefig("./data/LR_coef/LR_coef_" + self.predict_object_column + "_" + self.poke_name + ".jpg")
            
        elif self.model == "GBDT":
            "（おまけ）特徴量の重要度を出力する"
            # 重要度をモデルから抽出
            importance_df = pd.DataFrame(self.GBDT_model.feature_importance(), index = self.X_train.columns, columns = ["importance"])
            # 特に重要なものだけ抜き出す
            importance_df.sort_values("importance", inplace = True, ascending = False)
            importance_df = importance_df.head(5)
            print(importance_df)

            # 棒グラフにして出力
            plt.clf()
            plt.bar(x = importance_df.index, height = importance_df["importance"])
            plt.savefig("./data/feature_importance/feature_importance_" + self.predict_object_column + "_" + self.poke_name + ".jpg")

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
    # 分析対象にできる、充分にデータが集まったポケモンのリストを作る
    object_poke_list = pd.read_csv("./data/intermediate/1_preprocessed/major_poke.csv")["poke_name"]
    
    for poke_name in object_poke_list:
        # 分析対象とする各ポケモンについて、学習とテストを行う
        print("poke_name:", poke_name)

        # 対象のポケモンについて、インスタンスを作成
        instance = split_train_test(poke_name)

        # 複数モデルで学習、予測を行う
        for model in ["LR", "GBDT"]:
            print("model:", model)
            # データを分割
            instance.split_data(predict_object_column = "start_pick")
            # データ学習
            instance.train_data(model)
            # 予測を行う
            instance.predict_data()
            # 
            instance.analyze_model()
            # 結果を評価する
            instance.evaluate_test()
            #
            print("#####################")