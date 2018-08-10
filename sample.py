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

#------------------------------------------------------------------------------------
# 索引キーワード取得処理
#------------------------------------------------------------------------------------
def getKeys():
    # DBに登録されているキーワードを取得
    key_select_list = db_accessor.select_keyword()
    # 構造変換
    key_list = []
    for key in key_select_list:
        key_list.append(key[0])

    return key_list

#------------------------------------------------------------------------------------
# ディレクトリパス取得処理
#------------------------------------------------------------------------------------
def getDirs(file_name=None):
    # DBに登録されているディレクトリパスを取得
    dir_select_list = db_accessor.select_dir_path(file_name)
    # 構造変換
    dir_list = []
    for dir_path in dir_select_list:
        dir_list.append(dir_path[0])

    return dir_list

#------------------------------------------------------------------------------------
# ファイル名取得処理
#------------------------------------------------------------------------------------
def getFilenames(dir_path=None):
    # DBに登録されているファイル名を取得
    name_select_list = db_accessor.select_file_name(dir_path)
    # 構造変換
    name_list = []
    for file_name in name_select_list:
        name_list.append(file_name[0])

    return name_list

#------------------------------------------------------------------------------------
# フレーム上位層移動処理
#------------------------------------------------------------------------------------
def changeFrame(tgt_frame, main_win, front_view=None):
    # 表示フレーム切替
    if front_view:
        # 索引表示に切り替える場合
        main_win.geometry(str(tgt_frame.win_width) + 'x' + str(tgt_frame.win_height))
        main_win.resizable(1, 1)
    else:
        # 索引作成に切り替える場合
        main_win.state('normal')
        main_win.geometry('560x200')
        main_win.resizable(0, 0)

    # 指定フレームを上位層にする
    tgt_frame.tkraise()

#------------------------------------------------------------------------------------
# ディレクトリ選択ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedSelectDir(self, frame_create):
    iDir = os.path.abspath(os.path.dirname(__file__))
    selected_dir = fdialog.askdirectory(initialdir = iDir)
    if selected_dir:
        frame_create.dirvalue.set(selected_dir)

#------------------------------------------------------------------------------------
# 索引作成ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedCreate(self, frame_create):
    strdir = frame_create.dirvalue.get()
    strkey = frame_create.keyvalue.get()
    if not strdir or not strkey:
        messagebox.showerror('エラー', 'ディレクトリパス、またはキーワードが設定されていません。')
    else:
        stratTime = time.time()

        # ボタンの無効化
        frame_create.dirbtn.configure(state=tk.DISABLED)
        frame_create.createbtn.configure(state=tk.DISABLED)
        frame_create.viewbtn.configure(state=tk.DISABLED)
        frame_create.deletebtn.configure(state=tk.DISABLED)
        frame_create.deleteallbtn.configure(state=tk.DISABLED)

        # 索引キーワード登録
        db_accessor.insert_keyward(strkey)

        # 指定ディレクトリ下のファイルリスト取得
        file_list = search_file.get_file_list(strdir)

        # 検索、索引作成
        search_files(file_list, strkey)

        # DBから索引キーワードを取得して、コンボボックスへ設定
        frame_create.keycb['values'] = tuple(getKeys())

        # ボタンの有効化
        frame_create.dirbtn.configure(state=tk.NORMAL)
        frame_create.createbtn.configure(state=tk.NORMAL)
        frame_create.viewbtn.configure(state=tk.NORMAL)
        frame_create.deletebtn.configure(state=tk.NORMAL)
        frame_create.deleteallbtn.configure(state=tk.NORMAL)

        endTime = time.time()
        print('処理時間（索引作成）：{}[sec]'.format(endTime-stratTime))

        # 索引作成終了メッセージダイアログ表示
        messagebox.showinfo('メッセージ', '索引作成が終了しました。')

#------------------------------------------------------------------------------------
# 索引削除ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedDelete(self, frame_create):
    strkey = frame_create.keyvalue.get()
    # 索引キーワードが選択されていない場合
    if not strkey:
        messagebox.showerror('エラー', '削除対象キーワードが設定されていません。')
    else:
        # 索引削除
        db_accessor.delete_by_key(strkey)
        # コミット
        db_accessor.commit()

        # DBから索引キーワードを取得して、索引キーワードコンボボックスへ設定
        frame_create.keycb['values'] = tuple(getKeys())

        # 索引削除終了メッセージダイアログ表示
        messagebox.showinfo('メッセージ', '"{}"の索引削除が終了しました。'.format(strkey))

