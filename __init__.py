import traceback
from loguru import logger
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, GroupMessageEvent
from nonebot.log import logger
from utils.utils import scheduler, get_bot
from configs.path_config import DATA_PATH
from .data_source import get_reply, get_reply_A, update_card, get_reply_B

__zx_plugin_name__ = "SIF查卡简易版"
__plugin_usage__ = """
usage：
/sif {卡片ID} 查询该卡数据
/siff {卡片ID} 查询该卡后面最多十张卡的数据（不包括该卡）
/sif 更新 向后更新十张卡的数据
示例：/sif 1314
""".strip()
__plugin_des__ = "SIF查卡简易版"
__plugin_type__ = ("一些工具",)
__plugin_version__ = 0.1
__plugin_cmd__ = ["/sif {卡片ID}", "/siff {卡片ID}", "/sif 更新"]
__plugin_author__ = "FengXin"

__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["/sif {卡片ID}", "/siff {卡片ID}", "/sif 更新"],
}
sifFC_A = on_command("/sif", block=True, priority=1)
sifFC_B = on_command("/siff", block=True, priority=1)
sifFC = on_command("/sifff", block=True, priority=1)
sifFC_C = on_command("/sif 更新", block=True, priority=1)


@sifFC.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    if not text:
        await sifFC.finish()

    try:
        res = await get_reply(text)
    except:
        logger.warning(traceback.format_exc())
        await sifFC.finish("出错了，请稍后再试")

    await sifFC.finish(res)


@sifFC_A.handle()
async def _(msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    if not text:
        await sifFC.finish()

    try:
        res = await get_reply_A(text)
    except:
        logger.warning(traceback.format_exc())
        await sifFC.finish("出错了，请稍后再试")

    if isinstance(res, str or dict):
        await sifFC.finish(res)
    # else:
    #     await sifFC.finish(MessageSegment.image(res))


@sifFC_B.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    text = msg.extract_plain_text().strip()
    bot = get_bot()
    msg_list = await get_reply_B(bot, text)
    if isinstance(event, GroupMessageEvent):
        if msg_list is not None:
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
    else:
        for msg in msg_list:
            await bot.send_private_msg(user_id=event.user_id, message=msg)


@sifFC_C.handle()
async def _(event: MessageEvent):
    bot = get_bot()
    msg_list = await update_card(bot)
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_list)
    else:
        for msg in msg_list:
            await bot.send_private_msg(user_id=event.user_id, message=msg)
