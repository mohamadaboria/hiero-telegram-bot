from flask import Flask, request
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image, ImageDraw, ImageFont
import os
import asyncio

# إعداد Flask
app = Flask(__name__)

# إعداد البوت
TOKEN = "TOKEN"
WEBHOOK_URL = "WEEBHOOK_URL"  

arabic_to_hieroglyphs = {
    'ا': '𓄿', 'ب': '𓃀', 'ت': '𓏏', 'ث': '𓍿',
    'ج': '𓎼', 'ح': '𓉔', 'خ': '𓐍', 'د': '𓂧',
    'ذ': '𓆓', 'ر': '𓂋', 'ز': '𓊃', 'س': '𓋴',
    'ش': '𓈙', 'ص': '𓍑', 'ض': '𓂞', 'ط': '𓏠',
    'ظ': '𓅱', 'ع': '𓂝', 'غ': '𓎼', 'ف': '𓆑',
    'ق': '𓎡', 'ك': '𓎢', 'ل': '𓃭', 'م': '𓅓',
    'ن': '𓈖', 'ه': '𓎛', 'و': '𓅱', 'ي': '𓇌',
    'ء': '𓀀', 'ى': '𓇌', 'ة': '𓏏'
}

def translate_to_hieroglyphs(text):
    return ''.join(arabic_to_hieroglyphs.get(char, char) for char in text)

def create_hieroglyph_image(text, user_id):
    img = Image.new('RGB', (600, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("NotoSansEgyptianHieroglyphs-Regular.ttf", 50)
    except:
        font = ImageFont.load_default()
    draw.text((20, 70), text, font=font, fill=(0, 0, 0))
    filepath = f"{user_id}_hiero.png"
    img.save(filepath)
    return filepath

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "مرحبًا بك في بوت الهيروغليفية!"
        "أرسل اسمك بالعربية وسأحوله إلى رموز فرعونية مع صورة."
    )
    await update.message.reply_text(welcome)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    arabic_text = update.message.text
    hiero_text = translate_to_hieroglyphs(arabic_text)

    await update.message.reply_text("اسمك بالهيروغليفية:" + hiero_text)

    image_path = create_hieroglyph_image(hiero_text, uid)
    with open(image_path, 'rb') as img:
        await update.message.reply_photo(photo=InputFile(img))
    os.remove(image_path)

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("restart", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route("/")
def index():
    return "البوت يعمل على Heroku"

@app.route("/webhook", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.update_queue.put(update)
        return "OK"

if __name__ == "__main__":
    import asyncio
    asyncio.run(application.bot.set_webhook(url=WEBHOOK_URL))
    app.run(port=int(os.environ.get("PORT", 5000)))