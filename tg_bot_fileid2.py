import re
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置信息
BOT_TOKEN = "8206700130:AAEsvkT5iD0Zd0vPx-7Xc57IU_zjkTfCuts"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        "欢迎使用文件ID提取机器人！\n\n"
        "请直接发送任何Telegram消息链接，我会为您提取其中的文件ID。\n"
        "例如: https://t.me/channel_name/1234"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户发送的消息链接"""
    text = update.message.text
    
    # 验证链接格式
    if not re.match(r'https?://t\.me/(\w+)/(\d+)', text):
        await update.message.reply_text("格式错误，请使用 Telegram 标准消息链接格式：\nhttps://t.me/channel_name/message_id")
        return
    
    # 提取频道名和消息ID
    match = re.search(r'https?://t\.me/(\w+)/(\d+)', text)
    channel_username = f"@{match.group(1)}"  # 添加 @ 符号
    message_id = int(match.group(2))
    
    try:
        # 使用机器人API获取消息内容
        bot = context.bot
        message = await bot.get_message(chat_id=channel_username, message_id=message_id)
        
        # 提取文件ID
        file_id = None
        if message.document:
            file_id = message.document.file_id
        elif message.video:
            file_id = message.video.file_id
        elif message.audio:
            file_id = message.audio.file_id
        elif message.photo:
            file_id = message.photo[-1].file_id  # 取最高分辨率图片
        elif message.voice:
            file_id = message.voice.file_id
        elif message.sticker:
            file_id = message.sticker.file_id
        
        if file_id:
            await update.message.reply_text(
                f"✅ 文件 ID 提取成功：\n`{file_id}`\n\n"
                f"📤 原始链接: {text}",
                parse_mode='MarkdownV2'
            )
        else:
            await update.message.reply_text("⚠️ 该消息没有找到文件附件")
            
    except Exception as e:
        error_msg = (
            f"❌ 提取文件ID失败: {str(e)}\n\n"
            "可能原因：\n"
            "1. 机器人未加入该频道或群组\n"
            "2. 没有查看消息的权限\n"
            "3. 消息ID不正确"
        )
        await update.message.reply_text(error_msg)

def main():
    """启动机器人"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    
    # 添加消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 启动机器人
    print("🤖 机器人已启动，等待接收消息...")
    application.run_polling()
    

if __name__ == "__main__":
    main()
