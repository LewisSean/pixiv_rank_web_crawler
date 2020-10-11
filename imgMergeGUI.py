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
        self.imgs = []
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        Label(self, text="target row:").grid(row=0, column=0)
        self.rowInput = Entry(self)
        self.rowInput.grid(row=0, column=1)
        Label(self, text="target column:").grid(row=1, column=0)
        self.colInput = Entry(self)
        self.colInput.grid(row=1, column=1)

        self.alertButton = Button(self, text='get image address', command=self.selectPath)
        self.alertButton.grid(row=2, column=0,sticky="ew")
        self.alertButton = Button(self, text='get images to merge', command=self.getImgs)
        self.alertButton.grid(row=2, column=1,sticky="ew")
        self.alertButton = Button(self, text='reset', command=self.reset)

        self.alertButton.grid(row=3, column=0,sticky="ew")
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=3, column=1,sticky="ew")

        self.alertButton = Button(self, text='merge', command=self.merge)
        self.alertButton.grid(row=4, column=0,sticky="ew")
        self.alertButton = Button(self, text='save', command=self.save)
        self.alertButton.grid(row=4, column=1,sticky="ew")


    def selectPath(self):
        self.path = askopenfilename()
        # messagebox.showinfo('Message', 'the address is %s' % self.path)
        if self.path != '' and (self.path.endswith('.jpg') or self.path.endswith('.png')):
            self.imgs.append(self.path)

    def getImgs(self):
        str_list = " ".join(self.imgs)
        messagebox.showinfo('Message', 'the imgs are \t  %s' % str_list)

    def reset(self):
        self.path = ''
        self.imgs = []
        self.row = 1
        self.column = 1
        self.result = None

    def merge(self):
        self.row = int(self.rowInput.get())
        self.column = int(self.colInput.get())
        self.result = imgMerge.merge(self.imgs, (self.row, self.column))
        self.result.show()

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
