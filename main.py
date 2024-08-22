from pyrogram import Client, filters
from pyrogram.types import Message,  KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton 
import pyromod
import sqlite3 as sq
import random
import string


api_id = 11111111
api_hash = ""
token= ""

app = Client(       #connect to bot
    "nashenas_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=token)

db = sq.connect("data_users.db")        #connect to database
cursor = db.cursor()
db.execute(
    """CREATE TABLE IF NOT EXISTS users(
        id_db INTEGER PRIMARY KEY,
        id_tel INTEGER,
        firstname VARCHAR(30),
        lastname VARCHAR(30),
        username VARCHAR(30),
        unique_id VARCHAR(15)
        )"""
)

link = "https://telegram.me/ho3jrbot?start="


button1 = KeyboardButton("لینک من")
button2 = KeyboardButton("به مخاطب خاصم وصلم کن")
button3 = KeyboardButton("راهنما")
button4 = KeyboardButton("سورس ربات | درباره ربات")
    

keyboard_start = ReplyKeyboardMarkup([[button1, button2], [button3, button4]], resize_keyboard=True)

learn_how_to_recive_id_group = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("پیدا کردن آیدی عددی❓", callback_data="learn_how_to_recive_id_group")]
    ]
)


def generate_unique_id():      #generate unique id
    characters = string.ascii_letters + string.digits 
    password = ''.join(random.choice(characters) for i in range(12))
    return password 


