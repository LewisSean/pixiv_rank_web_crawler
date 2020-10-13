import csv
import json
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter.filedialog import askdirectory,askopenfilename
from tkinter.ttk import Combobox
import queue
from PixivRank import pixiv,demo_selenium, get_rank_list_v2
import os


class Application(Frame):

    def __init__(self, master=None):
        self._p = pixiv()
        self.folder = 'PixivImage'
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.srcolls = 2
        self.wait = 3
        self.result = []
        self.mode = 'monthly'
        self.tags = []
        self.range = 100
        self.thread = 24
        self.maxThreads = 24
        self.path = "C:/myApps/chromedriver/chromedriver.exe"
        f = open('tags.txt', 'r', encoding='utf-8')
        self.translation: dict = json.loads(f.readline())
        f.close()

        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        cur_row = 0
        Label(self, text="chromedriver:").grid(row=cur_row, column=0,sticky="ew")
        self.locInput = Entry(self)
        self.locInput.insert(0, self.path)
        self.locInput.grid(row=cur_row, column=1)
        self.dirverButton = Button(self, text='get its location', command=self.selectPath)
        self.dirverButton.grid(row=cur_row, column=2,sticky="ew")

        cur_row += 1
        Label(self, text="tag:").grid(row=cur_row, column=0, sticky="ew")
        self.tagInput = Entry(self)
        self.tagInput.grid(row=cur_row, column=1)
        self.tagButton = Button(self, text='add your tag', command=self.addTags)
        self.tagButton.grid(row=cur_row, column=2,sticky="ew")

        cur_row += 1
        self.getTagButton = Button(self, text='check added tags', command=self.getTags)
        self.getTagButton.grid(row=cur_row, column=0,sticky="ew")
        self.alertButton = Button(self, text='reset tags', command=self.reset)
        self.alertButton.grid(row=cur_row, column=1,sticky="ew")
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=cur_row, column=2,sticky="ew")

        cur_row += 1
        Label(self, text="").grid(row=cur_row, column=0, sticky="ew")

        cur_row += 1
        Label(self, text="search range(100 etc.):").grid(row=cur_row, column=0, sticky="ew")
        self.rangeInput = Entry(self)
        self.rangeInput.insert(0, self.range)
        self.rangeInput.grid(row=cur_row, column=1)
        self.rangeButton = Button(self, text='enter', command=self.setRange)
        self.rangeButton.grid(row=cur_row, column=2,sticky="ew")

        cur_row += 1
        Label(self, text="multi_threads:").grid(row=cur_row, column=0, sticky="ew")
        self.threadInput = Entry(self)
        self.threadInput.insert(0, self.thread)
        self.threadInput.grid(row=cur_row, column=1)
        self.threadButton = Button(self, text='enter', command=self.setThreads)
        self.threadButton.grid(row=cur_row, column=2,sticky="ew")

        cur_row += 1
        Label(self, text="search mode:").grid(row=cur_row, column=0, sticky="ew")
        self.modes = ['daily', 'weekly', 'monthly', 'rookie', 'original', 'male', 'female']
        self.modeList = Combobox(self,values=self.modes)
        self.modeList.set('monthly')
        self.modeList.grid(row=cur_row, column=1)
        self.modeButton = Button(self, text='enter', command=self.setMode)
        self.modeButton.grid(row=cur_row, column=2,sticky="ew")

        cur_row += 1
        Label(self, text="").grid(row=cur_row, column=0, sticky="ew")

        cur_row += 1
        self.searchButton = Button(self, text='run', command=self.search)
        self.searchButton.grid(row=cur_row, column=0, sticky="ew")
        self.showButton = Button(self, text='results', command=self.show)
        self.showButton.grid(row=cur_row, column=1, sticky="ew")
        self.saveButton = Button(self, text='save', command=self.save)
        self.saveButton.grid(row=cur_row, column=2, sticky="ew")

    def setMode(self):
        _str = self.modes[self.modeList.current()]
        if _str != '':
            self.mode = _str


    def search(self):
        # _refs = demo_selenium('https://www.pixiv.net/ranking.php?mode={}'.format(self.mode),
        #                       scrolls=self.srcolls, num=self.range, wait=self.wait)
        _refs = get_rank_list_v2(self.mode, self.range, self.tags)
        '''
        pids = []
        for ref in _refs:
            ref = ref[ref.rfind('/') + 1: len(ref)]
            pids.append(ref)
        '''
        print('search tags:{}'.format(" | ".join(self.tags)))
        print('multi-threads:{}'.format(self.thread))
        print('search website: https://www.pixiv.net/ranking.php?mode={}'.format(self.mode))
        _que = self._p.multi_info_data(_refs, [], self.thread)

        if _que.qsize() == 0:
            messagebox.showinfo('Message', 'no result found!')
        else:
            self.result = []
            while _que.qsize() > 0:
                self.result.append(_que.get())

        print("----------------------")
        print(self.result)

        '''if len(_refs) < self.range:
            # messagebox.showinfo('Message', 'Fail to get the FULL rank list, due to unreliable network etc.\n '
            #                                'Certain Operation have been made, you can try run again.')
            self.srcolls += 1
            self.wait += 2'''

    def show(self):
        if len(self.result) > 0:
            folder = os.path.join(self.root, self.folder)
            if not os.path.exists(folder):
                os.mkdir(folder)

            headers = ['img url', 'author id', 'Tags_cn', 'Tags_jp']
            # data list of 4: 0 image id | 1 header | 2 uid | 3 tags_cn  |  4 tags_jp
            file = os.path.join(folder, str('results.csv'))
            with open(file, 'w', encoding='utf-8') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(headers)
                for data in self.result:
                    print(['https://www.pixiv.net/artworks/' + data[0],
                     data[2], "  ".join(data[3]), "  ".join(data[4])])
                    f_csv.writerow(['https://www.pixiv.net/artworks/'+data[0],
                                    data[2], "  ".join(data[3]), "  ".join(data[4])])

    def setThreads(self):
        _thread = int(self.threadInput.get().strip())
        if 0 < _thread <= self.maxThreads:
            self.thread = _thread

    def setRange(self):
        _range = int(self.rangeInput.get().strip())
        if _range > 0:
            self.range = _range

    def selectPath(self):
        _path = askopenfilename()
        if not _path.endswith('chromedriver.exe'):
            messagebox.showinfo('Message', 'wrong location!\nChoose chromedriver.exe!')
        else:
            self.path = _path
            self.locInput.insert(0, self.path)

    def addTags(self):
        _str = self.tagInput.get().strip()
        if _str != '' and self.translation[_str]:
            self.tags.append(self.translation[_str])
            self.tagInput.delete(0, END)

    def getTags(self):
        str_list = " | ".join(self.tags)
        messagebox.showinfo('Message', 'the tags are %s' % str_list)

    def reset(self):
        self.tags = []

    def save(self):
        if len(self.result) > 0:
            task_que = queue.Queue()
            for item in self.result:
                task_que.put(item)
            self._p.multi_download_img(task_que,self.thread)




def transfer(tag):

    return tag


app = Application()
# 设置窗口标题:
app.master.title('Pixiv WebCrawler by Sean')
# 主消息循环:
app.mainloop()