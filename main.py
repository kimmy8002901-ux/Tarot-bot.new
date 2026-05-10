import os
import random
import asyncio
import google.generativeai as genai
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
PHONE_NUMBER = os.environ.get("PHONE_NUMBER")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

SYSTEM_PROMPT = """
မင်းက သာမန် မြန်မာလူငယ်တစ်ယောက်ပါ။
နာမည် နာမည်မင်းရဲ့ ၊ အွန်လိုင်းမှာ တာရော့ဖဲထုတ်ပေးနေတဲ့သူပါ။
အောက်ပါအတိုင်း တင်းကြပ်စွာ လိုက်နာပါ-
- "ကျွန်တော်/ကျွန်မ" မသုံးဘဲ "ကျွန်တော့်/client လေး စတဲ့
စတဲ့ ရင်းနှီးတဲ့အသုံးအနှုန်းများကိုသာ သုံးပါ။
- အင်္ဂလိပ်စာလုံး သိပ်မသုံးဘဲ မြန်မာလိုပဲ ရေးပါ။
- စာလုံးပေါင်း ပြည့်စုံလွန်းအောင် မရေးဘဲ ပေါ့ပေါ့ပါးပါး နေ့စဉ်သုံးစကားပုံစံ ရေးပါ။
- Emoji 😊✨ များများသုံးပါ (သို့သော် အလွန်အကျွံမဟုတ်)။
- တစ်ခါတစ်ရံ "..." "အင်း..." "ဟုတ်တယ်နော်" စသည်ဖြင့် ဝေ့လည်ကြောင်ပတ် ရေးပါ။
- မေးခွန်းမသိရင် "အိုး... ဒီတစ်ခုတော့ ငါလည်း သေချာမသိဘူးဗျ" လိုမျိုး လူပုံစံကျကျ ပြောပါ။
- AI / Bot ဆိုတဲ့ စကားမျိုး ဘယ်တော့မှ မပြောရ။
- တာရော့ဖဲထုတ်ခိုင်းရင် ဖဲချပ် ၃ ချပ်ဆွဲပေးပြီး နေရာလိုက် အဓိပ္ပါယ်ပြန်ပေးပါ။
- စကားပြောတဲ့အခါ အေးအေးဆေးဆေး ဖော်ဖော်ရွေရွေနဲ့ သဘာဝကျကျ ဖြေပါ။
"""

client = TelegramClient('my_account', API_ID, API_HASH)

user_histories = {}

@client.on(events.NewMessage(incoming=True))
async def auto_reply(event):
    if event.out:
        return

    sender = await event.get_sender()
    user_id = sender.id
    user_msg = event.message.text

    await client.send_chat_action(user_id, 'typing')
    await asyncio.sleep(random.uniform(1.5, 3.5))

    if user_id not in user_histories:
        user_histories[user_id] = []

    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]

    full_prompt = f"{SYSTEM_PROMPT}\n\n"
    for entry in user_histories[user_id]:
        full_prompt += f"{entry['role']}: {entry['content']}\n"
    full_prompt += f"user: {user_msg}\nassistant:"

    try:
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
    except Exception as e:
        reply = "အိုး... ခဏလေး ပြန်ပြောပါဦး 😅"

    await event.reply(reply)

    user_histories[user_id].append({"role": "user", "content": user_msg})
    user_histories[user_id].append({"role": "assistant", "content": reply})

print("Bot is starting...")
client.start(phone=PHONE_NUMBER)
print("Bot is running!")
client.run_until_disconnected()
