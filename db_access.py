# -*- coding: utf-8 -*-
import sqlite3

#------------------------------------------------------------------------------------
# DBアクセスクラス
#------------------------------------------------------------------------------------
class DBAccess:
    # データベースファイルのパス
    db_path = 'sample_db.sqlite'

    #------------------------------------------------------------------------------------
    # DB接続
    #------------------------------------------------------------------------------------
    def connect(self):
        # データベース接続とカーソル生成
        self.connection = sqlite3.connect(self.db_path)
        self.connection.text_factory = str
        self.cursor = self.connection.cursor()
        # 外部キー制約を有効にする
        self.cursor.execute('PRAGMA foreign_keys = 1')

    #------------------------------------------------------------------------------------
    # SQL発行
    #------------------------------------------------------------------------------------
    def execute(self, sql_str):
        #print(sql_str)
        self.cursor.execute(sql_str)

    #------------------------------------------------------------------------------------
    # 1件取得
    #------------------------------------------------------------------------------------
    def fetchone(self):
        return self.cursor.fetchone()

    #------------------------------------------------------------------------------------
    # 全件取得
    #------------------------------------------------------------------------------------
    def fetchall(self):
        return self.cursor.fetchall()

    #------------------------------------------------------------------------------------
    # コミット
    #------------------------------------------------------------------------------------
    def commit(self):
        # コミット
        self.connection.commit()

    #------------------------------------------------------------------------------------
    # DB切断
    #------------------------------------------------------------------------------------
    def close(self):
        # データベース切断
        self.connection.close()

    #------------------------------------------------------------------------------------
    # テーブル作成処理
    #------------------------------------------------------------------------------------
    def create(self):
        # キーワードテーブル作成
        self.execute('CREATE TABLE IF NOT EXISTS key_table \
        (keyword TEXT)')
        # ファイル情報テーブル作成
        self.execute('CREATE TABLE IF NOT EXISTS file_table \
        (dir_path TEXT, file_name TEXT, mtime REAL)')
        # 索引付け結果テーブル作成
        self.execute('CREATE TABLE IF NOT EXISTS result_table \
        (id INTEGER PRIMARY KEY, keyword TEXT, dir_path TEXT, file_name TEXT, row_no INTEGER, start INTEGER, end INTEGER)')
        # 削除結果テーブル
        self.execute('CREATE TABLE IF NOT EXISTS drop_result_table \
        (id INTEGER PRIMARY KEY)')

    #------------------------------------------------------------------------------------
    # 検索処理
    #------------------------------------------------------------------------------------
    def select(self, selectsql):
        # SQL発行
        self.execute(selectsql)

        # 結果取得
        select_result = self.fetchall()

        return select_result

    #------------------------------------------------------------------------------------
    # 索引キーワード検索
    #------------------------------------------------------------------------------------
    def select_keyword(self):
        # SQL発行
        return self.select('SELECT keyword FROM key_table ORDER BY keyword ASC')

    #------------------------------------------------------------------------------------
    # ディレクトリパス検索
    #------------------------------------------------------------------------------------
    def select_dir_path(self, file_name=None):
        # SQL文生成
        str_sql = 'SELECT DISTINCT dir_path FROM file_table'

        if file_name:
            str_sql = str_sql + ' WHERE file_name="{}"'.format(file_name)

        str_sql = str_sql + ' ORDER BY dir_path ASC'

        # SQL発行
        return self.select(str_sql)

    #------------------------------------------------------------------------------------
    # ファイル名検索
    #------------------------------------------------------------------------------------
    def select_file_name(self, dir_path=None):
        # SQL文生成
        str_sql = 'SELECT DISTINCT file_name FROM file_table'

        if dir_path:
            str_sql = str_sql + ' WHERE dir_path="{}"'.format(dir_path)

        str_sql = str_sql + ' ORDER BY file_name ASC'

        # SQL発行
        return self.select(str_sql)

    #------------------------------------------------------------------------------------
    # ファイル情報検索
    #------------------------------------------------------------------------------------
    def select_by_file_path(self, dir_path, file_name):
        # SQL発行
        return self.select('SELECT * FROM file_table WHERE dir_path="{0}" AND file_name="{1}"'.format(dir_path, file_name))

    #------------------------------------------------------------------------------------
    # 検索結果検索
    #------------------------------------------------------------------------------------
    def select_result(self, keyword=None, dir_path=None, file_name=None):
        # SQL文生成
        str_sql = 'SELECT keyword, dir_path, file_name, row_no, start, end FROM result_table left outer join drop_result_table on (result_table.id = drop_result_table.id)'

        cnt_where = 0

        if keyword or dir_path or file_name:
            str_sql = str_sql + ' WHERE drop_result_table.id is null'

        if keyword:
            str_sql = str_sql + ' AND keyword="{}"'.format(keyword)
            cnt_where = cnt_where + 1

        if dir_path:
            str_sql = str_sql + ' AND dir_path="{}"'.format(dir_path)
            cnt_where = cnt_where + 1

        if file_name:
            str_sql = str_sql + ' AND file_name="{}"'.format(file_name)

        # SQL発行
        return self.select(str_sql)

    #------------------------------------------------------------------------------------
    # ファイル情報登録
    #------------------------------------------------------------------------------------
    def insert_file_record(self, dir_path, file_name, mtime):
        # SQL発行
        self.execute('INSERT INTO file_table VALUES ("{0}", "{1}", {2})'.format(dir_path, file_name, mtime))

    #------------------------------------------------------------------------------------
    # ファイル情報更新
    #------------------------------------------------------------------------------------
    def update_file_record(self, dir_path, file_name, mtime):
        # SQL発行
        self.execute('UPDATE file_table SET mtime={0} WHERE dir_path="{1}" AND file_name="{2}"'.format(mtime, dir_path, file_name))

    #------------------------------------------------------------------------------------
    # 索引キーワード登録
    #------------------------------------------------------------------------------------
    def insert_keyward(self, keyword):
        # SQL発行
        self.execute('INSERT INTO key_table (keyword) SELECT "{0}" WHERE NOT EXISTS (SELECT 1 from key_table WHERE keyword="{0}")'.format(keyword))

    #------------------------------------------------------------------------------------
    # ファイル情報登録
    #------------------------------------------------------------------------------------
    def insert_result_record(self, keyword, dir_path, file_name, row_no, start, end):
        # SQL発行
        self.execute('INSERT INTO result_table(keyword, dir_path, file_name, row_no, start, end) VALUES ("{0}", "{1}", "{2}", {3}, {4}, {5})'.format(keyword, dir_path, file_name, row_no, start, end))

    #------------------------------------------------------------------------------------
    # キーワード関連情報削除
    #------------------------------------------------------------------------------------
    def delete_by_key(self, key):
        # SQL発行
        self.execute('DELETE FROM result_table WHERE keyword="{}"'.format(key))
        self.execute('DELETE FROM key_table WHERE keyword="{}"'.format(key))

    #------------------------------------------------------------------------------------
    # ファイル情報削除
    #------------------------------------------------------------------------------------
    def delete_result_record(self, keyword, dir_path, file_name):
        # SQL発行
        self.execute('INSERT OR IGNORE INTO drop_result_table SELECT id FROM result_table WHERE keyword="{0}" AND dir_path="{1}" AND file_name="{2}"'.format(keyword, dir_path, file_name))
#        self.execute('SELECT id FROM result_table WHERE keyword="{0}" AND dir_path="{1}" AND file_name="{2}"'.format(keyword, dir_path, file_name))

    #------------------------------------------------------------------------------------
    # 全レコード削除処理
    #------------------------------------------------------------------------------------
    def delete_all_recored(self):
        # 索引付け結果レコード削除
        self.execute('DELETE FROM result_table')
        # キーワードレコード削除
        self.execute('DELETE FROM key_table')
        # ファイル情報レコード削除
        self.execute('DELETE FROM file_table')
        # 削除レコード削除
        self.execute('DELETE FROM drop_result_table')

