from nonebot import on_command, on_message, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, MessageEvent
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.log import logger

from src.utils import get_config, get_logger as setup_logger, permission, require_master, require_admin
from src.services.chat import chat_service
from src.services.news import news_service
from src.services.push import push_service
from src.services.game.keyword import keyword_manager
from src.services.game.data import game_data
from src.storage import db
from src.memory import memory, init_vector_store

setup_logger()
driver = get_driver()


@driver.on_startup
async def startup():
    await db.init()
    await init_vector_store()
    chat_service.llm = None
    logger.info("ZZZAI Bot started")


@driver.on_bot_connect
async def bot_connect(bot: Bot):
    push_service.set_bot(bot)
    push_service.start()


@driver.on_shutdown
async def shutdown():
    push_service.stop()
    await db.close()
    logger.info("ZZZAI Bot stopped")


help_cmd = on_command("帮助", aliases={"help", "菜单"}, priority=10, block=True)

@help_cmd.handle()
async def handle_help(event: MessageEvent):
    user_id = event.get_user_id()
    is_master_user = permission.is_master(user_id)
    is_admin_user = permission.is_admin(user_id)
    
    help_text = """【绝区零机器人 - 帮助菜单】

📋 基础命令：
  #帮助 - 显示帮助菜单
  #资讯 - 查看最新资讯
  #公告 - 查看官方公告
  #活动 - 查看当前活动
  #热点 - 查看热门话题

🎮 游戏查询：
  #角色 [名称] - 查看角色信息
  #材料 [名称] - 查看材料信息
  #图鉴 [关键词] - 综合查询

💬 对话功能：
  @机器人 + 消息 - 与爱芮对话
  私聊机器人 - 直接对话
"""
    
    if is_admin_user:
        help_text += """
⚙️ 管理员命令：
  #刷新资讯 - 手动刷新资讯
  #推送资讯 - 手动推送资讯
"""
    
    if is_master_user:
        help_text += """
🔐 主人命令：
  #设置主人 @用户 - 添加主人
  #删除主人 @用户 - 移除主人
  #设置管理员 @用户 - 添加管理员
  #删除管理员 @用户 - 移除管理员
  #拉黑 @用户 - 添加黑名单
  #解除拉黑 @用户 - 移除黑名单
  #推送设置 [早间/晚间] [开/关] - 设置推送
  #推送目标 [早间/晚间] [群号/用户号] - 设置推送目标
  #权限列表 - 查看权限列表
  #添加关键词 [关键词] [回复] - 添加自动回复
  #删除关键词 [关键词] - 删除自动回复
  #关键词列表 - 查看关键词列表
"""
    
    help_text += """
📝 提示：
  命令前缀支持: # / %
"""
    await help_cmd.finish(help_text)


news_cmd = on_command("资讯", priority=10, block=True)

@news_cmd.handle()
async def handle_news(event: MessageEvent):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    news_list = await news_service.fetch_latest_news(24)
    if news_list:
        message = news_service.format_news_for_push(news_list[:5], "最新资讯")
        await news_cmd.finish(message)
    else:
        await news_cmd.finish("暂无资讯，请稍后再试~")


notice_cmd = on_command("公告", priority=10, block=True)

@notice_cmd.handle()
async def handle_notice(event: MessageEvent):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    news_list = await news_service.get_news_by_type("公告")
    if news_list:
        message = news_service.format_news_for_push(news_list[:5], "官方公告")
        await notice_cmd.finish(message)
    else:
        await notice_cmd.finish("暂无公告~")


activity_cmd = on_command("活动", priority=10, block=True)

@activity_cmd.handle()
async def handle_activity(event: MessageEvent):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    news_list = await news_service.get_news_by_type("活动")
    if news_list:
        message = news_service.format_news_for_push(news_list[:5], "当前活动")
        await activity_cmd.finish(message)
    else:
        await activity_cmd.finish("暂无活动~")


hot_cmd = on_command("热点", aliases={"热门", "hot"}, priority=10, block=True)

@hot_cmd.handle()
async def handle_hot(event: MessageEvent):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    hot_list = await news_service.fetch_hot_topics()
    if hot_list:
        message = news_service.format_hot_topics(hot_list, "绝区零热点")
        await hot_cmd.finish(message)
    else:
        await hot_cmd.finish("暂无热点话题，请稍后再试~")


char_cmd = on_command("角色", priority=10, block=True)

@char_cmd.handle()
async def handle_character(event: MessageEvent, args = CommandArg()):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    name = args.extract_plain_text().strip()
    
    if not name:
        chars = await game_data.list_characters()
        message = game_data.get_character_list_message(chars[:15])
        await char_cmd.finish(message)
    
    char = await game_data.search_character(name)
    if char:
        await char_cmd.finish(char.to_message())
    else:
        await char_cmd.finish(f"未找到角色「{name}」，请检查名称是否正确")


