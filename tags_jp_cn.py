import json
import queue
import re
from urllib import request
import requests
from PixivRank import get_rank_list_v2, pixiv
import demjson

# target: to get japanese tags corresponding to Chinese tags
# step 1:get https://www.pixiv.net/tags for JP tags
# step 2:post https://www.pixiv.net/rpc_language_setting.php to switch to CN
# step 3:get https://www.pixiv.net/tags for CN tags (use urlopen of urllib.request, requests still gets JP web page)
# step 4:get dict
# result: failure, cause len(cn_tags) != len(jp_tags)
def get_cn_jp_tags():
    defaultHeader = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "",
        "Connection": "keep-alive",
    }
    r = requests.get(url="https://www.pixiv.net/tags", params=defaultHeader)

    data = r.text
    display_tags: list = re.findall('"tag-value icon-text">[^<]*<', data)

    popular_tags = []
    for item in display_tags:
        popular_tags.append(item[item.find('>') + 1:len(item) - 1])

    for tag in popular_tags:
        print(tag)

    data = {
        'mode': 'set',
        'tt': '427cd279d273cc36578d9e8372a8908b',
        'user_language': 'zh'
    }
    # -----------------------------switch to chinese----------------------
    requests.post(url="https://www.pixiv.net/rpc_language_setting.php", data=data)

    # ---------------------------------------------------------------------

    r = request.urlopen(request.Request("https://www.pixiv.net/tags", headers=defaultHeader, method='GET'))
    data = r.read().decode('utf-8')
    '''仍然为日语标签
    r = requests.get(url="https://www.pixiv.net/tags", params=defaultHeader)
    data = r.text
    '''
    display_tags: list = re.findall('"tag-value icon-text">[^<]*<', data)

    popular_tags_cn = []
    for item in display_tags:
        popular_tags_cn.append(item[item.find('>') + 1:len(item) - 1])

    for tag in popular_tags_cn:
        print(tag)

    print(len(popular_tags) == len(popular_tags_cn))
    tag_pairs = {}
    for i in range(0, len(popular_tags_cn)):
        tag_pairs[popular_tags_cn[i]] = popular_tags[i]

    print('________________________________________________________________')
    for key in tag_pairs.keys():
        print('{}: {}'.format(key, tag_pairs[key]))


def get_cn_jp_tags_v2(filename: str = ''):
    p = pixiv()
    refs = get_rank_list_v2('monthly', 100, [])
    que: queue.Queue = p.multi_info_data(refs, [], 24)
    pairs = {}
    while que.qsize() > 0:
        img_pairs: dict = que.get()[5]
        for key in img_pairs.keys():
            pairs['"'+key+'"'] = '"'+img_pairs[key]+'"'

    f = open(filename, 'w', encoding='utf-8')
    f.write('{')
    flag = 0
    for key in pairs.keys():
        if flag == 0:
            f.write('{}: {}'.format(key, pairs[key]))
            flag = 1

        f.write(', {}: {}'.format(key, pairs[key]))
    f.write('}')
    f.close()


# get_cn_jp_tags_v2('tags.txt')
f = open('tags.txt', 'r', encoding='utf-8')
string: str = f.readline()
print(string)
# json loads的格式： { "label":[]/"value" }
res = json.loads(string)
f.close()
print(len(res))
print(type(res))
print(res)

