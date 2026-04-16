
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 18:57:42 2021

@author: SGMT
"""

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np  # 日付ずれの相関を求めるために使います。
import pandas as pd  # 株価データをまとめて処理するために使います。
import datetime  # 株価データを日付ごとに扱いやすくするために使います。（なくてもよい）
from tqdm import tqdm  # 処理時間の資産の目安に使います。
import os  # ディレクトリの調整に使います。
import urllib.request  # urlからzipファイルをダウンロードするのに使います。
import zipfile  # zipファイルの解凍に使います。
import shutil  # ファイルの移動に使います。
import glob  # 個々の株価データを一つのcsvファイルにまとめるのに使います。
from tkcalendar import *

class application(tk.Frame):
    def __init__(self,master):
        super().__init__(master)        #superclass(tk.Frame)の初期化メソッドを参照
        self.pack()
        self.master.geometry("800x600")
        self.master.title("風が吹けば桶屋が儲かる君")
        self.create_widgets()
        self.parentFolder = 'content'
        self.new_dir_path = 'content/japan'
        self.us_dir_path='content/us'
        self.zip_dir_path = 'content/kabu.zip'
        self.xls_dir_path = 'content/data_j.xls'
        self.result_dir_path = 'result'
        try:
            os.makedirs(self.parentFolder+'/'+self.result_dir_path)
        except:
            pass

    def create_widgets(self):
        self.downloadframe=ttk.Frame(self)
        self.mainFrame = ttk.Frame(self)
        self.allFrame = ttk.Frame(self)
        self.eachFrame = ttk.Frame(self)
        ttk.Button(self.downloadframe,text='株価データをダウンロード',command=self.download).pack(pady=100,fill=tk.X)
        ttk.Button(self.downloadframe,text='ダウンロードせずに始める',command=self.nondownload).pack(pady=100,fill=tk.X)

        ttk.Button(self.mainFrame,text='全銘柄で解析',command=lambda:self.changeall(self.allFrame,self.gyousyuFrame,self.idoFrame,self.soukanFrame,self.sortcheckFrame)).pack(pady=100)
        ttk.Button(self.mainFrame,text='個別銘柄で解析',command=lambda:self.changecode(self.eachFrame)).pack(pady=100)
        ttk.Button(self.mainFrame,text='米国株解析',command=lambda:self.changecode(self.eachFrame)).pack(pady=100)

        self.dateFrame=ttk.LabelFrame(self.allFrame,text="解析期間指定")
        label_start = ttk.Label(self.dateFrame, text='開始日')
        label_start.grid(row=0, column=0, sticky='w',padx=30)
        self.daybefore=datetime.date.today()-datetime.timedelta(60)
        self.cal1=Calendar(self.dateFrame,selectmode='day',year=self.daybefore.year,month=self.daybefore.month,day=self.daybefore.day)
        self.cal2=Calendar(self.dateFrame,selectmode='day',year=datetime.date.today().year,month=datetime.date.today().month,day=datetime.date.today().day)
        self.cal1.grid(row=1,column=0,padx=30,pady=10,sticky='e')
        self.cal2.grid(row=1,column=1,padx=30,pady=10,sticky='e')
        label_end = ttk.Label(self.dateFrame, text='終了日')
        label_end.grid(row=0, column=1, sticky='w',padx=30)
        self.gyousyuFrame=ttk.LabelFrame(self.allFrame,text='業種を指定')
        #ttk.Button(self.eachFrame,text='解析開始',command=self.meigara_all).grid(row=0, column=1, sticky='s',padx=30,pady=10)
       # self.codeFrame=ttk.LabelFrame(self.eachFrame,text='codeを指定')
        self.idoFrame=ttk.LabelFrame(self.allFrame,text='移動平均を指定')
        self.soukanFrame=ttk.LabelFrame(self.allFrame,text='相互相関係数の下限を設定')
        self.sortcheckFrame=ttk.LabelFrame(self.allFrame,text='同じ業種で絞り込み')
        self.downloadframe.grid(row=0,column=0,stick='nsew')
        ttk.Button(self.allFrame,text='解析開始',command=self.numcheck).grid(row=3,column=2,sticky='s',pady=10,padx=10)
        self.allFrame.grid(row=0,column=0,sticky='nsew')
        self.dateFrame.grid(row=0,column=0,columnspan=3)
        self.gyousyuFrame.grid(row=1,column=0,columnspan=3)
        self.idoFrame.grid(row=2,column=0,padx=10)
       # self.codeFrame.grid(row=0,column=0,padx=10)
        self.soukanFrame.grid(row=2,column=1,padx=10)
        self.sortcheckFrame.grid(row=2,column=2,padx=10)
        self.mainFrame.grid(row=0,column=0,sticky='nsew')
        self.eachFrame.grid(row=0,column=0,sticky='nsew')
        self.downloadframe.tkraise()

    def numcheck(self):
        #try:
            isinstance(int(self.rollingentry.get()),int)
            if int(self.rollingentry.get())<1:
                tk.messagebox.showwarning('エラー', '移動平均は1以上の整数を指定してください')
            elif int(self.rollingentry.get())>round(len(self.df_jp[self.cal1.get_date():self.cal2.get_date()].index)/3):
                tk.messagebox.showwarning('エラー','移動平均は1以上{0}以下の数字を入力してください'.format(round(len(self.df_jp[self.cal1.get_date():self.cal2.get_date()])/3)))
            else:
                #try:
                    isinstance(float(self.soukanentry.get()),float)
                    if float(self.soukanentry.get())>1.0 or float(self.soukanentry.get())<0:
                        tk.messagebox.showwarning('エラー', '係数は0以上1以下の値を指定してください')
                    else:
                        self.meigara_all(self.df_jp,self.syousai)
                        
    def numcheck2(self):
        #try:
            isinstance(int(self.rollingentry.get()),int)
            if int(self.rollingentry.get())<1:
                tk.messagebox.showwarning('エラー', '移動平均は1以上の整数を指定してください')
            elif int(self.rollingentry.get())>round(len(self.df_jp[self.cal1.get_date():self.cal2.get_date()].index)/3):
                tk.messagebox.showwarning('エラー','移動平均は1以上{0}以下の数字を入力してください'.format(round(len(self.df_jp[self.cal1.get_date():self.cal2.get_date()])/3)))
            else:
                #try:
                    isinstance(float(self.soukanentry.get()),float)
                    if float(self.soukanentry.get())>1.0 or float(self.soukanentry.get())<0:
                        tk.messagebox.showwarning('エラー', '係数は0以上1以下の値を指定してください')
                    else:
                        self.meigara_kobetu(self.df_jp,self.syousai)
                #except:
                #    tk.messagebox.showwarning('エラー', '係数は0以上1以下のを指定してください')
        #except:
          #  tk.messagebox.showwarning('エラー', '移動平均は1以上の整数を指定してください')

    def changeall(self,frame,frame2,frame3,frame4,frame5):
        self.gyousyucheck(frame2)
        self.rolling(frame3)
        self.soukanunder(frame4)
        self.sortcheckbox(frame5)
        frame.tkraise()

    def changecode(self,frame):
        self.dateFrame=ttk.LabelFrame(self.eachFrame,text="解析期間指定")
        label_start = ttk.Label(self.dateFrame, text='開始日')
        label_start.grid(row=0, column=0, sticky='w',padx=30)
        self.daybefore=datetime.date.today()-datetime.timedelta(60)
        self.cal1=Calendar(self.dateFrame,selectmode='day',year=self.daybefore.year,month=self.daybefore.month,day=self.daybefore.day)
        self.cal2=Calendar(self.dateFrame,selectmode='day',year=datetime.date.today().year,month=datetime.date.today().month,day=datetime.date.today().day)
        self.cal1.grid(row=1,column=0,padx=30,pady=10,sticky='e')
        self.cal2.grid(row=1,column=1,padx=30,pady=10,sticky='e')
        label_end = ttk.Label(self.dateFrame, text='終了日')
        label_end.grid(row=0, column=1, sticky='w',padx=30)
        self.gyousyuFrame=ttk.LabelFrame(self.eachFrame,text='業種を指定')
        #ttk.Button(self.eachFrame,text='解析開始',command=self.meigara_all).grid(row=0, column=1, sticky='s',padx=30,pady=10)
        self.codeFrame=ttk.LabelFrame(self.eachFrame,text='codeを指定')
        self.idoFrame=ttk.LabelFrame(self.eachFrame,text='移動平均を指定')
        self.soukanFrame=ttk.LabelFrame(self.eachFrame,text='相互相関係数の下限を設定')
        self.sortcheckFrame=ttk.LabelFrame(self.eachFrame,text='同じ業種で絞り込み')
        self.downloadframe.grid(row=0,column=0,stick='nsew')
        ttk.Button(self.eachFrame,text='解析開始',command=self.numcheck2).grid(row=3,column=2,sticky='s',pady=10,padx=10)
        self.eachFrame.grid(row=0,column=0,sticky='nsew')
        self.dateFrame.grid(row=0,column=0,columnspan=3)
        self.gyousyuFrame.grid(row=1,column=0,columnspan=3)
        self.idoFrame.grid(row=2,column=0,padx=10)
        self.codeFrame.grid(row=3,column=1,padx=10)
        self.soukanFrame.grid(row=2,column=1,padx=10)
        self.sortcheckFrame.grid(row=2,column=2,padx=10)
        self.mainFrame.grid(row=0,column=0,sticky='nsew')
        self.eachFrame.grid(row=0,column=0,sticky='nsew')
        self.codeinput(self.codeFrame)
        self.changeall(self.eachFrame,self.gyousyuFrame,self.idoFrame,self.soukanFrame,self.sortcheckFrame)
        frame.tkraise()

    def callback(self):

        pass
    def sortcheckbox(self,frame):
        self.sortopt=tk.BooleanVar()
        self.sortopt.set(False)
        self.sortchk=tk.Checkbutton(frame,text='同じ業種で絞り込む',variable=self.sortopt)
        self.sortchk.pack()

    def soukanunder(self,frame):
        ttk.Label(frame,text='値以上の結果を表示').grid(row=0,column=0)
        self.soukanentry = ttk.Entry(frame,justify='center',textvariable=tk.DoubleVar())
        self.soukanentry.insert(0,0.65)
        self.soukanentry.grid(row=0,column=1)

    def rolling(self,frame):
        ttk.Label(frame,text='平均をとる日数を入力').grid(row=0,column=0)
        self.rollingentry = ttk.Entry(frame,justify='center',textvariable=tk.IntVar())
        self.rollingentry.insert(0,3)
        self.rollingentry.grid(row=0,column=1)
        
    def codeinput(self,frame):
        ttk.Label(frame,text='銘柄コードを入力').grid(row=0,column=0)
        self.meigaracode = ttk.Entry(frame,justify='center',textvariable=tk.StringVar())
        self.meigaracode.insert(0,'7780')
        self.meigaracode.grid(row=0,column=1)

    def gyousyucheck(self,frame):
        gyousyu_list=[['水産・農林業','建設業','非鉄金属','鉱業','サービス業','化学','情報・通信業','食料品','ガラス・土石製品'],['不動産業','その他金融業','小売業','卸売業','その他製品','繊維製品','電気機器','医薬品'],['証券、商品先物取引業','輸送用機器','石油・石炭製品','金属製品','パルプ・紙','ゴム製品','鉄鋼','機械'],['精密機器','銀行業','保険業','陸運業','倉庫・運輸関連業','海運業','空運業','電気・ガス業']]
        self.gyousyu_list=['水産・農林業','建設業','非鉄金属','鉱業','サービス業','化学','情報・通信業','食料品','不動産業','その他金融業','小売業','卸売業','その他製品','繊維製品','電気機器','医薬品','証券、商品先物取引業','輸送用機器','石油・石炭製品','金属製品','パルプ・紙','ゴム製品','鉄鋼','機械','精密機器','銀行業','保険業','陸運業','倉庫・運輸関連業','海運業','空運業','電気・ガス業','ガラス・土石製品']
        self.chk=[]
        self.opt=[]
        self.count=0
        for i in range(4):
            for j in range(8):
                self.opt.append(tk.BooleanVar())
                self.opt[self.count].set(True)
                self.chk.append(tk.Checkbutton(frame,text=gyousyu_list[i][j],variable=self.opt[self.count]))
                self.chk[self.count].grid(column=j,row=i,sticky='w')
                self.count=self.count+1
        self.opt.append(tk.BooleanVar())
        self.opt[self.count].set(True)
        self.chk.append(tk.Checkbutton(frame,text=gyousyu_list[0][8],variable=self.opt[self.count]))
        self.chk[self.count].grid(column=0,row=4,sticky='w')
        ttk.Button(frame,text='選択解除',command=self.resetbottun).grid(row=4,column=7)
        ttk.Button(frame,text='全選択',command=self.allselectbottun).grid(row=4,column=6)

    def resetbottun(self):
        for i in range(33):
            self.opt[i].set(False)


    def allselectbottun(self):
        for i in range(33):
            self.opt[i].set(True)

    def nondownload(self):
        if os.path.exists('content/df_jp.csv'):
            self.df_jp = pd.read_csv('content/df_jp.csv', index_col=0, parse_dates=True)
        else:
            self.combine_files()
        if os.path.exists('content/df_us.csv'):
            self.df_us = pd.read_csv('content/df_us.csv', index_col=0, parse_dates=True)
        else:
            self.combine_files_us()
        self.syousai = pd.read_csv('content/syousai.csv', index_col=0, parse_dates=True)
        self.mainFrame.tkraise()
    def download(self):
        now = datetime.datetime.now()
        print('処理開始 時刻：' + str(now))

        # ファイルの保管場所を用意します。ここら辺は環境依存ですので媒体に合わせて自由にやってください。今回はcolaboratoryの形式に合わせます。
        url = 'https://static.stooq.com/db/h/d_jp_txt.zip'  # 株価データのurl

        def download_file(url, dst_path):
            with urllib.request.urlopen(url) as web_file:
                data = web_file.read()
                with open(dst_path, mode='wb') as local_file:
                    local_file.write(data)


        # フォルダがあれば削除
        if os.path.exists(self.parentFolder):
            shutil.rmtree(self.parentFolder)
        # ファイルの取り込み
        os.makedirs(self.new_dir_path)
        kabu_url='https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls'
        download_file(kabu_url, self.xls_dir_path)
        filename='content/data_j.xls'
        gyousyu=pd.read_excel(filename)
        now = datetime.datetime.now()
        print('ファイルのダウンロード開始 時刻：' + str(now))
        download_file(url, self.zip_dir_path)
        now = datetime.datetime.now()
        print('ファイルのダウンロード完了 時刻：' + str(now))

        # ファイルの結合
        # ダウンロードしたデータは個々の銘柄ごとにtxt ファイルになっているのでこれらを結合して一つのcsvファイルにします。
        with sfile.ZipFile(self.zip_dir_path) as existing_zip:  # zipファイルをオープンします。
            existing_zip.extractall(self.new_dir_path)

        for p in os.listdir(self.new_dir_path + '/data/daily/jp/tse stocks/2/'):  # ファイルを一つの場所にまとめます。
            shutil.move(os.path.join(self.new_dir_path + '/data/daily/jp/tse stocks/2',
                        p), self.new_dir_path + '/data/daily/jp/tse stocks/1/')

        self.makefiles()
    def combine_files(self):
        # 必要なディレクトリの存在を確認して結合処理
        source_dir = os.path.join(self.new_dir_path, 'data/daily/jp/tse stocks/2/')
        dest_dir = os.path.join(self.new_dir_path, 'data/daily/jp/tse stocks/1/')
    
        if os.path.exists(source_dir):
            for p in os.listdir(source_dir):
                shutil.move(os.path.join(source_dir, p), dest_dir)
    
        self.makefiles()
    def combine_files_us(self):
            # NASDAQ stocks への統合
            nasdaq_dir = os.path.join(self.us_dir_path, 'data/daily/us/nasdaq stocks/1/')
            os.makedirs(nasdaq_dir, exist_ok=True)
    
            stock_dirs = [
                os.path.join(self.us_dir_path, 'data/daily/us/nasdaq stocks/2/'),
                os.path.join(self.us_dir_path, 'data/daily/us/nyse stocks/1/'),
                os.path.join(self.us_dir_path, 'data/daily/us/nyse stocks/2/'),
                os.path.join(self.us_dir_path, 'data/daily/us/nyse stocks/3/')
            ]
    
            # 各フォルダのファイルを nasdaq stocks/1/ に移動
            for stock_dir in stock_dirs:
                if os.path.exists(stock_dir):
                    for p in os.listdir(stock_dir):
                        shutil.move(os.path.join(stock_dir, p), nasdaq_dir)
    
            # 統合したファイルをDataFrameに変換
            path = nasdaq_dir
            all_files = glob.glob(path + '*.txt')
    
            b = pd.read_csv(path + 'aacg.us.txt').set_index('<DATE>')[['<CLOSE>']].rename(columns={'<CLOSE>': 'start'})
            li = []
    
            for filename in tqdm(all_files):
                try:
                    a = pd.read_csv(filename)
                    li.append(a.set_index('<DATE>')[['<CLOSE>']].rename(columns={'<CLOSE>': a['<TICKER>'][0]}))
                except:
                    pass
            
            df_us = b.join(li, how='outer')
            df_us = df_us.drop('start', axis=1)  # 不要な列の削除
            df_us=df_us.sort_index(axis=1)
            df_us.index=pd.to_datetime(df_us.index,format='%Y%m%d')
            self.df_us=df_us
            self.mainFrame.tkraise()
            self.df_us.to_csv(self.parentFolder+'/df_us.csv')



    def makefiles(self):
        filename='content/data_j.xls'
        gyousyu=pd.read_excel(filename)
        path = self.new_dir_path + '/data/daily/jp/tse stocks/1/'  # pathの指定
        all_files = glob.glob(path+'*.txt')  # txtファイルの出力
        b = pd.read_csv(path+'1301.jp.txt').set_index('<DATE>')[['<CLOSE>']].rename(columns={'<CLOSE>': 'start'})  # ファイルのひな型を作ります。銘柄コードはなんでもいいです。
        li = []  # 空のリスト
        print('ファイルを結合しています')
        for filename in tqdm(all_files):  # すべてのファイルに対し結合処理を行います。
            try:
                a = pd.read_csv(filename)
                li.append(a.set_index('<DATE>')[['<CLOSE>']].rename(
                    columns={'<CLOSE>': a['<TICKER>'][0]}))  # 終値を取り出しています。OPENなど複数選択も可です。
            except:  # 例外処理
                pass
        print('完了')
        df_jp = b.join(li, how='outer')  # すべてのファイルの結合
        df_jp = df_jp.drop('start', axis=1)  # 不要な列の削除
        df_jp=df_jp.sort_index(axis=1)
        df_jp.index=pd.to_datetime(df_jp.index,format='%Y%m%d')
        gyousyu = gyousyu.astype({'コード': str})
        gyousyu['コード']=gyousyu['コード']+'.JP'
        syousai=pd.DataFrame(np.array([gyousyu['銘柄名'].values,gyousyu['33業種区分'].values]),index=['銘柄名','業種'],columns=gyousyu['コード'].values)
        kata=pd.DataFrame([['']*len(df_jp.columns.values),['']*len(df_jp.columns.values)],index=['銘柄名','業種'],columns=df_jp.columns.values)
        syousai=pd.concat([kata,syousai],join='outer')[list(kata.columns.values)]
        syousai=syousai[2:4]
        self.syousai=syousai
        self.df_jp=df_jp
        self.mainFrame.tkraise()
        self.df_jp.to_csv(self.parentFolder+'/df_jp.csv')
        self.syousai.to_csv(self.parentFolder+'/syousai.csv')

    def meigara_all(self,df_jp,syousai):
        siborikomi=[]
        for i in range(33):
            if self.opt[i].get():
              siborikomi.append(self.gyousyu_list[i])
            else:
              pass
        gy=self.syousai.T

        sortgy=list(gy[gy['業種'].isin(siborikomi)].index.values)

        df_jp=df_jp[sortgy]
        df_jp=df_jp[self.cal1.get_date():self.cal2.get_date()]
        for columns in df_jp.columns: #欠損値が10個以上含まれている場合は測定不能としデータを除外します。
            if df_jp[columns].isna().sum()>10:
                df_jp=df_jp.drop(columns,axis=1)

        df_jp=df_jp.dropna(axis=0,how='all') #すべての株が欠損値である日付を除外しておきます。
        df_jp=df_jp.fillna(df_jp.median()) #欠損値を中央値で置き換えます。
        for columns in df_jp.columns: #安値株は変動が激しく邪魔なので除外します。
            if df_jp[columns].mean()<300: #ここでは平均300円以下の株を除外します。
                df_jp=df_jp.drop(columns,axis=1)
        df_jp=df_jp.rolling(int(self.rollingentry.get())).mean()
        df_jp=df_jp.dropna(axis=0,how='all') #すべての株が欠損値である日付を除外しておきます。

        rets_jp=np.log(df_jp/df_jp.shift(1)) #対数収益率を定義
        rets_jp=rets_jp.dropna(axis=0,how='all') #すべてが欠損値の行を削除
        rets_norm=(rets_jp-rets_jp.mean())/rets_jp.std()  #対数収益率を正規化します
        #相互相関関数の計算と遅延の測定
        sort_past=pd.DataFrame(columns=['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1','銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2','相関','遅れ','チャート'],index=[])
        print('解析開始')
        for columns_jp in tqdm(rets_jp.columns): #すべての株に対して繰り返し処理
            keisuu=[] #相互相関係数を入れるリストです。
            max=[] #畳み込み積分が最大となる遅延を入れます。
            meigara_code1=[]
            name_code1=[]
            gyousyu_code1=[]
            chart_url=[]
            kabunusi_code1=[]
            kabunusi_code2='https://kabutan.jp/stock/holder?code={:s}'.format(columns_jp.replace('.JP',''))
            for columns_jp2 in rets_jp.columns: #すべての株に対し繰り返し
                    y=rets_norm[columns_jp2].values #株価データを抽出します
                    corr=np.correlate(rets_norm[columns_jp].values,y,mode='full') #銘柄ごとに相互相関関数の計算をさせます。
                    keisuu.append(corr.max()/len(rets_norm.index.values)) #keisuuに相互相関係数を順番に入れていきます。
                    delay=corr.argmax()-len(rets_norm.index.values)+1 #mode='full'の場合は相互相関係数が最大となる遅延は左の式で計算できます。
                    max.append(delay) #maxに遅延を代入しておきます。
                    meigara_code1.append(columns_jp2)
                    name_code1.append(syousai.at['銘柄名',columns_jp2])
                    gyousyu_code1.append(syousai.at['業種',columns_jp2])
                    chart_url.append('https://finance.yahoo.co.jp/quote/{:s}.T/chart?frm=dly&trm=6m&compare={:s}.T'.format(columns_jp2.replace('.JP',''),columns_jp.replace('.JP','')))
                    kabunusi_code1.append('https://kabutan.jp/stock/holder?code={:s}'.format(columns_jp2.replace('.JP','')))
            kekka=pd.DataFrame(np.array([meigara_code1,name_code1,gyousyu_code1,kabunusi_code1,[str(columns_jp)]*len(max),[str(syousai.at['銘柄名',columns_jp])]*len(max),[str(syousai.at['業種',columns_jp])]*len(max),[kabunusi_code2]*len(max),keisuu,max,chart_url],dtype=object).T, columns=['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1','銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2','相関','遅れ','チャート']) #結果をまとめたデータを作成します。
            sort=pd.concat((sort_past,kekka.query('相関> {}'.format(float(self.soukanentry.get())))),sort=False) #わかりやすいように相関係数が高い順に並び変えておきます。0.7以下はほぼ相関がないので、この時点で消します。
            sort_past=sort
        sort=sort.sort_values(by='相関',ascending=False) #相関係数で並び替えます。
        print('解析終了')
        sort_t=sort[sort['銘柄コード_code1']!=sort['銘柄コード_code2']] #同じ銘柄同士による結果を排除しておきます
        result=sort_t[::2] #このままでは2024と2025の組み合わせが二通り出てしまうので偶数行だけ抽出します
        if self.sortopt.get():
            result=result[result['業種_code1']==result['業種_code2']]
        result=result.reset_index(drop=True)
        for i in result.index.values:
            if result.at[i,'遅れ']<0:
                tmp=result.loc[i,['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1']].values
                result.loc[i,['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1']]=result.loc[i,['銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2']].values
                result.loc[i,['銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2']]=tmp
                result.at[i,'遅れ']=-result.at[i,'遅れ']
        result.to_csv(self.parentFolder + '/' + self.result_dir_path + '/result_{:s}.csv'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')),encoding='cp932')  # 結果の保存
        print('結果を保存しました')
        
        
    def meigara_kobetu(self,df_jp,syousai):
        siborikomi=[]
        for i in range(33):
            if self.opt[i].get():
              siborikomi.append(self.gyousyu_list[i])
            else:
              pass
        gy=self.syousai.T

        sortgy=list(gy[gy['業種'].isin(siborikomi)].index.values)

        df_jp=df_jp[sortgy]
        df_jp=df_jp[self.cal1.get_date():self.cal2.get_date()]
        for columns in df_jp.columns: #欠損値が10個以上含まれている場合は測定不能としデータを除外します。
            if df_jp[columns].isna().sum()>10:
                df_jp=df_jp.drop(columns,axis=1)

        df_jp=df_jp.dropna(axis=0,how='all') #すべての株が欠損値である日付を除外しておきます。
        df_jp=df_jp.fillna(df_jp.median()) #欠損値を中央値で置き換えます。
        for columns in df_jp.columns: #安値株は変動が激しく邪魔なので除外します。
            if df_jp[columns].mean()<300: #ここでは平均300円以下の株を除外します。
                df_jp=df_jp.drop(columns,axis=1)
        df_jp=df_jp.rolling(int(self.rollingentry.get())).mean()
        df_jp=df_jp.dropna(axis=0,how='all') #すべての株が欠損値である日付を除外しておきます。

        rets_jp=np.log(df_jp/df_jp.shift(1)) #対数収益率を定義
        print(self.sortopt)
      ##  print(self.meigaracode.get()+'.JP')
        #print(pd.Index([self.meigaracode.get()+'.JP']))
        rets_jp=rets_jp.dropna(axis=0,how='all') #すべてが欠損値の行を削除
        rets_norm=(rets_jp-rets_jp.mean())/rets_jp.std()  #対数収益率を正規化します
        #相互相関関数の計算と遅延の測定
        sort_past=pd.DataFrame(columns=['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1','銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2','相関','遅れ','チャート'],index=[])
        print('解析開始')
        for columns_jp in pd.Index([self.meigaracode.get()+'.JP']): #すべての株に対して繰り返し処理
            keisuu=[] #相互相関係数を入れるリストです。
            max=[] #畳み込み積分が最大となる遅延を入れます。
            meigara_code1=[]
            name_code1=[]
            gyousyu_code1=[]
            chart_url=[]
            kabunusi_code1=[]
            kabunusi_code2='https://kabutan.jp/stock/holder?code={:s}'.format(columns_jp.replace('.JP',''))
            for columns_jp2 in tqdm(rets_jp.columns): #すべての株に対し繰り返し
                    y=rets_norm[columns_jp2].values #株価データを抽出します
                    corr=np.correlate(rets_norm[columns_jp].values,y,mode='full') #銘柄ごとに相互相関関数の計算をさせます。
                    keisuu.append(corr.max()/len(rets_norm.index.values)) #keisuuに相互相関係数を順番に入れていきます。
                    delay=corr.argmax()-len(rets_norm.index.values)+1 #mode='full'の場合は相互相関係数が最大となる遅延は左の式で計算できます。
                    max.append(delay) #maxに遅延を代入しておきます。
                    meigara_code1.append(columns_jp2)
                    name_code1.append(syousai.at['銘柄名',columns_jp2])
                    gyousyu_code1.append(syousai.at['業種',columns_jp2])
                    chart_url.append('https://finance.yahoo.co.jp/quote/{:s}.T/chart?frm=dly&trm=6m&compare={:s}.T'.format(columns_jp2.replace('.JP',''),columns_jp.replace('.JP','')))
                    kabunusi_code1.append('https://kabutan.jp/stock/holder?code={:s}'.format(columns_jp2.replace('.JP','')))
            kekka=pd.DataFrame(np.array([meigara_code1,name_code1,gyousyu_code1,kabunusi_code1,[str(columns_jp)]*len(max),[str(syousai.at['銘柄名',columns_jp])]*len(max),[str(syousai.at['業種',columns_jp])]*len(max),[kabunusi_code2]*len(max),keisuu,max,chart_url],dtype=object).T, columns=['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1','銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2','相関','遅れ','チャート']) #結果をまとめたデータを作成します。
            sort=pd.concat((sort_past,kekka.query('相関> {}'.format(float(self.soukanentry.get())))),sort=False) #わかりやすいように相関係数が高い順に並び変えておきます。0.7以下はほぼ相関がないので、この時点で消します。
            sort_past=sort
        sort=sort.sort_values(by='相関',ascending=False) #相関係数で並び替えます。
        print('解析終了')
        sort_t=sort[sort['銘柄コード_code1']!=sort['銘柄コード_code2']] #同じ銘柄同士による結果を排除しておきます
        result=sort_t[::2] #このままでは2024と2025の組み合わせが二通り出てしまうので偶数行だけ抽出します
        if self.sortopt.get():
            result=result[result['業種_code1']==result['業種_code2']]
        result=result.reset_index(drop=True)
        for i in result.index.values:
            if result.at[i,'遅れ']<0:
                tmp=result.loc[i,['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1']].values
                result.loc[i,['銘柄コード_code1','銘柄名_code1','業種_code1','株主構成_code1']]=result.loc[i,['銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2']].values
                result.loc[i,['銘柄コード_code2','銘柄名_code2','業種_code2','株主構成_code2']]=tmp
                result.at[i,'遅れ']=-result.at[i,'遅れ']
        result.to_csv(self.parentFolder + '/' + self.result_dir_path + '/result_{:s}.csv'.format(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')),encoding='cp932')  # 結果の保存
        print('結果を保存しました')
    def kobetu_now(self):
        self.eachFrame.tkraise()


def main():
    root = tk.Tk()
    app = application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()