#------------------------------------------------------------------------------------
# 全削除ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedAllDelete(self, frame_create):
    # 全レコード削除
    db_accessor.delete_all_recored()
    # コミット
    db_accessor.commit()

    # 索引キーワードコンボボックスのリストを空にする
    frame_create.keycb['values'] = tuple([])

    # 全削除終了メッセージダイアログ表示
    messagebox.showinfo('メッセージ', '登録情報の全削除が終了しました。')

#------------------------------------------------------------------------------------
# 索引表示ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedView(self, frame_create, frame_view):
    # DBから索引キーワードを取得して、コンボボックスへ設定
    frame_view.keycb['values'] = tuple(getKeys())
    # DBからディレクトリパスを取得して、コンボボックスへ設定
    dir_tmp = getDirs()
    dir_tmp.insert(0, '')
    frame_view.dircb['values'] = tuple(dir_tmp)
    # DBからファイル名を取得して、コンボボックスへ設定
    name_tmp = getFilenames()
    name_tmp.insert(0, '')
    frame_view.filcb['values'] = tuple(name_tmp)

    # 索引作成画面で設定されたキーワードを索引表示画面に設定
    strkey = frame_create.keyvalue.get()
    frame_view.keyvalue.set(strkey)
    # ディレクトリ、ファイル名は空にする
    frame_view.dirvalue.set('')
    frame_view.filvalue.set('')

    # 索引表示
    viewResult(frame_view, strkey)
    # 索引表示画面を前面とする
    changeFrame(frame_view, frame_create.master.master, 1)

#------------------------------------------------------------------------------------
# 索引表の表示ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedListView(self):
    strkey = self.keyvalue.get()
    # 索引キーワードが選択されていない場合
    if not strkey:
        messagebox.showerror('エラー', '表示対象キーワードが設定されていません。')
    else:
        viewResult(self, strkey, self.dirvalue.get(), self.filvalue.get(),)

#------------------------------------------------------------------------------------
# 索引作成画面表示ボタン押下時処理
#------------------------------------------------------------------------------------
def pushedCreateWinDisp(self, frame_create):
    # 索引表示画面のサイズを保存
    self.win_width = self.master.master.winfo_width()
    self.win_height = self.master.master.winfo_height()
    # 索引作成画面を前面とする
    changeFrame(frame_create, self.master.master)

#------------------------------------------------------------------------------------
# 索引表示
#------------------------------------------------------------------------------------
def viewResult(self, key=None, dir_path=None, file_name=None):
    if key:
        stratTime = time.time()

        # DBから結果を検索
        val_list = db_accessor.select_result(key, dir_path, file_name)
        # 現在表示しているデータをテーブルから削除
        self.table.delete(*self.table.get_children())

        # 表示テーブルへの追加
        no = 1
        for val in val_list:
            self.table.insert('', 'end', values=(no, val[1], val[2], val[3], val[4], val[5]))
            no = no + 1

        endTime = time.time()
        print('処理時間（索引表示）：{}[sec]'.format(endTime-stratTime))

#------------------------------------------------------------------------------------
# ファイルリスト検索処理
#------------------------------------------------------------------------------------
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

    for matched in matched_array:
        if matched:
            # 同一キーワード、同一ファイルの検索結果を削除
            delete_result(pattern, matched[0]['dir_path'], matched[0]['file_name'])

        # 検索結果登録
        for dat in matched:
            regist_result(pattern, dat['dir_path'], dat['file_name'], dat['line_number'], dat['start'], dat['end'])

#------------------------------------------------------------------------------------
# ファイル情報登録処理
#------------------------------------------------------------------------------------
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

    # コミット
    db_accessor.commit()

#------------------------------------------------------------------------------------
# 検索結果登録処理
#------------------------------------------------------------------------------------
def regist_result(keyword, dir_path, file_name, row_no, start, end):
    # 検索結果登録
    db_accessor.insert_result_record(keyword, dir_path, file_name, row_no, start, end)
    # コミット
    db_accessor.commit()

