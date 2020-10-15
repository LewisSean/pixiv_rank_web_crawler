from PIL import Image
import os


def padding(path, my_size: tuple = (1920, 1080), color: tuple = (0, 0, 0), mode=0):
    # 填充指定文件夹中所有JPG或PNG图像,返回与my_size长宽比相同的填充图片,只能上下或左右填充, color定义填充色，默认黑色
    # mode 0 左右填充   mode 1 上下填充
    print(path)

    files = [fn for fn in os.listdir(path) if not fn.startswith('padding_') and (fn.endswith('.jpg') or fn.endswith('.png'))]
    im_list = [[fn, Image.open(os.path.join(path, fn))] for fn in files]
    print(len(im_list))
    if mode == 1:
        im_list = [img for img in im_list if img[1].size[0]*my_size[1] >= img[1].size[1]*my_size[0]]
    if mode == 0:
        im_list = [img for img in im_list if img[1].size[0] * my_size[1] >= img[1].size[1] * my_size[0]]

    print(len(im_list))

    for item in im_list:
        img = item[1]
        print(img.size)
        result = Image.new(img.mode, my_size, color=color)
        if mode == 0:
            new_wid = int(img.size[0] / img.size(1) * my_size[1])
            img = img.resize((new_wid, my_size[1]), Image.BILINEAR)
            result.paste(img, box=(int((my_size[0]-new_wid)/2, 0)))
        if mode == 1:
            new_hei = int(img.size[1] / img.size[0] * my_size[0])
            img = img.resize((my_size[0], new_hei), Image.BILINEAR)
            result.paste(img, box=(0, int((my_size[1]-new_hei)/2)))
        result.save(os.path.join(path, 'padding_{}.png'.format(item[0][0: len(item[0])-4])))


def sort_img(path: str, save_path: str, my_size: tuple = (1920, 1080), deviation = 0.05):
    files = [fn for fn in os.listdir(path) if (fn.endswith('.jpg') or fn.endswith('.png'))]
    im_list = [[fn, Image.open(os.path.join(path, fn))] for fn in files]
    im_list = [img for img in im_list if
               my_size[0] / my_size[1] - deviation <= img[1].size[0] / img[1].size[1] <= my_size[0] / my_size[1] + deviation]
    for img in im_list:
        img[1].save(os.path.join(save_path, 'OK_{}.png'.format(img[0][0: len(img[0]) - 4])))


padding('C:/Users/Sean/PycharmProjects/web_crawler/imgs', mode=1)
# sort_img('C:/Users/Sean/Pictures/Saved Pictures/', 'C:/Users/Sean/PycharmProjects/web_crawler/imgs')


'''
files_des = [fn for fn in os.listdir('C:/Users/Sean/Pictures/bkg_album_std')
             if (fn.endswith('.jpg') or fn.endswith('.png'))]
files_src = [fn for fn in os.listdir('C:/Users/Sean/PycharmProjects/web_crawler/imgs')
             if (fn.endswith('.jpg') or fn.endswith('.png'))]
files_src = [fn for fn in files_src if not 'padding_'+fn[3:len(fn)] in files_des]
print(files_src)
im_list = [[fn, Image.open(os.path.join('C:/Users/Sean/PycharmProjects/web_crawler/imgs', fn))] for fn in files_src]
for img in im_list:
    img[1].save(os.path.join('C:/Users/Sean/Pictures/bkg_album_std', img[0]))
'''

