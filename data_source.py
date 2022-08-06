import math
import json
from utils.http_utils import AsyncHttpx
import jinja2
from configs.path_config import DATA_PATH
from typing import List, Union
from nonebot.log import logger
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_htmlrender import html_to_pic
from configs.config import Config
import os
from .model import SifCardData
from nonebot.adapters.onebot.v11 import Bot
from configs.config import NICKNAME

data_path = DATA_PATH / "sifFindCard"
card_data_path = data_path / "card_data"
pic_card_path = data_path / "piccard"
pic_navi_path = data_path / "picnavi"


async def down_card_data(card_id):
    card_url = "https://card.llsif.moe/cardApi/" + str(card_id)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }
    try:
        res = await AsyncHttpx.get(card_url, headers=headers, timeout=10)
        if res.status_code == 404:
            return {}, 404
        res_json = res.json()
        data = await down_card_data_json(res_json)
        return data, 200
    except Exception as e:
        logger.error(f"访问接口错误 {type(e)}：{e}")
    return None, 404


def num_to_type(num):
    numbers = {
        1: "通常卡",
        2: "活动卡",
        3: "特典卡",
        4: "练习用卡",
        5: "box卡"
    }

    return numbers.get(num)


def num_to_rarity(num):
    numbers = {
        1: "N",
        2: "R",
        3: "SR",
        4: "UR",
        5: "SSR"
    }

    return numbers.get(num)


def num_to_color(num):
    numbers = {
        1: "红",
        2: "绿",
        3: "蓝",
    }

    return numbers.get(num)


def num_to_skill_effect_type(num):
    numbers = {
        0: "支援卡",
        4: "小判",
        5: "大判",
        9: "奶卡",
        11: "分卡",
        2000: "概率",
        2100: "复读",
        2201: "PP",
        2300: "CF",
        2400: "属性同步",
        2500: "LV",
        2600: "属性UP"
    }

    return numbers.get(num)


async def get_data_json(num: int):
    try:
        fn = str(num) + '.json'
        fn = card_data_path / fn
        with open(fn, 'r+', encoding='utf-8') as f:
            file = f.read()
        return json.loads(file), 200  # bug
    except FileNotFoundError:
        card_data, code = await down_card_data(num)
        return card_data, code
        # fn = 'data/' + str(num) + '.json'
        # with open(fn, 'r+', encoding='utf-8') as f:
        #     file = f.read()
        # down_card_data_json(json.loads(file))


def read_card_data_json(json_data: dict):
    data = {"unit_number": json_data['unit_number'],
            "card_type": num_to_type(json_data['card_type']),
            "eponym": json_data['eponym'],
            "name": json_data['name'],
            "normal_card_id": json_data['normal_card_id'],
            "rank_max_card_id": json_data['rank_max_card_id'],
            "normal_unit_navi_asset_id": json_data['normal_unit_navi_asset_id'],
            "rank_max_unit_navi_asset_id": json_data['rank_max_unit_navi_asset_id'],
            "rarity": num_to_rarity(json_data['rarity']),
            "card_color": num_to_color(json_data['card_color']),
            "smile_max": json_data['smile_max'],
            'pure_max': json_data['pure_max'],
            'cool_max': json_data['cool_max'],
            "center_skill_description": json_data['center_skill_description'],
            "skill_effect_type": num_to_skill_effect_type(json_data['skill_effect_type']),
            "skill_type_name": json_data['skill_type_name'],
            "skill_lv_8_description": json_data['skill_lv_8_description'],
            "skill_lv_max_description": json_data['skill_lv_max_description']}
    a = str(json_data['rank_max_unit_navi_asset_id']) + '.png'
    rank_max_unit_navi_asset_id_url = pic_navi_path / a
    b = str(json_data['rank_max_card_id']) + '.png'
    rank_max_card_id_url = pic_card_path / b
    msg = "卡序号：{}\n卡名字：{} {}\n{}{}{} {}/{}/{}\n主唱技能：{}\n技能类型：{}\n8级效果：{}\n满级效果：{}".format(
        # rank_max_unit_navi_asset_id_url,
        # rank_max_card_id_url,
        data["unit_number"],
        data["eponym"],
        data["name"],
        data["card_color"],
        data["rarity"],
        data["card_type"],
        data["smile_max"],
        data["pure_max"],
        data["cool_max"],
        data["center_skill_description"],
        data["skill_type_name"],
        data["skill_lv_8_description"],
        data["skill_lv_max_description"],
    )
    return msg


