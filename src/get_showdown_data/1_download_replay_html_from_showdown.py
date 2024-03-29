"""
showdownの各urlにアクセスし、リプレイのhtmlをDownloadフォルダに保存する

注意：
Chlomeを開かないとDLが始まらない
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import time
import pandas as pd
import os
from selenium.webdriver.common.alert import Alert


# options.add_argument("--headless")


def download_replay_html_from_showdown():
    """
    "get_showdown_data/data/replay_urls.csv"のurlを開き、リプレイのhtmlファイルを"get_showdown_data/data/replay_htmls"に保存する。

    エラーで止まりがちなので、try文で書く。
    """
    replay_urls_df = pd.read_csv("./data/input/flow/replay_urls.csv")
    print(replay_urls_df)

    # ChromeOptionsを設定
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument('--proxy-server="direct://"')
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument("--kiosk")
    options.add_argument("--disable-popup-blocking")

    # DL先を指定する
    ## 絶対パスで指定する必要があるので、相対から変換する
    abs_path = os.path.abspath("./data/input/stock/ShowDown_html")
    prefs = {"download.default_directory": abs_path}
    options.add_experimental_option("prefs", prefs)

    # Chromeを起動
    print("Chromeを起動中...")
    driver = webdriver.Chrome(options=options)

    # DLする個数
    n = len(replay_urls_df)
    # テスト用に一旦少ない数で行う。
    # n = 30
    for i in range(n):
        try:
            url = replay_urls_df["url"][i]
            # 指定したURLに遷移
            driver.get(url)

            # ダウンロードボタンをクリックし、リプレイをダウンロードする
            driver.find_element_by_xpath(
                "/html/body/div[1]/div/div/div[1]/div/div[3]/p[3]/a"
            ).click()

            # 5秒待機
            time.sleep(4)
            print(i / n)
            try:
                # 何かしらの操作でアラートが表示される場合
                alert = Alert(driver)

                # アラートを無視する
                alert.dismiss()
            except:
                # 何もしない（アラートが表示されなかった場合や無視した場合）
                pass
        except:
            # 5秒待機
            time.sleep(4)
            try:
                # 何かしらの操作でアラートが表示される場合
                alert = Alert(driver)

                # アラートを無視する
                alert.dismiss()
            except:
                # 何もしない（アラートが表示されなかった場合や無視した場合）
                pass


if __name__ == "__main__":
    # リプレイのurlから、htmlをDLする。
    download_replay_html_from_showdown()