#------------------------------------------------------------------------------------
# 検索結果削除処理
#------------------------------------------------------------------------------------
def delete_result(keyword, dir_path, file_name):
    # 検索結果削除
    db_accessor.delete_result_record(keyword, dir_path, file_name)
    # コミット
    db_accessor.commit()

#------------------------------------------------------------------------------------
# メインフレームクラス
#------------------------------------------------------------------------------------
class MainFrame(ttk.Frame):
    #------------------------------------------------------------------------------------
    # コンストラクタ
    #-----------------------------------------------------------------------------------
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        master.title(u'プロコンサンプル')

        #style = ttk.Style()
        ##print(style.theme_names())
        #style.theme_use('xpnative')

        # 初期サイズ
        master.geometry('560x200')

        # 索引作成画面を生成
        self.frame_create = CreateFrame(self)
        self.frame_create.grid(row=0, column=0, sticky=tk.NSEW)

        # 索引表示画面を生成
        self.frame_view = ViewFrame(self)
        self.frame_view.grid(row=0, column=0, sticky=tk.NSEW)

        # 画面に合わせて拡縮するように設定
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 索引作成画面を前面にする
        changeFrame(self.frame_create, self.master)

#------------------------------------------------------------------------------------
# 索引作成画面クラス
#------------------------------------------------------------------------------------
class CreateFrame(ttk.Frame):
    #------------------------------------------------------------------------------------
    # コンストラクタ
    #-----------------------------------------------------------------------------------
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)

        # 部品整形用にフレームを配置
        self.frame1 = ttk.Frame(self, height=10, borderwidth=10)
        self.frame1.grid(row=0, column=0, sticky=tk.EW)

        self.frame2 = ttk.Frame(self, borderwidth=10)
        self.frame2.grid(row=1, column=0, sticky=tk.EW)

        self.frame3 = ttk.Frame(self, borderwidth=10)
        self.frame3.grid(row=2, column=0, sticky=tk.EW)

        self.frame4 = ttk.Frame(self, height=30, borderwidth=10)
        self.frame4.grid(row=3, column=0, sticky=tk.EW)

        self.frame5 = ttk.Frame(self, borderwidth=10)
        self.frame5.grid(row=4, column=0, sticky=tk.EW)

        self.dirlabel = ttk.Label(self.frame2, text=u'ディレクトリ : ', relief=tk.FLAT)
        self.dirlabel.pack(anchor=tk.W, side=tk.LEFT)

        self.dirvalue = tk.StringVar()
        self.dirtext = ttk.Entry(self.frame2, style="", width=30, textvariable=self.dirvalue)
        self.dirtext.pack(anchor=tk.W, side=tk.LEFT)

        self.dirbtn = ttk.Button(self.frame2, text=u'選択', command= lambda : pushedSelectDir(self.dirbtn, self))
        self.dirbtn.pack(anchor=tk.W, side=tk.LEFT, padx=5)

        # 索引キーワードコンボボックス
        self.cblabel = ttk.Label(self.frame3, text=u'　キーワード : ', relief=tk.FLAT)
        self.cblabel.pack(anchor=tk.W, side=tk.LEFT)
        self.keyvalue = tk.StringVar()
        self.keycb = ttk.Combobox(self.frame3, textvariable=self.keyvalue)
        # DBから索引キーワードを取得して、コンボボックスへ設定
        self.keycb['values'] = tuple(getKeys())
        self.keycb.pack(anchor=tk.W, side=tk.LEFT)

        # 索引作成ボタン
        self.createbtn = ttk.Button(self.frame5, text=u'作成', command= lambda : pushedCreate(self.createbtn, self))
        self.createbtn.grid(row=0, column=0, sticky=tk.EW, padx=20, pady=5)

        # 索引表示ボタン
        self.viewbtn = ttk.Button(self.frame5, text=u'表示', command= lambda : pushedView(self.viewbtn, self, master.frame_view))
        self.viewbtn.grid(row=0, column=1, sticky=tk.EW, padx=20)

        # 索引削除ボタン
        self.deletebtn = ttk.Button(self.frame5, text=u'削除', command= lambda : pushedDelete(self.deletebtn, self))
        self.deletebtn.grid(row=0, column=2, sticky=tk.EW, padx=20)

        # 索引全削除ボタン
        self.deleteallbtn = ttk.Button(self.frame5, text=u'全削除', command= lambda : pushedAllDelete(self.deleteallbtn, self))
        self.deleteallbtn.grid(row=0, column=3, sticky=tk.EW, padx=20)

