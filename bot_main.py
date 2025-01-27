import requests
import re
import json
import time
import ADC_API
from datetime import datetime
from zoneinfo import ZoneInfo



TOKEN = "Bot 1/MzM4NzQ=/1waJJzIp1/TPECHSCdxGHA=="
HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
    }
URL = 'https://www.kookapp.cn'
SERVER_ID = '1906198267648059'
CHANNEL_ID = '9744163465012843'

class http_methods():
    resonse = 0

def get_channel_list():
    api_url = URL+f"/api/v3/channel/list?guild_id={SERVER_ID}"
    response = requests.get(api_url,headers=HEADERS)
    if response.status_code ==200:
        print(response.json())
def get_server_list():
    api_url = URL+"/api/v3/guild/list"
    response = requests.get(api_url,headers=HEADERS)
    if response.status_code ==200:
        print(response.json())
        

def UTCstringToBeijing(UTC_string):
    utc_time = datetime.strptime(UTC_string, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=ZoneInfo("UTC"))
    Beijing_time = utc_time.astimezone(ZoneInfo("Asia/Shanghai"))
    formatted_local_time = f"{Beijing_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
    return formatted_local_time

def get_msg_list():
    ##获取目标target_id的bot频道的消息列表
    api_url=URL+f"/api/v3/message/list?target_id={CHANNEL_ID}"
    try :
        response = requests.get(api_url,headers=HEADERS)
        if response.status_code == 200:
            response_json = response.json()
            msg_items = response_json['data']['items']
            print(f"成功获得消息列表")
            return msg_items
        else:
            print(f"请求失败，状态码：{response.status_code}\n")
            raise ValueError
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        return 'error'
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
        return 'error'
    except ValueError as json_err:
        print(f'解析错误:{json_err}')
        return 'error'
    
def post_msg(content,quete = ''):
    
    api_url = URL+'/api/v3/message/create'
    data = {
        "target_id":f"{CHANNEL_ID}",
        "type": 9,
        "content":content,
        "quote":quete
    }
    data = json.dumps(data)
    
    try :
        response = requests.get(api_url,data=data,headers=HEADERS)
        if response.status_code == 200:
            response_json = response.json()
            print(f"{response_json}")
            # msg_items = response_json['data']['items']
            return True
        else:
            print(f"请求失败，状态码：{response.status_code}\n")
            raise ValueError
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        return 'error'
    except requests.exceptions.RequestException as err:
        print(f"请求错误: {err}")
        return 'error'
    except ValueError as json_err:
        print(f'解析错误:{json_err}')
        return 'error'

def run_bot():
    last_msg_time = 0
    #记录最后一个消息的时间

    while True:
    #主循环 每五秒拉取一次信息并判断是否需要处理
        try:
            msg_list=get_msg_list()
        except:
            print("获取消息队列时发生错误")
        if last_msg_time == 0 :
            last_msg_time = msg_list[-1]['create_at']
            continue
        if msg_list == 'error':
            continue 
        for msg_item in msg_list:
            if msg_item['create_at'] > last_msg_time:
                content = msg_item['content']
                match=re.match(r'^item#.*@\d\.\d$',content)
                if match:
                # 对符合正则表达式的玩家信息进行回应
                # TODO: 获取content后面的信息
                    begin_time = time.time()
                    responce_content = ''
                    itemName_to_query = content[5:-4]
                    price_list = []
                    
                    id_list = ADC_API.name_to_idList(itemName_to_query)
                    if id_list == '':
                        responce_content = '本地化文档中没有找到该装备,原因可能是查询有误或是缺乏本地化文件。如确定无误，请报告Takanshi'
                    else :
                        responce_rows = ADC_API.get_item_lists(id_list)
                        if responce_rows == -1 :
                            responce_content = 'bot请求Albion Data Client服务器API失败或遭拒绝，请检查请求是否过于模糊（服务器不会跑路了吧(确信'
                        elif responce_rows == 0 :
                            responce_content = '本地化文档中没有找到该装备,原因可能是查询有误或是缺乏本地化文件。如确定无误，请报告Takanshi'
                        else:
                            for priceInfo in responce_rows:
                                #分离信息整理为list
                                if priceInfo['item_id'][1] != content[-3] :
                                    #-3位置是tier，-1位置是enchantment
                                    continue
                                name = ADC_API.id_to_name(priceInfo['item_id'])
                                tier = int(priceInfo['item_id'][1])
                                enchantment = 0
                                if priceInfo ['item_id'][-2] == '@':
                                    enchantment = int(priceInfo ['item_id'][-1])
                                quality = priceInfo ['quality']
                                price = int(priceInfo['buy_price_max'])
                                update_time = UTCstringToBeijing(priceInfo['buy_price_max_date'])
                                
                                
                                item_price = {
                                    'name' : name,
                                    'tier' : tier,
                                    'enchantment' : enchantment,
                                    'quality' : quality,
                                    'price' : price, 
                                    'update_time' : update_time
                                }
                                price_list.append(item_price)
                                
                            for priceInfo in price_list:
                                if priceInfo['enchantment'] == int(content[-1]) and priceInfo['tier'] == int(content[-3]) :
                                    
                                    responce_content += f'{priceInfo['name']}: {priceInfo['tier']}.{priceInfo['enchantment']} 品质:{priceInfo['quality']} 价格{priceInfo['price']:,} \n更新:{priceInfo['update_time']}\n\n'
                
                    
                #找到信息后回复该玩家
                    # if len(responce_rows) > 30 :
                    #     responce_content = '模糊查询结果超过30个，请重新使用范围更小的查询字符串,例如"禅师级背包"而不是"背包"'
                    # else :
                    #     for row in responce_rows:
                    #         update_time = date_change.timestamp_to_date(row[7])
                    #         responce_content += f'{row[6]}: 等阶/附魔:{row[2]}.{row[3]} 品质:{row[4]} 价格{row[5]:,} 最后一次更新:{update_time}\n'
                    # if responce_content == '':
                    #     responce_content = '查询结果为空，原因可能有:\n数据库暂未更新\n机器人本地化信息缺失\n查询内容有误'
                        endtime = time.time()
                        used_time = endtime - begin_time
                        responce_content+= f'本次查询所用时间:{round(used_time, 2)}秒'
                        post_msg(responce_content,msg_item['id'])
                    
        last_msg_time = msg_list[-1]['create_at']
        time.sleep(7)

if __name__ == "__main__":
    # get_server_list()
    # get_channel_list()
    run_bot()