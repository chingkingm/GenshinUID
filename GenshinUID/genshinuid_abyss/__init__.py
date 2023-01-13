import re

from hoshino.typing import CQEvent, HoshinoBot

from ..base import sv, logger
from .draw_abyss_card import draw_abyss_img
from ..utils.message.error_reply import UID_HINT
from ..utils.db_operation.db_operation import select_db
from ..utils.mhy_api.convert_mysid_to_uid import convert_mysid
from ..utils.draw_image_tools.send_image_tool import convert_img


@sv.on_rex(
    r'^(\[CQ:at,qq=[0-9]+\])?( )?'
    r'gs(uid|查询|mys)?([0-9]+)?(上期)?(深渊|sy)'
    r'(9|10|11|12|九|十|十一|十二)?(层)?'
    r'(\[CQ:at,qq=[0-9]+\])?( )?$',
)
async def send_abyss_info(bot: HoshinoBot, ev: CQEvent):
    args = ev['match'].groups()
    logger.info('开始执行[查询深渊信息]')
    logger.info('[查询深渊信息]参数: {}'.format(args))
    at = re.search(r'\[CQ:at,qq=(\d*)]', str(ev.message))

    if at:
        qid = int(at.group(1))
    else:
        if ev.sender:
            qid = int(ev.sender['user_id'])
        else:
            return

    # 判断uid
    if args[2] != 'mys':
        if args[3] is None:
            uid = await select_db(qid, mode='uid')
            uid = str(uid)
        elif len(args[3]) != 9:
            return
        else:
            uid = args[3]
    else:
        uid = await convert_mysid(args[3])

    logger.info('[查询深渊信息]uid: {}'.format(uid))

    if '未找到绑定的UID' in uid:
        await bot.send(ev, UID_HINT)

    # 判断深渊期数
    if args[4] is None:
        schedule_type = '1'
    else:
        schedule_type = '2'
    logger.info('[查询深渊信息]深渊期数: {}'.format(schedule_type))

    if args[6] in ['九', '十', '十一', '十二']:
        floor = (
            args[6]
            .replace('九', '9')
            .replace('十一', '11')
            .replace('十二', '12')
            .replace('十', '10')
        )
    else:
        floor = args[6]
    if floor is not None:
        floor = int(floor)
    logger.info('[查询深渊信息]深渊层数: {}'.format(floor))

    im = await draw_abyss_img(uid, floor, schedule_type)
    if isinstance(im, str):
        await bot.send(ev, im)
    elif isinstance(im, bytes):
        im = await convert_img(im)
        await bot.send(ev, im)
    else:
        await bot.send(ev, '发生了未知错误,请联系管理员检查后台输出!')
