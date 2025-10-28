import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask
from threading import Thread

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for keeping bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Instagram Reset Class
class InstagramReset:
    def __init__(self):
        self.url = 'https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/'
        self.headers = {
            'authority': 'www.instagram.com',
            'method': 'POST',
            'path': '/api/v1/web/accounts/account_recovery_send_ajax/',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'csrftoken=BbJnjd.Jnw20VyXU0qSsHLV; mid=ZpZMygABAAH0176Z6fWvYiNly3y2; ig_did=BBBA0292-07BC-49C8-ACF4-AE242AE19E97; datr=ykyWZhA9CacxerPITDOHV5AE; ig_nrcb=1; dpr=2.75; wd=393x466',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/password/reset/?source=fxcal',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; M2101K786) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'x-asbd-id': '129477',
            'x-csrftoken': 'BbJnjd.Jnw20VyXU0qSsHLV',
            'x-ig-app-id': '1217981644879628',
            'x-ig-www-claim': '0',
            'x-instagram-ajax': '1015181662',
            'x-requested-with': 'XMLHttpRequest'
        }

    def reset_account(self, email):
        try:
            data = {'email_or_username': email, 'flow': 'fxcal'}
            response = requests.post(self.url, headers=self.headers, data=data, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Initialize Instagram Reset
ig_reset = InstagramReset()

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with inline button"""
    keyboard = [[InlineKeyboardButton("🔄 RESET", callback_data='reset')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "📱 Instagram Reset Bot By Hazy • @yaplol\n\n"
        "Click RESET below to recover your account."
    )
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'reset':
        context.user_data['awaiting_input'] = True
        await query.message.reply_text(
            "✉️ Please enter your Instagram username or email:"
        )
        
    elif query.data == 'reset_again':
        keyboard = [[InlineKeyboardButton("🔄 RESET", callback_data='reset')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.user_data['awaiting_input'] = False
        
        await query.message.reply_text(
            "📱 Instagram Reset Bot By Hazy • @yaplol\n\n"
            "Click RESET below to recover your account.",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user input for reset"""
    if context.user_data.get('awaiting_input'):
        context.user_data['awaiting_input'] = False
        email = update.message.text.strip()
        
        # Show processing message
        processing_msg = await update.message.reply_text("⏳ Processing your request...")
        
        # Perform reset
        result = ig_reset.reset_account(email)
        
        # Format response
        if "error" in result:
            response = f"❌ Error occurred: {result['error']}"
            status = "failed"
        elif result.get('status') == 'ok':
            response = "✅ Password reset link sent successfully!"
            status = "success"
        else:
            response = f"⚠️ Response: {result}"
            status = "unknown"
        
        # Create reset again button
        keyboard = [[InlineKeyboardButton("🔄 RESET AGAIN", callback_data='reset_again')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.edit_text(response, reply_markup=reply_markup)

def main():
    """Start the bot"""
    # Start Flask in background thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Get bot token from environment variable
    TOKEN = "8256075803:AAE5XedVphcKSm1X_hCgpWAaHd26pARU5qc"
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    from telegram.ext import MessageHandler, filters
    main()
