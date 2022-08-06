# -*- coding:utf-8 -*-
""" 
Python 3.9.5
作者: Feng Xin
日期: 2022年08月03日
"""
from services.db_context import db
from nonebot.log import logger


class SifCardData(db.Model):
    __tablename__ = "sif_card_data"

    unit_number = db.Column(db.Integer(), primary_key=True)
    card_type = db.Column(db.Integer())
    eponym = db.Column(db.Integer())
    name = db.Column(db.String())
    normal_card_id = db.Column(db.Integer())
    rank_max_card_id = db.Column(db.Integer())
    normal_unit_navi_asset_id = db.Column(db.Integer())
    rank_max_unit_navi_asset_id = db.Column(db.Integer())
    rarity = db.Column(db.Integer())
    card_color = db.Column(db.Integer())
    smile_max = db.Column(db.Integer())
    pure_max = db.Column(db.Integer())
    cool_max = db.Column(db.Integer())
    center_skill_description = db.Column(db.String())
    skill_effect_type = db.Column(db.Integer())
    skill_type_name = db.Column(db.String())
    skill_lv_8_description = db.Column(db.String())
    skill_lv_max_description = db.Column(db.String())

    _idx1 = db.Index("carddata_cardId_idx1", "unit_number", unique=True)

    @classmethod
    async def add_card_data(
            cls,
            data: dict,
    ):
        """
        说明:
            添加一份卡片数据
        参数:
            :param data: 卡数据
        """
        # :param unit_number: 卡片ID
        # :param card_type: 卡片类型
        # :param eponym: 卡片称号
        # :param name: 角色名字
        # :param normal_card_id: 未觉醒卡面ID
        # :param rank_max_card_id: 觉醒卡面ID
        # :param rarity: 稀有度
        # :param card_color: 卡片颜色
        # :param smile_max: 满级红值
        # :param pure_max: 满级绿值
        # :param cool_max: 满级蓝值
        # :param center_skill_description: 主唱技能
        # :param skill_effect_type: 技能类型（数字）
        # :param skill_type_name: 技能类型
        # :param skill_lv_8_description: 8级效果
        # :param skill_lv_max_description: 满级效果

        await cls.create(
            unit_number=data['unit_number'],
            card_type=data['card_type'],
            eponym=data['eponym'],
            name=data['name'],
            normal_card_id=data['normal_card_id'],
            rank_max_card_id=data['rank_max_card_id'],
            normal_unit_navi_asset_id=data['normal_unit_navi_asset_id'],
            rank_max_unit_navi_asset_id=data['rank_max_unit_navi_asset_id'],
            rarity=data['rarity'],
            card_color=data['card_color'],
            smile_max=data['smile_max'],
            pure_max=data['pure_max'],
            cool_max=data['cool_max'],
            center_skill_description=data['center_skill_description'],
            skill_effect_type=data['skill_effect_type'],
            skill_type_name=data['skill_type_name'],
            skill_lv_8_description=data['skill_lv_8_description'],
            skill_lv_max_description=data['skill_lv_max_description'],
        )

    @classmethod
    async def ensure_card(
            cls,
            unit_number: int,
    ) -> bool:
        """
        说明:
            获取卡片对象
        参数:
            :param unit_number: 卡片ID
        """

        query = cls.query.where(cls.unit_number == unit_number)
        user = await query.gino.first()
        return user

    @classmethod
    async def max_card_id(cls) -> int:
        """
        说明:
            获取数据库卡片数量
        :return: 卡片数量
        """

        return await db.func.count(cls.unit_number).gino.scalar()

    @classmethod
    async def get_card_sql_data(
            cls,
            unit_number: int,
    ):
        """
            说明:
                获取卡片对象
            参数:
                :param unit_number: 卡片ID
            """
        query = cls.query.where((cls.unit_number == unit_number))
        data_list = await query.gino.first()
        return data_list

