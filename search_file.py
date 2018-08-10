# -*- coding: utf-8 -*-
import os
import re

# 検索対象のファイル拡張子
ext_patterns = (
    'txt',
    '.csv',
    '.xml',
    '.sh',
    '.h',
    '.c',
    '.hpp',
    '.cpp',
    '.java',
    '.pl',
    '.pm',
    '.py',
    '.m'
)

#------------------------------------------------------------------------------------
# ファイルリスト取得
#------------------------------------------------------------------------------------
def get_file_list(dir_path):
    file_list = []
    # 指定ディレクトリを再帰的に探索
    for root_dir, _, files in os.walk(dir_path):
        # 検索対象拡張子のファイルを抽出
        sub_file_list = extract_target_files(root_dir, files)
        file_list.extend(sub_file_list)

    return file_list

#------------------------------------------------------------------------------------
# 検索対象ファイル抽出
#------------------------------------------------------------------------------------
def extract_target_files(dir_path, file_list):
    file_path_list = []
    for file_name in file_list:
        # ファイルの拡張子を取得
        _, ext = os.path.splitext(file_name)
        if ext in ext_patterns:
            # 対象拡張子のファイルだけ抽出
            file_path_list.append(os.path.abspath(os.path.join(dir_path, file_name)))

    return file_path_list

#------------------------------------------------------------------------------------
# ファイル内検索処理
#------------------------------------------------------------------------------------
def search(file_path, search_pattern):
    matched_list = []
    with open(file_path,'r',encoding="utf-8") as f:
        lines = f.readlines()

    # ディレクトリパスとファイル名に分離
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    line_number = 1
    for line in lines:
        ite = re.finditer(search_pattern, line)
        for m in ite:
            if m:
                file_info = {
                    'dir_path': dir_path,
                    "file_name": file_name,
                    "line_number": line_number,
                    "line": line.strip(),
                    "group": m.group(),
                    "start": m.start()+1,
                    "end": m.end(),
                    "span": m.span()
                }
                matched_list.append(file_info)
        line_number = line_number + 1

    return matched_list