material_cmd = on_command("材料", priority=10, block=True)

@material_cmd.handle()
async def handle_material(event: MessageEvent, args = CommandArg()):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    name = args.extract_plain_text().strip()
    
    if not name:
        mats = await game_data.list_materials()
        message = game_data.get_material_list_message(mats)
        await material_cmd.finish(message)
    
    mat = await game_data.search_material(name)
    if mat:
        await material_cmd.finish(mat.to_message())
    else:
        await material_cmd.finish(f"未找到材料「{name}」，请检查名称是否正确")


wiki_cmd = on_command("图鉴", aliases={"百科"}, priority=10, block=True)

@wiki_cmd.handle()
async def handle_wiki(event: MessageEvent, args = CommandArg()):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    query = args.extract_plain_text().strip()
    
    if not query:
        await wiki_cmd.finish("""【绝区零图鉴】

🔍 使用方法：
  #图鉴 角色名 - 查看角色详情
  #图鉴 材料名 - 查看材料信息

📋 快速查询：
  #角色 - 查看角色列表
  #材料 - 查看材料列表""")
    
    char = await game_data.search_character(query)
    if char:
        await wiki_cmd.finish(char.to_message())
    
    mat = await game_data.search_material(query)
    if mat:
        await wiki_cmd.finish(mat.to_message())
    
    await wiki_cmd.finish(f"未找到「{query}」相关信息，请尝试其他关键词")


refresh_news_cmd = on_command("刷新资讯", priority=10, block=True)

@refresh_news_cmd.handle()
async def handle_refresh_news(event: MessageEvent):
    if not permission.is_admin(event.get_user_id()):
        await refresh_news_cmd.finish("权限不足，此命令仅管理员可用")
    
    news_list = await news_service.fetch_latest_news(24)
    await news_service.save_news(news_list)
    await refresh_news_cmd.finish(f"已刷新 {len(news_list)} 条资讯")


push_news_cmd = on_command("推送资讯", priority=10, block=True)

@push_news_cmd.handle()
async def handle_push_news(event: MessageEvent):
    if not permission.is_admin(event.get_user_id()):
        await push_news_cmd.finish("权限不足，此命令仅管理员可用")
    
    unpushed = await news_service.get_unpushed_news()
    if unpushed:
        message = news_service.format_news_for_push(unpushed[:10], "资讯推送")
        await push_news_cmd.finish(message)
        await news_service.mark_pushed([n.id for n in unpushed[:10]])
    else:
        await push_news_cmd.finish("暂无未推送的资讯")


set_master_cmd = on_command("设置主人", priority=10, block=True)

