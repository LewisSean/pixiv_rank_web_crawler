from tkinter import *
import tkinter.messagebox as messagebox
from tkinter.filedialog import askdirectory,askopenfilename
import imgMerge
from PIL import Image
from os import listdir

class Application(Frame):

    def __init__(self, master=None):
        self.result = None
        self.row = 1
        self.column = 1
        self.path = ''
        self.tags = []
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        cur_row = 0
        Label(self, text="chromedriver:").grid(row=cur_row, column=0,sticky="ew")
        self.locInput = Entry(self)
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
        self.checkButton = Button(self, text='check added tags', command=self.getTags)
        self.getTagButton.grid(row=cur_row, column=0,sticky="ew")
        self.alertButton = Button(self, text='reset tags', command=self.reset)
        self.alertButton.grid(row=cur_row, column=1,sticky="ew")
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=cur_row, column=2,sticky="ew")

    def selectPath(self):
        _path = askopenfilename()
        if not _path.endswith('chromedriver.exe'):
            messagebox.showinfo('Message', 'wrong location!\nChoose chromedriver.exe!')
        else:
            self.path = _path
            self.locInput.insert(0, self.path)

    def addTags(self):
        _str = self.tagInput.get().strip()
        if _str != '':
            self.tags.append(_str)
            self.tagInput.delete(0, END)

    def getTags(self):
        str_list = " | ".join(self.tags)
        messagebox.showinfo('Message', 'the tags are %s' % str_list)

    def reset(self):
        self.tags = []
        self.result = None

    def save(self):
        if self.result is not None:
            if self.path.rfind('/') != -1:
                savePath = self.path[0:self.path.rfind('/')+1]
            else:
                savePath = 'C:/Users/Sean/Desktop/'
            self.result.save(savePath + 'merge_img.png')
            messagebox.showinfo('Message', 'save success!')
        else:
            messagebox.showinfo('Message', 'save fail!')


app = Application()
# 设置窗口标题:
app.master.title('Hello World')
# 主消息循环:
app.mainloop()