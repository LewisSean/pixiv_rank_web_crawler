import time
from urllib import request
import threading
import queue
import re
import os
from selenium import webdriver
import json


class pixiv:
    def __init__(self):
        self.folder = 'PixivImage'
        self.web_coding = 'utf-8'
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.DefaultHeader = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "",
            "Connection": "keep-alive",
        }
        self.data_low = []
        self.num = 0

    def _http(self, url, headers, Obj=False):
        res = request.urlopen(request.Request(url, headers=headers, method='GET'))
        if Obj:
            return res
        else:
            return res.read().decode(self.web_coding, "ignore")

    def data_image_thread(self, url_id, keywords, _res_que):
        _header = self.DefaultHeader.copy()
        # https://www.pixiv.net/member_illust.php?mode=medium&illust_id=84306692
        _header["Referer"] = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(url_id)
        # https://www.pixiv.net/touch/ajax/illust/details?illust_id=84306692    （未用utf-8解码的网页源码，错误信息报文）
        _url_data = "https://www.pixiv.net/touch/ajax/illust/details?illust_id={}".format(url_id)

        _data_details = self._http(_url_data, _header)
        # data_url，形如 https://i.pximg.net/img-master/img/2020/09/12/00/00/03/84306692_p0_master1200.jpg
        # 访问时请求报文必须有Referer，位置是该图片当前的pixiv主页
        # data_uid 作者的uid
        # data_tags 作品的tag
        data_tags = self.sort_tags_cn(_data_details)
        print(data_tags)
        if len(keywords) == 0 or have_keyword(data_tags, keywords):
            data_url = self.sort_data(re.findall('"url_big":"[^"]*"', _data_details))
            data_uid = str(str(str(re.findall('"user_id":"[^"]*"', _data_details)[0]).split(':', 1)[-1]).strip('"'))
            for url in data_url:
                _res_que.put([url, _header, data_uid, data_tags])
                print('   ------->add new item')

    def sort_data(self, data):
        _data = []
        for item in data:
            if item not in _data:
                _data.append(item)
        return [str(str(item).replace('\\', '').split(':', 1)[-1]).strip('"') for item in _data]

    def sort_tags_japanese(self, data):
        display_tags = re.findall('"display_tags":\[[^\[\]]*', data)
        tags = re.findall('"tag":[^,]*', display_tags[0])
        tags_unicode = []
        for tag in tags:
            # DeprecationWarning: invalid escape sequence '\/'  source: Fate/GO   23333333
            tags_unicode.append(tag[7:len(tag) - 1].encode('utf-8').decode('unicode_escape'))
        return tags_unicode

    def sort_tags_cn(self, data):
        display_tags = re.findall('"display_tags":\[[^\[\]]*', data)
        if len(display_tags) > 0:
            tags = re.findall('"translation":[^,]*', display_tags[0])
            tags_unicode = []
            for tag in tags:
                # DeprecationWarning: invalid escape sequence '\/'  source: Fate/GO   23333333
                tags_unicode.append(tag[15:len(tag) - 1].encode('utf-8').decode('unicode_escape'))
            return tags_unicode
        return None

    # data list of 4: 0 image id | 1 header | 2 uid | 3 tags
    def get_data_by_item_thread(self, data):
        image = self._http(data[0], data[1], True)
        if image.code != 200:
            raise Exception("Pixiv Image: [{} | {}]".format(image.code, data[0]))
        self.write(str("{}_{}").format(str(data[2]), str(str(data[0]).rsplit('/', 1)[-1])), image.read())
        print(data[3])

    def write(self, name, data):
        folder = os.path.join(self.root, self.folder)
        if not os.path.exists(folder):
            os.mkdir(folder)
        file = os.path.join(folder, str(name))
        fp = open(file, 'wb')
        fp.write(data)
        fp.close()
        self.num += 1
        print("Pixiv Image: [ OK | {} ]".format(file))

    def add_downloadInfo_queue(self, _queue, task_que):
        while task_que.qsize() > 0:
            item = task_que.get()
            print(item)
            _queue.put(item)

    def multi_info_data(self, data_list=None, keywords=[], max=24):
        time_start = time.time()

        if not data_list:
            data_list = self.data_low
        print('----------multi_info_data----------')
        _threads = []
        _queue = queue.Queue(maxsize=max)
        res_que = queue.Queue()
        task_main = threading.Thread(target=self.add_queue, args=(_queue, data_list))
        task_main.setName("TaskMain")
        task_main.setDaemon(True)
        task_main.start()
        while _queue.qsize() > 0:
            if len(_threads) >= max:
                for _item in _threads.copy():
                    if not _item.is_alive():
                        _threads.remove(_item)
                continue
            item = _queue.get()
            task = threading.Thread(target=self.data_image_thread, args=(item, keywords, res_que))
            task.setDaemon(True)
            task.start()
            _threads.append(task)
        for _task in _threads:
            _task.join()

        time_end = time.time()
        print('time cost', time_end - time_start, 's')
        return res_que

    def multi_download_img(self, task_que, max=24):
        time_start = time.time()

        print("New task_que:", task_que.qsize())
        _threads = []
        _queue = queue.Queue(maxsize=max)
        task_main = threading.Thread(target=self.add_downloadInfo_queue, args=(_queue, task_que))
        task_main.setName("TaskMain")
        task_main.setDaemon(True)
        task_main.start()
        while _queue.qsize() > 0:
            if len(_threads) >= max:
                for _item in _threads.copy():
                    if not _item.is_alive():
                        _threads.remove(_item)
                continue
            item = _queue.get()
            task = threading.Thread(target=self.get_data_by_item_thread, args=(item,))  # 不可以是(item)，会被误认为有5个参数
            task.setDaemon(True)
            task.start()
            _threads.append(task)
        for _task in _threads:
            _task.join()
        print("\nTotal Image: ", self.num)

        time_end = time.time()
        print('time cost', time_end - time_start, 's')

    def add_queue(self, _queue, data_list=None):
        for item in data_list:
            _item = str(item).strip()
            if item and _item:
                _queue.put(_item)
    # ------------------------old version, not effective------------------------------
    '''
    def data_image(self, url_id):
        _header = self.DefaultHeader.copy()
        # https://www.pixiv.net/member_illust.php?mode=medium&illust_id=84306692
        _header["Referer"] = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(url_id)
        # https://www.pixiv.net/touch/ajax/illust/details?illust_id=84306692    （未用utf-8解码的网页源码，错误信息报文）
        _url_data = "https://www.pixiv.net/touch/ajax/illust/details?illust_id={}".format(url_id)

        _data_details = self._http(_url_data, _header)
        data_url = self.sort_data(re.findall('"url_big":"[^"]*"', _data_details))
        data_uid = str(str(str(re.findall('"user_id":"[^"]*"', _data_details)[0]).split(':', 1)[-1]).strip('"'))
        data_tags = self.sort_tags_cn(_data_details)
        # data_url，形如 https://i.pximg.net/img-master/img/2020/09/12/00/00/03/84306692_p0_master1200.jpg
        # 访问时请求报文必须有Referer，位置是该图片当前的pixiv主页
        # data_uid 作者的uid
        # data_tags 作品的tag
        return data_url, _header, data_uid, data_tags

    # 核心函数，通过图片的id，调用data_image获取下载该图片的信息，调用write下载
    def get_data_by_item(self, item, keywords):
        data = self.data_image(item)
        if have_keyword(data[3], keywords) or len(keywords) == 0:
            for data_url in data[0]:
                image = self._http(data_url, data[1], True)
                if image.code != 200:
                    raise Exception("Pixiv Image: [{} | {}]".format(image.code, data[0]))
                self.write(str("{}_{}").format(str(data[2]), str(str(data_url).rsplit('/', 1)[-1])), image.read())
                print(data[3])


    def multi_data(self, data_list=None, keywords=[], max=24):
        time_start = time.time()

        if not data_list:
            data_list = self.data_low
        print("New Item:", len(data_list))
        _threads = []
        _queue = queue.Queue(maxsize=max)
        task_main = threading.Thread(target=self.add_queue, args=(_queue, data_list))
        task_main.setName("TaskMain")
        task_main.setDaemon(True)
        task_main.start()
        while _queue.qsize() > 0:
            if len(_threads) >= max:
                for _item in _threads.copy():
                    if not _item.is_alive():
                        _threads.remove(_item)
                continue
            item = _queue.get()
            task = threading.Thread(target=self.get_data_by_item, args=(item, keywords))
            task.setDaemon(True)
            task.start()
            _threads.append(task)
        for _task in _threads:
            _task.join()
        print("\nTotal Image: ", self.num)

        time_end = time.time()
        print('time cost', time_end - time_start, 's')
    '''


