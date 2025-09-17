from telegram.ext import Application

async def main():
    app = Application.builder().token("BOT_TOKEN").build()
    print("Application built successfully")

if name == "main":
    import asyncio
    asyncio.run(main())