#------------------------------------------------------------------------------------
# 索引表示画面クラス
#------------------------------------------------------------------------------------
class ViewFrame(ttk.Frame):
    #------------------------------------------------------------------------------------
    # コンストラクタ
    #-----------------------------------------------------------------------------------
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)

        # デフォルトサイズ
        self.win_width = 800
        self.win_height = 420

        # 部品整形用にフレームを配置
        self.frame1 = ttk.Frame(self, height=10, borderwidth=10)
        self.frame1.grid(row=0, column=0, sticky=tk.EW)

        self.frame2 = ttk.Frame(self, borderwidth=10)
        self.frame2.grid(row=1, column=0, sticky=tk.EW)

        self.frame3 = ttk.Frame(self, height=10, borderwidth=10)
        self.frame3.grid(row=2, column=0, sticky=tk.EW)

        self.frame4 = ttk.Frame(self, height=30, borderwidth=10)
        self.frame4.grid(row=3, column=0, sticky=tk.NSEW)

        self.frame5 = ttk.Frame(self, borderwidth=10)
        self.frame5.grid(row=4, column=0, sticky=tk.EW)

        # 画面に合わせて拡縮するように設定（縦方向は表だけ）
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 索引キーワードコンボボックス
        self.keylabel = ttk.Label(self.frame2, text=u'　キーワード : ', relief=tk.FLAT)
        self.keylabel.grid(row=0, column=0, sticky=tk.E)
        self.keyvalue = tk.StringVar()
        self.keycb = ttk.Combobox(self.frame2, state='readonly', textvariable=self.keyvalue)
        #self.keycb.pack(anchor=tk.NW, side=tk.LEFT)
        self.keycb.grid(row=0, column=1, sticky=tk.W)

        # ディレクトリコンボボックス
        self.dirlabel = ttk.Label(self.frame2, text=u'　ディレクトリ : ', relief=tk.FLAT)
        self.dirlabel.grid(row=1, column=0, sticky=tk.E)
        self.dirvalue = tk.StringVar()
        self.dircb = ttk.Combobox(self.frame2, width=80, state='readonly', textvariable=self.dirvalue)
        self.dircb.grid(row=1, column=1, sticky=tk.NSEW)
        self.dircb.bind('<<ComboboxSelected>>', self.dirSelected)

        # ファイル名コンボボックス
        self.fillabel = ttk.Label(self.frame2, text=u'　ファイル名 : ', relief=tk.FLAT)
        self.fillabel.grid(row=2, column=0, sticky=tk.E)
        self.filvalue = tk.StringVar()
        self.filcb = ttk.Combobox(self.frame2, width=30, state='readonly', textvariable=self.filvalue)
        self.filcb.grid(row=2, column=1, sticky=tk.W)
        self.filcb.bind('<<ComboboxSelected>>', self.fileSelected)

        # 索引表示ボタン
        self.viewbtn = ttk.Button(self.frame2, text=u'表示', command= lambda : pushedListView(self))
        #self.viewbtn.pack(anchor=tk.NW, side=tk.LEFT)
        self.viewbtn.grid(row=2, column=2, sticky=tk.E)

        # ディレクトリパスのコンボボックスはウィンドウサイズに合わせて拡げる
        self.frame2.grid_columnconfigure(1, weight=1)
        self.frame2.grid_rowconfigure(1, weight=1)


        # 索引テーブル
        self.table = ttk.Treeview(self.frame4, selectmode=tk.BROWSE)
        #self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.table.grid(row=0, column=0, stick=tk.NSEW)
        # スライドバー
        self.vsb = ttk.Scrollbar(self.frame4, orient=tk.VERTICAL, command=self.table.yview)
        self.table['yscrollcommand'] = self.vsb.set
        #self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.vsb.grid(row=0, column=1, stick=tk.NS)

        self.frame4.grid_rowconfigure(0, weight=1)
        self.frame4.grid_columnconfigure(0, weight=1)

        # ヘッダを設定
        self.table['columns'] = ('no', 'dir_path', 'file_name', 'row_no', 'start', 'end')
        self.table['show'] = 'headings'
        self.table.column('no', width=50, anchor=tk.E, stretch=False)
        self.table.column('dir_path', width=400, anchor=tk.W)
        self.table.column('file_name', width=120, anchor=tk.W)
        self.table.column('row_no', width=50, anchor=tk.E, stretch=False)
        self.table.column('start', width=50, anchor=tk.E, stretch=False)
        self.table.column('end', width=50, anchor=tk.E, stretch=False)
        self.table.heading('no', text='No.')
        self.table.heading('dir_path', text='ディレクトリ')
        self.table.heading('file_name', text='ファイル名')
        self.table.heading('row_no', text='行')
        self.table.heading('start', text='開始')
        self.table.heading('end', text='終了')

        self.table.bind('<Double-1>', self.doubleClicked)

        # 索引作成画面表示ボタン
        self.createbtn = ttk.Button(self.frame5, text=u'作成画面', command= lambda : pushedCreateWinDisp(self, master.frame_create))
        self.createbtn.pack(anchor=tk.W, side=tk.LEFT)

    #------------------------------------------------------------------------------------
    # ディレクトリパス選択イベント処理
    #------------------------------------------------------------------------------------
    def dirSelected(self, event):
        # DBからファイル名を取得して、コンボボックスへ再設定
        name_tmp = getFilenames(self.dirvalue.get())
        name_tmp.insert(0, '')
        self.filcb['values'] = tuple(name_tmp)

    #------------------------------------------------------------------------------------
    # ファイル名選択イベント処理
    #------------------------------------------------------------------------------------
    def fileSelected(self, event):
        # DBからファイル名を取得して、コンボボックスへ再設定
        name_tmp = getDirs(self.filvalue.get())
        name_tmp.insert(0, '')
        self.dircb['values'] = tuple(name_tmp)

    #------------------------------------------------------------------------------------
    # 索引テーブルのダブルクリックイベント処理
    #------------------------------------------------------------------------------------
    def doubleClicked(self, event):
        items = self.table.selection()
        if items:
            # 選択行の情報取得
            item = self.table.selection()[0]
            item_text = self.table.item(item,"values")

            # 新規ウィンドウ生成
            view_file_win = Toplevel()
            view_file_win.title('{0[1]}\{0[2]}'.format(item_text))
            text_frame = ttk.Frame(view_file_win)
            # テキスト領域生成
            txt = tkst.ScrolledText(text_frame)

            # ファイル読み込み、テキスト設定
            with open('{0[1]}\{0[2]}'.format(item_text),'r',encoding="utf-8") as f:
                txt.insert(tk.END, f.read())

            # マッチした箇所を強調表示
            txt.tag_config("MATCHED", background="red", foreground="white")
            txt.tag_add("MATCHED", '{0}.{1}'.format(item_text[3], int(item_text[4])-1), '{0}.{1}'.format(item_text[3], item_text[5]))

            # マッチした行に表示位置を移動
            txt.see('{0}.{1}'.format(item_text[3], int(item_text[4])-1))

            # ウィンドウ表示
            txt.pack(fill=tk.BOTH, expand=1)
            text_frame.pack(fill=tk.BOTH, expand=1)


#====================================================================================
# メイン処理
#====================================================================================
if __name__ == "__main__":

    # DBアクセサ作成
    db_accessor = db_access.DBAccess()
    # DB接続
    db_accessor.connect()
    # DBがない場合、作成する
    db_accessor.create()
    # コミット
    db_accessor.commit()

    # ウィンドウを作成
    root = tk.Tk()
    # メインのフレームを作成
    main_frame = MainFrame(root)
    # メインのフレームを表示
    main_frame.pack(expand=1, fill=tk.BOTH)
    # メインループ
    root.mainloop()

    # DB切断
    db_accessor.close()
