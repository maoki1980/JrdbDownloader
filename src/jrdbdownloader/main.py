import os
import re
import zipfile
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from tqdm import tqdm

project_path = "../../"
env_file = os.getenv("ENV_FILE", os.path.join(project_path, ".env"))
load_dotenv(env_file)
jrdb_zip_dir = os.getenv("JRDB_ZIP_DIR")
jrdb_txt_dir = os.getenv("JRDB_TXT_DIR")
jrdb_user = os.getenv("JRDB_USER")
jrdb_pass = os.getenv("JRDB_PASS")


def get_zip_links(jrdb_url, base_url):
    response = requests.get(jrdb_url, auth=HTTPBasicAuth(jrdb_user, jrdb_pass))
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    zip_links = soup.find_all("a", href=True)
    return [
        base_url + link["href"] for link in zip_links if link["href"].endswith(".zip")
    ]


def read_previous_list(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read().splitlines()
    return []


def save_current_list(file_path, current_list):
    with open(file_path, "w") as file:
        file.write("\n".join(current_list))


def download_and_extract_zip(zip_urls, download_dir, extract_dir, list_file, category):
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(extract_dir, exist_ok=True)

    previous_list = read_previous_list(list_file)
    new_urls = [url for url in zip_urls if url not in previous_list]

    print(f"List Length of {category}: {len(new_urls)}")
    for zip_url in tqdm(new_urls, desc=f"Downloading ZIP files of {category}"):
        zip_filename = os.path.join(download_dir, os.path.basename(zip_url))

        if not os.path.exists(zip_filename):
            try:
                zip_response = requests.get(
                    zip_url, auth=HTTPBasicAuth(jrdb_user, jrdb_pass)
                )
                zip_response.raise_for_status()

                with open(zip_filename, "wb") as file:
                    file.write(zip_response.content)

                with zipfile.ZipFile(zip_filename, "r") as thezip:
                    thezip.extractall(extract_dir)
            except requests.exceptions.HTTPError as e:
                if zip_response.status_code == 404:
                    continue
                else:
                    print(f"HTTP error occurred: {e}")
                    raise

    save_current_list(list_file, zip_urls)


def get_zip_urls_from_numbers(l_zip_numbers, base_url_pattern):
    zip_urls = []
    for number in l_zip_numbers:
        year_prefix = int(number[:2])
        year = 1900 + year_prefix if year_prefix >= 50 else 2000 + year_prefix
        url = base_url_pattern.format(year=year, number=number)
        zip_urls.append(url)
    return zip_urls


def extract_six_digit_numbers(directory):
    # 正規表現パターン：6桁の数字
    pattern = re.compile(r"\d{6}")
    six_digit_numbers = set()

    # ディレクトリを再帰的に探索
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".zip"):
                # ファイル名から6桁の番号を抽出
                matches = pattern.findall(file)
                if matches:
                    six_digit_numbers.update(matches)

    # リストに変換して降順にソート
    sorted_numbers = sorted(six_digit_numbers, reverse=True)

    return sorted_numbers


def download_category_data(
    page_url,
    base_url,
    download_dir,
    extract_dir,
    list_file,
    category,
    exclusion_prefix=None,
):
    zip_urls = get_zip_links(page_url, base_url)
    if exclusion_prefix:
        zip_urls = [
            url
            for url in zip_urls
            if not os.path.basename(url).startswith(exclusion_prefix)
        ]
    download_and_extract_zip(zip_urls, download_dir, extract_dir, list_file, category)


def main():
    # 環境変数の読み込み確認
    print(f"ENV_FILE: '{env_file}'")
    print(f"JRDB_ZIP_DIR: '{jrdb_zip_dir}'")
    print(f"JRDB_TXT_DIR: '{jrdb_txt_dir}'")

    # スクリプト開始時刻をログとして表示
    print(f"Script started at: {datetime.now()}")

    # 基本URLの定義
    base_jrdb_url = "http://www.jrdb.com/member/datazip"

    # ダウンロードカテゴリの設定
    categories = [
        ("Paci", f"{base_jrdb_url}/Paci/index.html", f"{base_jrdb_url}/Paci/", None),
        ("Ov", f"{base_jrdb_url}/Ov/index.html", f"{base_jrdb_url}/Ov/", None),
        ("Sed", f"{base_jrdb_url}/Sed/index.html", f"{base_jrdb_url}/Sed/", "SED_"),
        ("Skb", f"{base_jrdb_url}/Skb/index.html", f"{base_jrdb_url}/Skb/", "SKB_"),
        ("Hjc", f"{base_jrdb_url}/Hjc/index.html", f"{base_jrdb_url}/Hjc/", "HJC_"),
    ]

    # カテゴリデータのダウンロードと抽出
    for category, page_url, base_url, exclusion_prefix in categories:
        download_category_data(
            page_url,
            base_url,
            os.path.join(jrdb_zip_dir, category),
            os.path.join(jrdb_txt_dir, category),
            os.path.join(jrdb_zip_dir, category, "list.txt"),
            category,
            exclusion_prefix,
        )

    # マスタ系データ用のダウンロードリスト作成
    l_numbers = extract_six_digit_numbers(jrdb_zip_dir)
    master_categories = [
        ("CZA", f"{base_jrdb_url}/Cs/{{year}}/CZA{{number}}.zip", "Cs", "list_cz.txt"),
        ("CSA", f"{base_jrdb_url}/Cs/{{year}}/CSA{{number}}.zip", "Cs", "list_cs.txt"),
        ("KZA", f"{base_jrdb_url}/Ks/{{year}}/KZA{{number}}.zip", "Ks", "list_kz.txt"),
        ("KSA", f"{base_jrdb_url}/Ks/{{year}}/KSA{{number}}.zip", "Ks", "list_ks.txt"),
        ("MZA", f"{base_jrdb_url}/Ms/{{year}}/MZA{{number}}.zip", "Ms", "list_mz.txt"),
        ("MSA", f"{base_jrdb_url}/Ms/{{year}}/MSA{{number}}.zip", "Ms", "list_ms.txt"),
    ]

    # マスタ系データのダウンロードと抽出
    for category, base_url_pattern, dir_name, list_file_name in master_categories:
        zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
        download_and_extract_zip(
            zip_urls,
            os.path.join(jrdb_zip_dir, dir_name),
            os.path.join(jrdb_txt_dir, dir_name),
            os.path.join(jrdb_zip_dir, dir_name, list_file_name),
            category,
        )

    # スクリプト終了時刻をログとして表示
    print(f"\nScript finished at: {datetime.now()}")
    print("==================================================")


# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == "__main__":
    main()