# scrolls = 2 400~500 imgs
# scrolls = 3 500 imgs
def demo_selenium(url, scrolls, num, wait=3):
    driver = webdriver.Chrome("C:/myApps/chromedriver/chromedriver.exe")
    driver.get(url)

    for t in range(scrolls):
        scroll(driver, 100000)
    # scroll(driver, 0)
    time.sleep(wait)
    hrefs = []
    # 匹配tag为a的所有标签，这些标签的属性class='work  _work  '  且属性target = '_blank'
    for link in driver.find_elements_by_xpath("//a[@href and @target='_blank']"):
        ref = link.get_attribute('href')
        if ref.find("artworks") != -1:
            hrefs.append(ref)

    driver.quit()
    hrefs = sorted(set(hrefs), key=hrefs.index)    # 去重   不可以使用 hrefs = list(set(hrefs)) 会打乱顺序
    print(len(hrefs))
    if len(hrefs) > num:
        hrefs = hrefs[0:num]
    return hrefs


def scroll(driver, position):
    # 将滚动条移动到页面的position位置
    js = "var q=document.documentElement.scrollTop=%d" % position
    driver.execute_script(js)
    time.sleep(1)


def have_keyword(item, keywords):
    for tag in item:
        for keyword in keywords:
            if tag.find(keyword) != -1:
                return True
    return False