async def down_card_data_json(json_data: dict):
    data = {"unit_number": json_data['unit']['unit_number'],
            "card_type": json_data['card_type'],
            "eponym": json_data['unit']['eponym'],
            "name": json_data['unit']['name'],
            "normal_card_id": json_data['unit']['normal_card_id'],
            "rank_max_card_id": json_data['unit']['rank_max_card_id'],
            "normal_unit_navi_asset_id": json_data['unit']['normal_unit_navi_asset_id'],
            "rank_max_unit_navi_asset_id": json_data['unit']['rank_max_unit_navi_asset_id'],
            "rarity": json_data['unit']['rarity'],
            "card_color": json_data['unit']['attribute_id'],
            "smile_max": json_data['unit']['smile_max'],
            'pure_max': json_data['unit']['pure_max'],
            'cool_max': json_data['unit']['cool_max'],
            "center_skill_description":
                ((json_data['center_skill']['description'])
                 if (json_data['center_skill'] is not None)
                 else '') + (
                    (json_data['center_skill_extra']['description'])
                    if ('center_skill_extra' in json_data and json_data['center_skill_extra'] is not None)
                    else ''),
            "skill_effect_type":
                ((json_data['skill']['skill_effect_type'])
                 if (json_data['skill'] is not None)
                 else ''),
            "skill_type_name":
                (json_data['skill']['type_name']
                 if (json_data['skill'] is not None)
                 else ''),
            "skill_lv_8_description":
                ((json_data['skill_level'][7]['description'])
                 if (json_data['skill'] is not None and len(json_data['skill_level']) > 7)
                 else ''),
            "skill_lv_max_description":
                ((json_data['skill_level'][-1]['description'])
                 if (json_data['skill'] is not None)
                 else '')
            }
    await SifCardData.add_card_data(data)
    # fn = str(data["unit_number"]) + '.json'
    # File_Name = card_data_path / fn
    # with open(File_Name, 'wb') as f:
    #     f.write(json.dumps(data).encode())
    #     f.close()
    # print(fn + " Download Complete")
    return data


async def down_pic(json_data: dict):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36",
    }
    a = str(json_data['normal_card_id']) + '.png'
    b = str(json_data['rank_max_card_id']) + '.png'
    c = str(json_data['normal_unit_navi_asset_id']) + '.png'
    d = str(json_data['rank_max_unit_navi_asset_id']) + '.png'
    normal_card_id_url = "https://card.llsif.moe/card/v4/" + str(json_data["rank_max_card_id"]) + ".png"
    normal_card_id_temp = pic_card_path / a
    rank_max_card_id_url = "https://card.llsif.moe/card/v4/" + str(json_data["rank_max_card_id"]) + ".png"
    rank_max_card_id_temp = pic_card_path / b
    normal_unit_navi_asset_id_url = "https://card.llsif.moe/icon/" + str(
        json_data["rank_max_unit_navi_asset_id"]) + ".png"
    rank_max_unit_navi_asset_id_url = "https://card.llsif.moe/icon/" + str(
        json_data["rank_max_unit_navi_asset_id"]) + ".png"
    normal_unit_navi_asset_id_temp = pic_navi_path / c
    rank_max_unit_navi_asset_id_temp = pic_navi_path / d
    try:
        await AsyncHttpx.download_file(normal_card_id_url, normal_card_id_temp, headers=headers, stream=True)
        await AsyncHttpx.download_file(rank_max_card_id_url, rank_max_card_id_temp, headers=headers, stream=True)
        await AsyncHttpx.download_file(normal_unit_navi_asset_id_url, rank_max_unit_navi_asset_id_url, headers=headers,
                                       stream=True)
        await AsyncHttpx.download_file(normal_unit_navi_asset_id_temp, rank_max_unit_navi_asset_id_temp,
                                       headers=headers, stream=True)

    except Exception as e:
        logger.error(f"访问接口错误 {type(e)}：{e}")


