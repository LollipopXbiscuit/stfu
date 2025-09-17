import random
import re
import os
from telegram import Update, BotCommand, InlineQueryResultPhoto
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    InlineQueryHandler,
    filters,
)

message_count = {}  # Tracks messages per chat

# Extract owner ID from environment variable (handle extra text)
owner_id_str = os.environ.get("OWNER_ID", "0")
owner_id_match = re.search(r'\d+', owner_id_str)
OWNER_ID = int(owner_id_match.group()) if owner_id_match else 0

# --- Global Variables ---
rarities = {
    "Common": 0.8,
    "Uncommon": 0.7,
    "Rare": 0.6,
    "Epic": 0.6,
    "Legendary": 0.6,
    "Mythic": 0.5,
    "Celestial": 0.1,
    "Arcane": 0.00005,
    "Limited Edition": 0
}

rarity_styles = {
    "Common": "⚪️",
    "Uncommon": "🟢",
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡",
    "Mythic": "🟥",
    "Celestial": "🌌",
    "Arcane": "🔥",
    "Limited Edition": "💎"
}

# Example characters (you can replace with your real image URLs later)
characters = {
    "Common": [
        {"name": "Azure Knight", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Forest Guardian", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Uncommon": [
        {"name": "Storm Mage", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Shadow Warrior", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Rare": [
        {"name": "Crystal Sage", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Fire Empress", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Epic": [
        {"name": "Dragon Lord", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Ice Queen", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Legendary": [
        {"name": "Phoenix Master", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Void Keeper", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Mythic": [
        {"name": "Celestial Dragon", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Eternal Guardian", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Celestial": [
        {"name": "Star Weaver", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Cosmic Entity", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ],
    "Arcane": [
        {"name": "Reality Bender", "url": "https://telegra.ph/file/b925c3985f0f325e62e17.jpg"},
        {"name": "Time Weaver", "url": "https://telegra.ph/file/4211fb191383d895dab9d.jpg"}
    ]
}

# Track last summoned characters per user (temporary storage)
last_summons = {}
user_collections = {}
favorites = {}

# --- Bot Functions ---
async def start(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text(
            "✨ Welcome to the waifu collector Bot!\n\n"
            "Commands:\n"
            "/summon - Summon a random character\n"
            "/marry - Marry your last summoned character\n"
            "/collection - View your collection\n"
            "/fav - View your favorite character\n"
            "/setfav - Set your last summoned character as favorite"
        )

def choose_rarity():
    return random.choices(
        population=list(rarities.keys()),
        weights=list(rarities.values()),
        k=1
    )[0]

async def summon(update: Update, context: CallbackContext):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id

    if user_id != OWNER_ID:
        await update.message.reply_text(
            f"🚫 Only the bot owner can manually summon characters!\n"
            f"Your ID: {user_id}, Owner ID: {OWNER_ID}"
        )
        return

    rarity = choose_rarity()

    if rarity in characters and characters[rarity]:
        character = random.choice(characters[rarity])
        style = rarity_styles.get(rarity, "")
        caption = f"{style} A beauty has been summoned! Use /marry to add them to your harem!"

        last_summons[user_id] = {
            "name": character["name"],
            "rarity": rarity,
            "url": character["url"],
            "style": style
        }

        await update.message.reply_photo(character["url"], caption=caption)
    else:
        await update.message.reply_text("⚠️ No characters found for this rarity yet.")

async def marry(update: Update, context: CallbackContext):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if chat_id in last_summons:
        summon_info = last_summons[chat_id]
        if user_id not in user_collections:
            user_collections[user_id] = []
        user_collections[user_id].append(summon_info)
        del last_summons[chat_id]
        await update.message.reply_text(
            f"✅ You married {summon_info['style']} {summon_info['name']} ({summon_info['rarity']})!\n\n"
            f"Total characters in your collection: {len(user_collections[user_id])}"
        )
    else:
        await update.message.reply_text("❌ No summon available right now.")

async def collection(update: Update, context: CallbackContext):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    if user_id not in user_collections or not user_collections[user_id]:
        await update.message.reply_text("📦 Your collection is empty! Use /summon to find characters.")
        return

    collection_text = "🎴 Your Collection:\n\n"
    rarity_counts = {}
    for char in user_collections[user_id]:
        rarity = char['rarity']
        rarity_counts.setdefault(rarity, []).append(char['name'])

    rarity_order = ["Limited Edition", "Arcane", "Celestial", "Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]
    for rarity in rarity_order:
        if rarity in rarity_counts:
            style = rarity_styles.get(rarity, "")
            collection_text += f"{style} {rarity} ({len(rarity_counts[rarity])}):\n"
            for name in rarity_counts[rarity]:
                collection_text += f"  • {name}\n"
            collection_text += "\n"

    collection_text += f"📊 Total: {len(user_collections[user_id])} characters"
    await update.message.reply_text(collection_text)

async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_count[chat_id] = message_count.get(chat_id, 0) + 1
    if message_count[chat_id] >= 100:
        message_count[chat_id] = 0
        await summon(update, context)

async def fav(update: Update, context: CallbackContext):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    if user_id in favorites:
        fav_character = favorites[user_id]
        await update.message.reply_text(f"💖 Your favorite is {fav_character['name']} ({fav_character['rarity']})!")
        await update.message.reply_photo(fav_character['url'])
    else:
        await update.message.reply_text("You don't have a favorite yet. Use /setfav first!")

async def inline_query(update: Update, context: CallbackContext):
    query = update.inline_query.query.strip()
    offset = int(update.inline_query.offset or 0)
    page_size = 50

    all_characters = []
    for rarity, chara_list in characters.items():
        for chara in chara_list:
            all_characters.append({
                "name": chara["name"],
                "rarity": rarity,
                "url": chara["url"],
                "style": rarity_styles.get(rarity, "")
            })

    if query:
        all_characters = [c for c in all_characters if query.lower() in c["name"].lower()]

    page = all_characters[offset:offset + page_size]
    results = [
        InlineQueryResultPhoto(
            id=str(offset + idx),
            photo_url=chara["url"],
            thumb_url=chara["url"],
            title=f"{chara['name']} ({chara['rarity']})",
            description=f"Rarity: {chara['rarity']}",
            caption=f"{chara['style']} {chara['name']} ({chara['rarity']})"
        )
        for idx, chara in enumerate(page)
    ]

    next_offset = str(offset + page_size) if len(all_characters) > offset + page_size else ""
    await update.inline_query.answer(results, cache_time=1, next_offset=next_offset)

async def setfav(update: Update, context: CallbackContext):
    if not update.effective_user or not update.message:
        return

    user_id = update.effective_user.id
    if user_id in last_summons:
        favorites[user_id] = last_summons[user_id]
        await update.message.reply_text(f"💖 {last_summons[user_id]['name']} is now your favorite!")
    else:
        await update.message.reply_text("You haven't summoned any character yet!")

async def post_init(application):
    commands = [
        BotCommand("start", "Start the bot and get help"),
        BotCommand("summon", "Summon a random character (owner only)"),
        BotCommand("marry", "Marry your last summoned character"),
        BotCommand("collection", "View your character collection"),
        BotCommand("fav", "View your favorite character"),
        BotCommand("setfav", "Set your last summoned character as favorite"),
    ]
    await application.bot.set_my_commands(commands)
    print("🤖 Bot commands registered successfully")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN environment variable not set!")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summon", summon))
    application.add_handler(CommandHandler("marry", marry))
    application.add_handler(CommandHandler("collection", collection))
    application.add_handler(CommandHandler("fav", fav))
    application.add_handler(CommandHandler("setfav", setfav))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(InlineQueryHandler(inline_query))

    application.post_init = post_init

    print("🤖 Summon Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
