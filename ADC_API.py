import requests
from pathlib import Path
import json
import time

URL = 'https://east.albion-online-data.com/api/v2/stats/prices/'


def read_items_data():
    #返回items.json的list
    current_directory = Path(__file__).parent
    item_json_path = current_directory / 'items.json'
    with open(item_json_path,'r',encoding='utf-8') as items_file:
        items_database = json.load(items_file)
    return items_database

def name_to_idList(name):
    #把item中文名字按表查找id,输出查询字符串之子串的id列表
    items_database = read_items_data()
    target_list = [] 
    for item_info in items_database:
        if item_info['LocalizedNames'] is not None:
            if "ZH-CN" in item_info['LocalizedNames']:
                if name in item_info['LocalizedNames']["ZH-CN"]:
                    target_list.append(item_info['UniqueName'])
    print(target_list)
    if target_list == '':
        print('没有查询到item表中有对应的装备，可能是输入错误或者缺少该本地化项目')
        return 0
    else:
        return target_list
def id_to_name(id):
    #返回id对应的（唯一）对应的本地化item名称
    
    items_database = read_items_data()
    target_name = ''
    for item_info in items_database:
       if id == item_info['UniqueName']:
           if item_info['LocalizedNames'] is not None:
            target_name = item_info['LocalizedNames']["ZH-CN"]
    return target_name
    
    
def get_item_lists(id_list):
    #将获取到的id_list（通常包括附魔0-4级的所有id）请求数据
    if id_list == []:
        return 0
    api_url=URL
    ids = ",".join(id_list)
    #连接字符串，组合为url中的请求参数部分
    api_url+=ids
    api_url+='?locations=Blackmarket'
    responce = requests.get(url=api_url)
    if responce.status_code == 200:
        json = responce.json()
        print(json)
        return(json)
    else:
        print(f'请求黑市数据库失败,状态码：{responce.status_code}')
        return -1

#成功请求返回json，请求失败返回-1,数据库中没有查询到id返回0

if __name__ == "__main__":
    id_list=name_to_idList("禅师级背包")
    # get_item_lists(id_list)
    # id_to_name('T4_2H_DUALSICKLE_UNDEAD@4')
    