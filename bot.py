import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from playwright.async_api import async_playwright

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a MEGA.nz link and I'll try to download the file.")

async def download_mega_file(mega_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(mega_url)
        await page.wait_for_selector('a.download', timeout=15000)
        download_link = await page.get_attribute('a.download', 'href')
        await browser.close()
        return download_link

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    if "mega.nz" in message:
        await update.message.reply_text("Processing your MEGA link...")
        try:
            download_url = await download_mega_file(message)
            filename = download_url.split("/")[-1]
            response = requests.get(download_url)
            with open(filename, 'wb') as f:
                f.write(response.content)
            await update.message.reply_document(open(filename, 'rb'))
            os.remove(filename)
        except Exception as e:
            await update.message.reply_text(f"Download failed: {str(e)}")
    else:
        await update.message.reply_text("Please send a valid MEGA.nz link.")

if __name__ == '__main__':
    import asyncio

    TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # This will be your Render domain

    async def main():
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        await app.bot.set_webhook(url=WEBHOOK_URL)
        await app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 8080)),
            webhook_url=WEBHOOK_URL,
        )

    asyncio.run(main())