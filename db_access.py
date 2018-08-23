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
        (id INTEGER PRIMARY KEY, keyword TEXT)')
        # ファイル情報テーブル作成
        self.execute('CREATE TABLE IF NOT EXISTS file_table \
        (id INTEGER PRIMARY KEY, dir_path TEXT, file_name TEXT, mtime REAL)')
        # キーワード, ファイル情報更新カウンタ(テーブルのdeleteが遅いので、
        # 索引付結果テーブルは常に追加のみ行い、参照時に当該テーブルのupdate_counterと一致するレコードのみを参照する
        self.execute('CREATE TABLE IF NOT EXISTS update_counter_table \
        (keyword_id INTEGER, file_id INTEGER, update_counter INTEGER, PRIMARY KEY(keyword_id, file_id))')
        # 索引付け結果テーブル作成
        self.execute('CREATE TABLE IF NOT EXISTS result_table \
        (key_file_id INTEGER, row_no INTEGER, start INTEGER, end INTEGER)')

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
        str_sql = 'SELECT   \
        key_table.keyword,   \
        file_table.dir_path,    \
        file_table.file_name,   \
        result_table.row_no,    \
        result_table.start,    \
        result_table.end    \
        FROM result_table   \
        INNER JOIN update_counter_table ON result_table.key_file_id = update_counter_table.update_counter   \
        INNER JOIN key_table ON update_counter_table.keyword_id = key_table.id \
        INNER JOIN file_table on update_counter_table.file_id = file_table.id \
        '

        cnt_where = 0

        if keyword or dir_path or file_name:
            str_sql = str_sql + ' WHERE '

        if keyword:
            str_sql = str_sql + 'key_table.keyword="{}"'.format(keyword)
            cnt_where = cnt_where + 1

        if dir_path:
            if cnt_where > 0:
                str_sql = str_sql + ' AND '
            str_sql = str_sql + 'file_table.dir_path="{}"'.format(dir_path)
            cnt_where = cnt_where + 1

        if file_name:
            if cnt_where > 0:
                str_sql = str_sql + ' AND '
            str_sql = str_sql + 'file_table.file_name="{}"'.format(file_name)

        # SQL発行
        return self.select(str_sql)

    #------------------------------------------------------------------------------------
    # ファイル情報登録
    #------------------------------------------------------------------------------------
    def insert_file_record(self, dir_path, file_name, mtime):
        # SQL発行
        self.execute('INSERT INTO file_table(dir_path, file_name, mtime) VALUES ("{0}", "{1}", {2})'.format(dir_path, file_name, mtime))

    #------------------------------------------------------------------------------------
    # ファイル情報更新
    #------------------------------------------------------------------------------------
    def update_file_record(self, dir_path, file_name, mtime):
        # SQL発行
        self.execute('UPDATE file_table SET mtime={0}   \
        WHERE dir_path="{1}" AND file_name="{2}"'.format(mtime, dir_path, file_name))

    #------------------------------------------------------------------------------------
    # ファイルID取得
    #------------------------------------------------------------------------------------
    def get_file_record_id(self, pattern, dir_path, file_name):
        # SQL発行
        return self.select('SELECT update_counter_table.update_counter FROM update_counter_table, key_table, file_table   \
        WHERE key_table.id = update_counter_table.keyword_id AND   \
        file_table.id = update_counter_table.file_id AND    \
        file_table.dir_path="{0}" AND file_table.file_name="{1}" AND   \
        key_table.keyword="{2}"'.format(dir_path, file_name, pattern))

    #------------------------------------------------------------------------------------
    # 索引キーワード登録
    #------------------------------------------------------------------------------------
    def insert_keyward(self, keyword):
        # SQL発行
        self.execute('INSERT INTO key_table (keyword) SELECT "{0}" WHERE NOT EXISTS (SELECT 1 from key_table WHERE keyword="{0}")'.format(keyword))

    #------------------------------------------------------------------------------------
    # ファイル情報登録
    #------------------------------------------------------------------------------------
    def insert_result_record(self, key_file_id, row_no, start, end):
        # SQL発行
        self.execute('INSERT INTO result_table VALUES ({0}, {1}, {2}, {3})'.format(key_file_id, row_no, start, end))

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
    #def delete_result_record(self, keyword, dir_path, file_name):
        # SQL発行
        #self.execute('DELETE FROM result_table WHERE keyword="{0}" AND dir_path="{1}" AND file_name="{2}"'.format(keyword, dir_path, file_name))

    #------------------------------------------------------------------------------------
    # ファイル/キーワード関連テーブル
    #------------------------------------------------------------------------------------
    def insert_key_file(self, pattern, dir_path, file_path, m_time):
        # キーワード登録
        self.insert_keyward(pattern)
        # ファイル登録
        self.insert_file_record(dir_path, file_path, m_time)
        # キーワードファイル情報更新カウンタ
        self.execute('INSERT OR REPLACE INTO update_counter_table   \
        VALUES (    \
        (SELECT key_table.id FROM key_table WHERE keyword="{0}"), \
        (SELECT file_table.id FROM file_table WHERE dir_path="{1}" AND file_name="{2}"), \
        (SELECT ifnull(MAX(update_counter_table.update_counter), 0) + 1 FROM update_counter_table) \
        )'.format(pattern, dir_path, file_path))

    # ------------------------------------------------------------------------------------
    # ファイル/キーワード関連テーブル
    # ------------------------------------------------------------------------------------
    def update_key_file(self, pattern, dir_path, file_path, m_time):
        # キーワード登録
        self.insert_keyward(pattern)
        # ファイル登録
        self.insert_file_record(dir_path, file_path, m_time)
        # キーワードファイル情報更新カウンタ
        self.execute('INSERT OR REPLACE INTO update_counter_table   \
        VALUES (    \
        (SELECT key_table.id FROM key_table WHERE keyword="{0}"), \
        (SELECT file_table.id FROM file_table WHERE dir_path="{1}" AND file_name="{2}"), \
        (SELECT ifnull(MAX(update_counter_table.update_counter), 0) + 1 FROM update_counter_table) \
        )'.format(pattern, dir_path, file_path))

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

