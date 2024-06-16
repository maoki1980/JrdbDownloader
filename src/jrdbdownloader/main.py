import os
import re
import zipfile

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from tqdm import tqdm


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


def download_and_extract_zip(zip_urls, download_dir, extract_dir, list_file):
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(extract_dir, exist_ok=True)

    previous_list = read_previous_list(list_file)
    new_urls = [url for url in zip_urls if url not in previous_list]

    for zip_url in tqdm(new_urls, desc="Downloading ZIP files"):
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


jrdb_zip_dir = "../../JRDB_ZIP"
jrdb_txt_dir = "../../JRDB"

# .envファイルからJRDBの認証情報を読み込む
load_dotenv("../../.env")
jrdb_user = os.getenv("JRDB_USER")
jrdb_pass = os.getenv("JRDB_PASS")

# 前日系データ JRDBデータパック (Paci) のダウンロード
page_url = "http://www.jrdb.com/member/datazip/Paci/index.html"
base_url = "http://www.jrdb.com/member/datazip/Paci/"
zip_urls = get_zip_links(page_url, base_url)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Paci"),
    os.path.join(jrdb_txt_dir, "Paci"),
    os.path.join(jrdb_zip_dir, "Paci", "list.txt"),
)

# 前日系データ 3連単基準オッズデータ (OV) のダウンロード
page_url = "http://www.jrdb.com/member/datazip/Ov/index.html"
base_url = "http://www.jrdb.com/member/datazip/Ov/"
zip_urls = get_zip_links(page_url, base_url)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Ov"),
    os.path.join(jrdb_txt_dir, "Ov"),
    os.path.join(jrdb_zip_dir, "Ov", "list.txt"),
)

# 成績系データ JRDB成績データ (SE*) のダウンロード
page_url = "http://www.jrdb.com/member/datazip/Sed/index.html"
base_url = "http://www.jrdb.com/member/datazip/Sed/"
zip_urls = [
    url
    for url in get_zip_links(page_url, base_url)
    if not os.path.basename(url).startswith("SED_")
]
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Sed"),
    os.path.join(jrdb_txt_dir, "Sed"),
    os.path.join(jrdb_zip_dir, "Sed", "list.txt"),
)

# 成績系データ JRDB成績拡張データ (SK*) のダウンロード
page_url = "http://www.jrdb.com/member/datazip/Skb/index.html"
base_url = "http://www.jrdb.com/member/datazip/Skb/"
zip_urls = [
    url
    for url in get_zip_links(page_url, base_url)
    if not os.path.basename(url).startswith("SKB_")
]
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Skb"),
    os.path.join(jrdb_txt_dir, "Skb"),
    os.path.join(jrdb_zip_dir, "Skb", "list.txt"),
)

# マスタ系データ用のダウンロードリスト作成
l_numbers = extract_six_digit_numbers(jrdb_zip_dir)

# マスタ系データ JRDB調教師データ (CZA) のダウンロード
base_url_pattern = "http://www.jrdb.com/member/datazip/Cs/{year}/CZA{number}.zip"
zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Cs"),
    os.path.join(jrdb_txt_dir, "Cs"),
    os.path.join(jrdb_zip_dir, "Cs", "list_cz.txt"),
)

# マスタ系データ JRDB調教師データ (CSA) のダウンロード
base_url_pattern = "http://www.jrdb.com/member/datazip/Cs/{year}/CSA{number}.zip"
zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Cs"),
    os.path.join(jrdb_txt_dir, "Cs"),
    os.path.join(jrdb_zip_dir, "Cs", "list_cs.txt"),
)

# マスタ系データ JRDB騎手データ (KZA) のダウンロード
base_url_pattern = "http://www.jrdb.com/member/datazip/Ks/{year}/KZA{number}.zip"
zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Ks"),
    os.path.join(jrdb_txt_dir, "Ks"),
    os.path.join(jrdb_zip_dir, "Ks", "list_kz.txt"),
)

# マスタ系データ JRDB騎手データ (KSA) のダウンロード
base_url_pattern = "http://www.jrdb.com/member/datazip/Ks/{year}/KSA{number}.zip"
zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Ks"),
    os.path.join(jrdb_txt_dir, "Ks"),
    os.path.join(jrdb_zip_dir, "Ks", "list_ks.txt"),
)

# マスタ系データ JRDB抹消馬データ (MZA) のダウンロード
base_url_pattern = "http://www.jrdb.com/member/datazip/Ms/{year}/MZA{number}.zip"
zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Ms"),
    os.path.join(jrdb_txt_dir, "Ms"),
    os.path.join(jrdb_zip_dir, "Ms", "list_mz.txt"),
)

# マスタ系データ JRDB抹消馬データ (MSA) のダウンロード
base_url_pattern = "http://www.jrdb.com/member/datazip/Ms/{year}/MSA{number}.zip"
zip_urls = get_zip_urls_from_numbers(l_numbers, base_url_pattern)
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Ms"),
    os.path.join(jrdb_txt_dir, "Ms"),
    os.path.join(jrdb_zip_dir, "Ms", "list_ms.txt"),
)

# 直前系データ JRDB払戻情報データ (HJ*) のダウンロード
page_url = "http://www.jrdb.com/member/datazip/Hjc/index.html"
base_url = "http://www.jrdb.com/member/datazip/Hjc/"
zip_urls = [
    url
    for url in get_zip_links(page_url, base_url)
    if not os.path.basename(url).startswith("HJC_")
]
print(f"List Length: {len(zip_urls)}")
download_and_extract_zip(
    zip_urls,
    os.path.join(jrdb_zip_dir, "Hjc"),
    os.path.join(jrdb_txt_dir, "Hjc"),
    os.path.join(jrdb_zip_dir, "Hjc", "list.txt"),
)
