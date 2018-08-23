# -*- coding: utf8 -*-

import os
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fdialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as tkst
from tkinter import Toplevel

import db_access
import search_file
import sample

#------------------------------------------------------------------------------------
# ファイルリスト検索処理
#------------------------------------------------------------------------------------
#@profile
def search_files(file_path_list, pattern):
    # 索引情報作成
    matched_array = []
    for file_path in file_path_list:
        # 検索
        matched = search_file.search(file_path, pattern)
        matched_array.append(matched)

    for file_path in file_path_list:
        # ディレクトリパスとファイル名に分離
        dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        # ファイル情報をDBに登録
        regist_file_info(dir_path, file_name)

    db_accessor.commit()

    for matched in matched_array:
        if matched:
            # 同一キーワード、同一ファイルの検索結果を削除
            delete_result(pattern, matched[0]['dir_path'], matched[0]['file_name'])

        # 検索結果登録
        for dat in matched:
            regist_result(pattern, dat['dir_path'], dat['file_name'], dat['line_number'], dat['start'], dat['end'])

    db_accessor.commit()

#------------------------------------------------------------------------------------
# ファイル情報登録処理
#------------------------------------------------------------------------------------
#@profile
def regist_file_info(dir_path, file_name):
    # DB検索
    rec = db_accessor.select_by_file_path(dir_path, file_name)

    # ファイルの更新時刻(エポック秒)取得
    mtime = os.path.getmtime(os.path.join(dir_path, file_name))

    if rec: # 登録済みの場合
        # 更新
        db_accessor.update_file_record(dir_path, file_name, mtime)
    else:   # 未登録の場合
        # 追加
        db_accessor.insert_file_record(dir_path, file_name, mtime)

#------------------------------------------------------------------------------------
# 検索結果登録処理
#------------------------------------------------------------------------------------
def regist_result(keyword, dir_path, file_name, row_no, start, end):
    # 検索結果登録
    db_accessor.insert_result_record(keyword, dir_path, file_name, row_no, start, end)

def delete_result(keyword, dir_path, file_name):
    # 検索結果削除
    db_accessor.delete_result_record(keyword, dir_path, file_name)

#------------------------------------------------------------------------------------
# 検索関数
#------------------------------------------------------------------------------------
#@profile
def search_file_interface(directory, keyword):
    stratTime = time.time()
    db_accessor.insert_keyward(keyword)

    # 指定ディレクトリ下のファイルリスト取得
    file_list = search_file.get_file_list(directory)

    # 検索、索引作成
    search_files(file_list, keyword)

    endTime = time.time()
    print('処理時間（索引作成）：{}[sec]'.format(endTime - stratTime))

# テストのエントリー
if __name__ ==  "__main__":
    # DBアクセサ作成
    db_accessor = db_access.DBAccess()
    # DB接続
    db_accessor.connect()
    # DBがない場合、作成する
    db_accessor.create()
    # コミット
    db_accessor.commit()

    search_file_interface("/mnt/c/r/home/ryo/dev/procon/postgresql-10.4", "insert")
    search_file_interface("/mnt/c/r/home/ryo/dev/procon/postgresql-10.4", "return")

    # DB切断
    db_accessor.close()