@app.on_message(filters.private)        #receive msg in PV
async def PV_main(c: Client, m: Message):

    async def Sendـanـanonymousـmessage(m, user_info):
        if user_info[0] != int(m.from_user.id):
            try:
                answer = await app.ask(int(m.from_user.id), "در حال ارسال پیام ناشناس به **{}** هستی. هر پیامی ارسال کنی به صورت کاملا محرمانه ارسال خواهد شد. /cancel \n **◉ [Robot Source](https://github.com/ho3jr/)**".format(user_info[1]),timeout=120, disable_web_page_preview=True)
                if answer :
                    if answer.text=="/cancel":
                        await app.send_message(answer.from_user.id, "**کنسل شد!**")

                    else:
                        await app.send_message(user_info[0], "پیام ناشناس داری عزیزم:")
                        await app.copy_message(user_info[0], answer.from_user.id, answer.id)
                        await app.send_message(answer.from_user.id, "**پیام با موفقیت ارسال شد!**\n **◉ [Robot Source](https://github.com/ho3jr/)**", reply_to_message_id= answer.id, disable_web_page_preview=True)

            except:
                await app.send_message(m.from_user.id,"**هیچ پیامی دریافت نشد!**")
        else:
            await app.send_message(m.from_user.id,"**با خودت حرف میزنی؟**")

    
    def check_id_in_database():
        cursor.execute("SELECT id_tel FROM users WHERE id_tel=?", (m.from_user.id,))
        result = cursor.fetchone()
        if result:
            return True
        
    async def add_user_to_database(): 
        if check_id_in_database():
            pass
        else:
            db.execute(
                """
                INSERT INTO users(id_tel, firstname, lastname, username, unique_id) VALUES(?,?,?,?,?)""",
                (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username, generate_unique_id())
            )
            db.commit()

    await add_user_to_database()

    try:
        unique_id  = m.text.split(" ")[1]       #receive x for exmple in: https://telegram.me/ho3jr?start=x
    except:
        pass
    try:
        if unique_id:
            user_info = cursor.execute(
                "SELECT id_tel, firstname FROM users WHERE unique_id=?", (unique_id,)
                )
            if user_info:
                for i in user_info:
                    user_info= i

                await Sendـanـanonymousـmessage(m, user_info)

            else:
                await app.send_message(m.from_user.id,"**کاربر پیدا نشد!**")
    except:
        pass

    if m.text == "/start":      #start message
        await app.send_message(m.from_user.id,"به ربات فاکسانیموس خوش اومدی😘\nمیتوانید از دستور /help برای راهنمایی استفاده کنید.", reply_markup=keyboard_start, disable_web_page_preview=True)


    elif m.text == "/myinfo" or m.text == "لینک من":       #send user link 
        user_info = cursor.execute(
            "SELECT unique_id FROM users WHERE id_tel=?", (m.from_user.id,)
            )
        for i in user_info:
            user_info = i
        await app.send_message(m.from_user.id,"{} عزیز!\nلینک ناشناس شما: \n{}{}\nمیتونی لینکتو برای دوستات بفرستی تا بتونن حرف دلشون رو راحت و ناشناس بهت بزنن\n**◉ [Robot Source](https://github.com/ho3jr/)**".format(m.from_user.first_name, link, user_info[0]), disable_web_page_preview=True)

    elif m.text == "/help" or m.text == "راهنما":       #help message
        await app.send_message(m.from_user.id, "**دستورات قابل استفاده در ربات:**\n\n/connect_to_user   وصل شدن به مخاطب\n/myinfo  دریافت لینک ناشناس\n/robot_source   سورس ربات\n")

    elif m.text == "/connect_to_user" or m.text == "به مخاطب خاصم وصلم کن":
        try:
            answer = await app.ask(int(m.from_user.id), "یوزرنیم مخاطب**(بدون @)** یا آیدی عددی مخاطب مورد نظر را ارسال کنید./cancel\n**◉ [Robot Source](https://github.com/ho3jr/)**", timeout=120, disable_web_page_preview=True, reply_markup=learn_how_to_recive_id_group)

            if answer.text.isdigit():
                user_info = cursor.execute(
                "SELECT id_tel, firstname FROM users WHERE id_tel=?", (int(answer.text),)
                )
                for i in user_info:
                    user_info = i

                await Sendـanـanonymousـmessage(m,user_info)
            
            elif answer.text == "/cancel":
                await app.send_message(answer.from_user.id, "**کنسل شد!**")

            else:
                user_info = cursor.execute(
                "SELECT id_tel, firstname FROM users WHERE username=?", (answer.text,)      #check in database with username
                )
                for i in user_info:
                    user_info = i

                print(user_info)
                await Sendـanـanonymousـmessage(m, user_info)

        except:
            await app.send_message(m.from_user.id, "**کاربر ربات رو استارت نزده.** شاید بتونی لینک ناشناس خودتو بهش بدی تا ربات رو استارت بزنه؟\n/myinfo")


    elif m.text == "سورس ربات | درباره ربات" or m.text =="/robot_source":       #send robot source
        await app.send_message(m.from_user.id, "ربات فاکسامینوس به صورت کاملا اوپن سورس منتشر شده است و تمام توسعه دهندگان و برنامه نویسان میتوانند از این ربات استفاده کنند و آن را توسعه بدهند. از ویژگی های این ربات، میتوان به **حفظ حریم خصوصی** افراد اشاره کرد. این ربات اطلاعات و پیام های کاربران در هیچ کجا ذخیره نمیکند و به هیچ وجه ادمین به پیام های شما دسترسی ندارد. \n**این ربات به زبان پایتون و با کتابخانه pyrogram نوشته شده است!**\n\nعلاقه مندان به توسعه و استفاده از سورس ربات میتوانند از لینک زیر عمل کنند:\n**◉ [Robot Source](https://github.com/ho3jr/)**\nسازنده ربات: https://t.me/NaGHiZam")


@app.on_callback_query()        #receive query
async def query1(Client, call1):
    data = call1.data
    if data == "learn_how_to_recive_id_group":
        await app.send_message(call1.message.chat.id, "🆔**آموزش پیدا کردن آیدی عددی** \nبرای پیدا کردن آیدی یک کاربر میتوانید از ربات زیر استفاده کنید:\n@username_to_id_bot.")


app.run()