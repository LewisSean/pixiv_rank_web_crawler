from os import listdir
from PIL import Image


def merge(listD, mybox):
    # 获取当前文件夹中所有JPG图像
    # listD = listdir(path)
    print(listD)
    print(mybox)
    im_list = [Image.open(fn) for fn in listD if (fn.endswith('.jpg') or fn.endswith('.png'))]
    # 图片转化为相同的尺寸
    ims = []
    my_size = im_list[0].size
    for i in im_list:
        print(i.size)
        new_img = i.resize(my_size, Image.BILINEAR)
        # new_img.show()
        ims.append(new_img)
    # 单幅图像尺寸
    width, height = ims[0].size
    # 创建空白长图
    result = Image.new(ims[0].mode, (width * mybox[0], height * mybox[1]))
    # 拼接图片
    for i, im in enumerate(ims):
        print((i, im.size))
        result.paste(im, box=((i % mybox[0]) * width, (int)(i / mybox[0]) * height))
    # 保存图片
    return result


if __name__ == '__main__':
    path = 'C:/Users/Sean/Desktop/topingjie/1/'
    # result = merge(path, (2, 1))
    # result.save(path + 'res1.png')