@set_master_cmd.handle()
async def handle_set_master(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await set_master_cmd.finish("权限不足，此命令仅主人可用")
    
    if isinstance(event, GroupMessageEvent):
        mentions = [seg.data.get("qq") for seg in event.message if seg.type == "at"]
        if mentions:
            new_master = str(mentions[0])
            if permission.add_master(new_master):
                await set_master_cmd.finish(f"已添加主人: {new_master}")
            else:
                await set_master_cmd.finish("该用户已是主人")
        else:
            await set_master_cmd.finish("请 @ 要设置为新主人的用户")
    else:
        await set_master_cmd.finish("此命令仅群聊可用")


remove_master_cmd = on_command("删除主人", priority=10, block=True)

@remove_master_cmd.handle()
async def handle_remove_master(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await remove_master_cmd.finish("权限不足，此命令仅主人可用")
    
    if isinstance(event, GroupMessageEvent):
        mentions = [seg.data.get("qq") for seg in event.message if seg.type == "at"]
        if mentions:
            target = str(mentions[0])
            if permission.remove_master(target):
                await remove_master_cmd.finish(f"已移除主人: {target}")
            else:
                await remove_master_cmd.finish("该用户不是主人")
        else:
            await remove_master_cmd.finish("请 @ 要移除主人的用户")
    else:
        await remove_master_cmd.finish("此命令仅群聊可用")


set_admin_cmd = on_command("设置管理员", priority=10, block=True)

@set_admin_cmd.handle()
async def handle_set_admin(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await set_admin_cmd.finish("权限不足，此命令仅主人可用")
    
    if isinstance(event, GroupMessageEvent):
        mentions = [seg.data.get("qq") for seg in event.message if seg.type == "at"]
        if mentions:
            new_admin = str(mentions[0])
            if permission.add_admin(new_admin):
                await set_admin_cmd.finish(f"已添加管理员: {new_admin}")
            else:
                await set_admin_cmd.finish("该用户已是管理员")
        else:
            await set_admin_cmd.finish("请 @ 要设置为管理员的用户")
    else:
        await set_admin_cmd.finish("此命令仅群聊可用")


remove_admin_cmd = on_command("删除管理员", priority=10, block=True)

@remove_admin_cmd.handle()
async def handle_remove_admin(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await remove_admin_cmd.finish("权限不足，此命令仅主人可用")
    
    if isinstance(event, GroupMessageEvent):
        mentions = [seg.data.get("qq") for seg in event.message if seg.type == "at"]
        if mentions:
            target = str(mentions[0])
            if permission.remove_admin(target):
                await remove_admin_cmd.finish(f"已移除管理员: {target}")
            else:
                await remove_admin_cmd.finish("该用户不是管理员")
        else:
            await remove_admin_cmd.finish("请 @ 要移除管理员的用户")
    else:
        await remove_admin_cmd.finish("此命令仅群聊可用")


blacklist_cmd = on_command("拉黑", priority=10, block=True)

@blacklist_cmd.handle()
async def handle_blacklist(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await blacklist_cmd.finish("权限不足，此命令仅主人可用")
    
    if isinstance(event, GroupMessageEvent):
        mentions = [seg.data.get("qq") for seg in event.message if seg.type == "at"]
        if mentions:
            target = str(mentions[0])
            if permission.add_to_blacklist(target):
                await blacklist_cmd.finish(f"已拉黑用户: {target}")
            else:
                await blacklist_cmd.finish("该用户已在黑名单中")
        else:
            await blacklist_cmd.finish("请 @ 要拉黑的用户")
    else:
        await blacklist_cmd.finish("此命令仅群聊可用")


unblacklist_cmd = on_command("解除拉黑", priority=10, block=True)

@unblacklist_cmd.handle()
async def handle_unblacklist(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await unblacklist_cmd.finish("权限不足，此命令仅主人可用")
    
    if isinstance(event, GroupMessageEvent):
        mentions = [seg.data.get("qq") for seg in event.message if seg.type == "at"]
        if mentions:
            target = str(mentions[0])
            if permission.remove_from_blacklist(target):
                await unblacklist_cmd.finish(f"已解除拉黑: {target}")
            else:
                await unblacklist_cmd.finish("该用户不在黑名单中")
        else:
            await unblacklist_cmd.finish("请 @ 要解除拉黑的用户")
    else:
        await unblacklist_cmd.finish("此命令仅群聊可用")


permission_list_cmd = on_command("权限列表", priority=10, block=True)

@permission_list_cmd.handle()
async def handle_permission_list(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await permission_list_cmd.finish("权限不足，此命令仅主人可用")
    
    masters = permission.get_masters()
    admins = permission.get_admins()
    
    text = "【权限列表】\n\n"
    text += f"🔐 主人 ({len(masters)}):\n"
    for m in masters:
        text += f"  - {m}\n"
    
    text += f"\n⚙️ 管理员 ({len(admins)}):\n"
    for a in admins:
        text += f"  - {a}\n"
    
    await permission_list_cmd.finish(text)


push_setting_cmd = on_command("推送设置", priority=10, block=True)

@push_setting_cmd.handle()
async def handle_push_setting(event: MessageEvent, args = CommandArg()):
    if not permission.is_master(event.get_user_id()):
        await push_setting_cmd.finish("权限不足，此命令仅主人可用")
    
    arg_text = args.extract_plain_text().strip().split()
    
    if len(arg_text) < 2:
        await push_setting_cmd.finish("用法: #推送设置 [早间/晚间] [开/关]")
    
    push_type, action = arg_text[0], arg_text[1]
    
    if push_type not in ["早间", "晚间"]:
        await push_setting_cmd.finish("类型必须是 早间 或 晚间")
    
    if action not in ["开", "关"]:
        await push_setting_cmd.finish("操作必须是 开 或 关")
    
    enabled = action == "开"
    
    if push_type == "早间":
        push_service.morning_enabled = enabled
        await push_setting_cmd.finish(f"早间推送已{'开启' if enabled else '关闭'}")
    else:
        push_service.evening_enabled = enabled
        await push_setting_cmd.finish(f"晚间推送已{'开启' if enabled else '关闭'}")


push_target_cmd = on_command("推送目标", priority=10, block=True)

@push_target_cmd.handle()
async def handle_push_target(event: MessageEvent, args = CommandArg()):
    if not permission.is_master(event.get_user_id()):
        await push_target_cmd.finish("权限不足，此命令仅主人可用")
    
    arg_text = args.extract_plain_text().strip().split()
    
    if len(arg_text) < 2:
        await push_target_cmd.finish("用法: #推送目标 [早间/晚间] [群号/用户号]")
    
    push_type, target = arg_text[0], arg_text[1]
    
    if push_type not in ["早间", "晚间"]:
        await push_target_cmd.finish("类型必须是 早间 或 晚间")
    
    if target.startswith("群"):
        target_id = target.replace("群", "")
        target_str = f"group_{target_id}"
    else:
        target_str = f"user_{target}"
    
    if push_type == "早间":
        if target_str not in push_service.morning_targets:
            push_service.morning_targets.append(target_str)
            await push_target_cmd.finish(f"已添加早间推送目标: {target}")
        else:
            push_service.morning_targets.remove(target_str)
            await push_target_cmd.finish(f"已移除早间推送目标: {target}")
    else:
        if target_str not in push_service.evening_targets:
            push_service.evening_targets.append(target_str)
            await push_target_cmd.finish(f"已添加晚间推送目标: {target}")
        else:
            push_service.evening_targets.remove(target_str)
            await push_target_cmd.finish(f"已移除晚间推送目标: {target}")


add_keyword_cmd = on_command("添加关键词", priority=10, block=True)

@add_keyword_cmd.handle()
async def handle_add_keyword(event: MessageEvent, args = CommandArg()):
    if not permission.is_master(event.get_user_id()):
        await add_keyword_cmd.finish("权限不足，此命令仅主人可用")
    
    arg_text = args.extract_plain_text().strip()
    parts = arg_text.split(maxsplit=1)
    
    if len(parts) < 2:
        await add_keyword_cmd.finish("用法: #添加关键词 [关键词] [回复内容]")
    
    word, reply = parts[0], parts[1]
    
    if keyword_manager.add_rule(word, reply):
        await add_keyword_cmd.finish(f"已添加关键词: {word}")
    else:
        await add_keyword_cmd.finish("该关键词已存在")


remove_keyword_cmd = on_command("删除关键词", priority=10, block=True)

@remove_keyword_cmd.handle()
async def handle_remove_keyword(event: MessageEvent, args = CommandArg()):
    if not permission.is_master(event.get_user_id()):
        await remove_keyword_cmd.finish("权限不足，此命令仅主人可用")
    
    word = args.extract_plain_text().strip()
    
    if not word:
        await remove_keyword_cmd.finish("用法: #删除关键词 [关键词]")
    
    if keyword_manager.remove_rule(word):
        await remove_keyword_cmd.finish(f"已删除关键词: {word}")
    else:
        await remove_keyword_cmd.finish("该关键词不存在")


keyword_list_cmd = on_command("关键词列表", priority=10, block=True)

@keyword_list_cmd.handle()
async def handle_keyword_list(event: MessageEvent):
    if not permission.is_master(event.get_user_id()):
        await keyword_list_cmd.finish("权限不足，此命令仅主人可用")
    
    rules = keyword_manager.get_rules()
    
    if not rules:
        await keyword_list_cmd.finish("暂无关键词规则")
    
    text = "【关键词列表】\n\n"
    for i, rule in enumerate(rules, 1):
        text += f"{i}. {rule['word']}\n"
        text += f"   回复: {rule['reply'][:30]}...\n\n"
    
    await keyword_list_cmd.finish(text)


keyword_matcher = on_message(priority=15, block=False)

@keyword_matcher.handle()
async def handle_keyword(event: MessageEvent):
    if permission.is_blacklisted(event.get_user_id()):
        return
    
    text = event.get_plaintext().strip()
    if not text:
        return
    
    reply = keyword_manager.match(text)
    if reply:
        await keyword_matcher.finish(reply)


chat_matcher = on_message(rule=to_me(), priority=20, block=True)

@chat_matcher.handle()
async def handle_chat(event: MessageEvent):
    user_id = event.get_user_id()
    
    if permission.is_blacklisted(user_id):
        return
    
    if isinstance(event, GroupMessageEvent):
        group_id = str(event.group_id)
        session_id = memory.create_session_id(user_id, group_id)
    else:
        session_id = memory.create_session_id(user_id)
    
    user_input = event.get_plaintext().strip()
    if not user_input:
        await chat_matcher.finish("你好呀~有什么想和我聊的吗？")
    
    try:
        reply = await chat_service.chat(session_id, user_input, user_id)
        if not reply or not reply.strip():
            reply = "嗯...我好像不知道该说什么了~"
        await chat_matcher.finish(reply)
    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"Chat handler error: {e}", exc_info=True)
        await chat_matcher.finish("抱歉，我遇到了一些问题，稍后再聊吧~")
