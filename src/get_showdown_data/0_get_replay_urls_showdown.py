from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import time
import pandas as pd
import datetime


def get_replay_urls():
    # ルールを指定する
    rule_list = [
        "[Gen 9] VGC 2023 Regulation C",
        "[Gen 9] VGC 2023 Regulation D",
        "[Gen 9] VGC 2023 Regulation E",
        "[Gen 9] VGC 2024 Reg F",
    ]
    # リプレイに関するurlのみ抽出する(8個目以降を取る)
    url_list = []
    for rule in rule_list:
        # ChromeOptionsを設定
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument('--proxy-server="direct://"')
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument("--kiosk")
        # chromeを開かない
        options.add_argument("--headless")

        # Chromeを起動
        print("Chromeを起動中...")
        driver = webdriver.Chrome(options=options)

        # 指定したURLに遷移
        driver.get("https://replay.pokemonshowdown.com/")

        # print(driver.page_source)

        # ルールを入力する
        form = driver.find_element_by_xpath(
            "/html/body/div/div/div/div[1]/section[1]/form/p[2]/label/input"
        )

        # フォームを入力する
        form.send_keys(rule)

        # クリックする
        driver.find_element_by_xpath(
            "/html/body/div/div/div/div[1]/section[1]/form/p[4]/button"
        ).click()

        # 一秒待機
        time.sleep(1)
        count = 0

        for i in range(10):
            try:
                # リンクを取得する
                # aタグのhrefをelementでリスト化
                elements = driver.find_elements_by_xpath("//a[@href]")

                for element in elements:
                    url_list.append(element.get_attribute("href"))

                # 進捗確認
                count += 1
                print(count, "ページ目")

                # 次のページに飛ぶ
                driver.find_element_by_xpath(
                    "/html/body/div/div/div/div[1]/section/form/p[6]/a"
                ).click()

                # 2秒待機
                time.sleep(2)
            except:
                break

        # Chromeを終了
        driver.quit()

    # DataFrame化する
    # 不要なhtml urlを削除する
    url_list = list(
        filter(lambda x: "https://replay.pokemonshowdown.com/gen9vgc" in x, url_list)
    )
    # 重複を消す
    url_list = list(set(url_list))
    replay_urls = pd.DataFrame(url_list, columns=["url"])
    return replay_urls


if __name__ == "__main__":
    # リプレイのurlを取得する
    replay_urls = get_replay_urls()

    # リプレイのurlをcsvで出力する
    replay_urls.to_csv(
        "./data/flow/replay_urls.csv",
        index=False,
    )