# mode = ['daily', 'weekly', 'monthly', 'rookie', 'original', 'male', 'female']
# pages start from 1 (ridiculous)
def get_rank_list_v2(mode, num, tags):
    pages = int((num-1) / 50 + 1)
    _threads = []
    res_que = queue.Queue()
    for p in range(1, pages+1):  # 前闭后开
        url = 'https://www.pixiv.net/ranking.php?mode={}&p={}&format=json'.format(mode, p)
        task = threading.Thread(target=get_pages_id, args=(url, res_que, p))
        task.setDaemon(True)
        task.start()
        _threads.append(task)
    for _task in _threads:
        _task.join()

    list = {}
    while res_que.qsize() > 0:
        # python 'str' object has no attribute 'read'
        # json.load(response) or json.loads(response.read())
        part = res_que.get()
        list[part[0]] = json.loads(part[1].read())['contents']

    rank_list = []
    for key in sorted(list.keys()):
        print(key)
        for item in list[key]:
            # print(item['tags'])
            if len(tags) == 0 or have_keyword(item['tags'], tags):
                rank_list.append(item['url'][item['url'].rfind('/')+1:item['url'].rfind('_')-3])

    print(rank_list)
    return rank_list


def get_pages_id(url, res_que, id):
    defaultHeader = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "",
        "Connection": "keep-alive",
    }
    res_que.put([id, request.urlopen(request.Request(url, headers=defaultHeader, method='GET'))])


if __name__ == '__main__':
    get_rank_list_v2('daily', 200, ['Fate'])

    '''path = 'https://www.pixiv.net/ranking.php?mode=monthly'
    refs = demo_selenium(path, 2, 100)
    print(refs)
    items = []
    for ref in refs:
        ref = ref[ref.rfind('/')+1: len(ref)]
        items.append(ref)

    print(items)'''


    '''
    p = pixiv()
    que = p.multi_info_data(items, ['碧蓝航线', '初音未来', '鬼灭之刃'], 12)
    p.multi_download_img(que, 24)
    '''

    '''p = pixiv()
    path = 'https://www.pixiv.net/artworks/84306692'
    print(p.data_image('84306692')[3])'''

    # 无法成功，反爬虫
    # print(p._http('https://www.pixiv.net/artworks/84306692', p.DefaultHeader))