async def get_reply(card_id: str) -> Union[str, bytes]:
    if card_id.isdigit():
        card_id = int(card_id)
    else:
        return "请输入正确的id"

    card_json, code = await get_data_json(card_id)
    if "unit_number" in card_json:
        # try:
        #     a = str(card_json['normal_unit_navi_asset_id']) + '.png'
        #     normal_unit_navi_asset_id_temp = pic_navi_path / a
        #     with open(normal_unit_navi_asset_id_temp, 'r+', encoding='utf-8') as f:
        #         f.close()
        #         return read_card_data_json(card_json)
        # except FileNotFoundError:
        #     await down_pic(card_json)

        return read_card_data_json(card_json)
    else:
        return "未获取到卡片信息"


def list_to_dict(data_list):
    data = {"unit_number": data_list.unit_number,
            "card_type": data_list.card_type,
            "eponym": data_list.eponym,
            "name": data_list.name,
            "normal_card_id": data_list.normal_card_id,
            "rank_max_card_id": data_list.rank_max_card_id,
            "normal_unit_navi_asset_id": data_list.normal_unit_navi_asset_id,
            "rank_max_unit_navi_asset_id": data_list.rank_max_unit_navi_asset_id,
            "rarity": data_list.rarity,
            "card_color": data_list.card_color,
            "smile_max": data_list.smile_max,
            'pure_max': data_list.pure_max,
            'cool_max': data_list.cool_max,
            "center_skill_description": data_list.center_skill_description,
            "skill_effect_type": data_list.skill_effect_type,
            "skill_type_name": data_list.skill_type_name,
            "skill_lv_8_description": data_list.skill_lv_8_description,
            "skill_lv_max_description": data_list.skill_lv_max_description}
    return data


async def get_reply_A(card_id: str) -> Union[str, bytes]:
    if card_id.isdigit():
        card_id = int(card_id)
    else:
        return "请输入正确的id"

    list = await SifCardData.get_card_sql_data(unit_number=card_id)
    if list:
        card_json = list_to_dict(list)
        return read_card_data_json(card_json)
    else:
        return await get_reply(str(card_id))


async def get_reply_B(bot: Bot, card_id: str):
    max_id = 3567  # await SifCardData.max_card_id()
    code = 200
    msg_list = []
    if card_id.isdigit():
        card_id = int(card_id)
    else:
        return "请输入正确的id"
    for i in range(0, 10):
        card_id += 1
        card_json, code = await get_data_json(str(card_id))
        if code == 404:
            break
        _message = read_card_data_json(card_json)
        data = {
            "type": "node",
            "data": {
                "name": f"{NICKNAME}",
                "uin": f"{bot.self_id}",
                "content": _message,
            },
        }
        msg_list.append(data)

    return msg_list


async def update_card(bot: Bot):
    card_id = await SifCardData.max_card_id()
    msg_list = []
    for i in range(0, 10):
        card_id += 1
        card_json, code = await get_data_json(str(card_id))
        if code == 404:
            break
        _message = read_card_data_json(card_json)
        data = {
            "type": "node",
            "data": {
                "name": f"{NICKNAME}",
                "uin": f"{bot.self_id}",
                "content": _message,
            },
        }
        msg_list.append(data)
    if i < 9:
        _message = "没有更多数据了！当前更新到卡ID:{}".format(str(card_id - 1))
        data = {
            "type": "node",
            "data": {
                "name": f"{NICKNAME}",
                "uin": f"{bot.self_id}",
                "content": _message,
            },
        }
        msg_list.append(data)

    return msg_list
