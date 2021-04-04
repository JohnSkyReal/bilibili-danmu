import requests
from bs4 import BeautifulSoup
import datetime
import random
import time
import os


def get_season(url):  # 获取html
    try:
        return requests.get(url, timeout=5).json()
    except Exception as e:
        raise  # raise提取出错误，中断程序


def extract_metadata(j_season):
    metadata = []
    episodes = j_season["result"]["episodes"]
    for each in episodes:
        aid = each["aid"]
        bvid = each["bvid"]
        cid = each["cid"]
        long_title = each["long_title"]  # 剧集标题全称
        title = each["title"]  # 剧集标题简写
        share_copy = each["share_copy"]  # 分享的标题，很全面
        share_url = each["share_url"]
        short_link = each["short_link"]
        metadata.append([cid, bvid, share_copy])
    return metadata


def get_html(url):  # 获取html
    try:
        r = requests.get(url, timeout=5)  # 请求超过5秒，报错。设置响应时间
        # soup = BeautifulSoup(html.content, "html.parser")
        # soup = soup.prettify()
        # print(soup)
        return r
    except Exception as e:
        raise  # raise提取出错误，中断程序


def get_content(r):  # 解析html，获取想要的东西
    soup = BeautifulSoup(r.content, "html.parser")
    result_list = []
    d_tags = soup.find_all("d")
    for i in d_tags:
        text = i.get_text().strip()  # 弹幕文本内容
        t_video = int(float(i["p"].split(',')[0]))  # 该条弹幕在视频中出现的时间
        # t_video = str(datetime.timedelta(seconds=int(float(i["p"].split(',')[0]))))  # 该条弹幕在视频中出现的时间
        # print(text)
        # print(t_video)
        result_list.append([text, t_video])
    return result_list


def get_target(text, result_list):
    text_list = [word.strip() for word in text.split(' ')]
    time_dict = {}
    out_list = []
    for each in result_list:
        for word in text_list:
            if word in each[0]:
                # print(each)
                if each[1] not in time_dict.keys():
                    time_dict[each[1]] = each[0]
                else:
                    time_dict[each[1]] += ' / ' + each[0]
    time_list = sorted(time_dict.items(), key=lambda x: x[0], reverse=False)
    for each in time_list:
        out_list.append([str(datetime.timedelta(seconds=each[0])), each[1]])
    return out_list


def output(path, data):
    with open(path,'w',encoding='utf-8') as f:
        for item in data:
            f.write(str(item[0]) + '\t' + str(item[1]) + '\n')


def save_xml(path, r):
    with open(path, "wb")as f:
        f.write(r.content)


def main():
    # 传入番剧或电视剧的season_id号，与想要定位的弹幕（多关键词用空格隔开）
    # target_text = '奇妙比喻 奇妙的比喻 神奇比喻 神奇的比喻'
    target_text = '比喻'
    # target_text = '一库贼 一狗贼'
    season_id = 28572
    # season_id = 5069

    init_url = 'https://api.bilibili.com/pgc/view/web/season?season_id=' + str(season_id)
    j_season = get_season(init_url)
    metadata = extract_metadata(j_season)

    if not os.path.exists(r'cache_xml'):
        os.mkdir(r'cache_xml')
    if not os.path.exists(r'cache_time'):
        os.mkdir(r'cache_time')

    for each_ep in metadata:
        cid = each_ep[0]
        BV = each_ep[1]
        title = each_ep[2]
        print(title)
        print('BV:{}，cid:{}'.format(BV, cid))
        # 根据cid号获取弹幕xml文件
        danmu_url = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cid)
        r = get_html(danmu_url)
        # 解析xml文件，提取弹幕内容与在视频中出现时间[[text, time], []]
        out_xml = 'cache_xml/' + BV + '_' + str(cid) + '.xml'
        save_xml(out_xml, r)
        result_list = get_content(r)
        # 定位目标弹幕在视频中出现时间
        time_list = get_target(target_text, result_list)
        if time_list:
            for each in time_list:
                print('时刻：{}，弹幕：{}'.format(each[0], each[1]))
        else:
            print('QAQ本集没有找到您期待的内容呦~')
        # print(time_list)
        out_path = 'cache_time/' + BV + '_time.txt'
        output(out_path, time_list)
        wait_time = random.randint(3, 7)  # 随机产生时间
        print("wait_time is %d s" % wait_time)
        time.sleep(wait_time)


if __name__ == '__main__':
    main()
