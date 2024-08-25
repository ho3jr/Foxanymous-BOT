from pyrogram import Client, filters
from pyrogram.types import Message,  KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, MessageEntity
import pyromod
import sqlite3 as sq
import random
from datetime import datetime
import string

import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding



api_id = 111111111
api_hash = ""
token= ""

app = Client(       #connect to bot
    "nashenas_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=token)

db = sq.connect("data_users.db",check_same_thread=False)        #connect to database
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
cursor = db.cursor()
db.execute(
    """CREATE TABLE IF NOT EXISTS najvas_msg(
        id_db INTEGER PRIMARY KEY,
        unique_id VARCHAR(15),
        ecrypt_text VARCHAR(1000),
        sender_id INTEGER,
        receiver_id_username VARCHAR(20)
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


def generate_key_and_iv():      #generate key and iv
    key = os.urandom(32)  # کلید 32 بایتی برای AES-256
    iv = os.urandom(16)   # IV باید 16 بایت باشد
    return key, iv


def encrypt_aes(plain_text, key, iv):       #encrypting by aes
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()
    cipher_text = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(iv + cipher_text).decode('utf-8')


def decrypt_aes(cipher_text, key):      #decrypting
    cipher_data = base64.b64decode(cipher_text)
    iv = cipher_data[:16]
    ct = cipher_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plain_text = decryptor.update(ct) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plain_text = unpadder.update(padded_plain_text) + unpadder.finalize()
    return plain_text.decode('utf-8')

key, iv = generate_key_and_iv()


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
                        keyboard_for_send_reply = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("پاسخ", callback_data="send_reply_/"+ str(m.from_user.id)+"_/"+str(m.id)+"_/"+str(answer.id))],
                            ]
                        )
                        await app.send_message(user_info[0], "پیام ناشناس داری عزیزم:")
                        await app.copy_message(user_info[0], answer.from_user.id, answer.id, reply_markup=keyboard_for_send_reply, )
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


                await Sendـanـanonymousـmessage(m, user_info)

        except:
            await app.send_message(m.from_user.id, "**کاربر ربات رو استارت نزده.** شاید بتونی لینک ناشناس خودتو بهش بدی تا ربات رو استارت بزنه؟\n/myinfo")


    elif m.text == "سورس ربات | درباره ربات" or m.text =="/robot_source":       #send robot source
        await app.send_message(m.from_user.id, "ربات فاکسامینوس به صورت کاملا اوپن سورس منتشر شده است و تمام توسعه دهندگان و برنامه نویسان میتوانند از این ربات استفاده کنند و آن را توسعه بدهند. از ویژگی های این ربات، میتوان به **حفظ حریم خصوصی** افراد اشاره کرد. این ربات اطلاعات و پیام های کاربران در هیچ کجا ذخیره نمیکند و به هیچ وجه ادمین به پیام های شما دسترسی ندارد. \n**این ربات به زبان پایتون و با کتابخانه pyrogram نوشته شده است!**\n\nعلاقه مندان به توسعه و استفاده از سورس ربات میتوانند از لینک زیر عمل کنند:\n**◉ [Robot Source](https://github.com/ho3jr/Foxanymous-BOT)**\nسازنده ربات: https://t.me/NaGHiZam")


    elif m.text == "/ping" or m.text == "Ping":
        start_t = datetime.now()
        await app.send_message(m.chat.id,"Pong!")
        end_t = datetime.now()
        time_taken_s = (end_t - start_t).microseconds / 1000
        await app.send_message(m.chat.id,f"Ping Pong Speed\n{time_taken_s} milli-seconds")
@app.on_callback_query()        #receive query
async def query_receiver(Client, call1):
    

    async def Sendـanـanonymousـreply(m, user_info, answer):        #reply option

        if user_info[1] != int(m.from_user.id):
            try:
                keyboard_for_send_reply = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("پاسخ", callback_data="send_reply_/"+ str(user_info[3])+"_/"+str(user_info[2]))],
                    ]
                )
                await app.send_message(user_info[1], "پیام ناشناس داری عزیزم:")
                await app.copy_message(user_info[1], user_info[3], answer.id ,reply_markup=keyboard_for_send_reply, reply_to_message_id=user_info[4])
                await app.send_message(answer.from_user.id, "**پیام با موفقیت ارسال شد!**\n **◉ [Robot Source](https://github.com/ho3jr/)**", reply_to_message_id= answer.id, disable_web_page_preview=True)

            except:
                await app.send_message(m.from_user.id,"**هیچ پیامی دریافت نشد!**")
        else:
            await app.send_message(m.from_user.id,"**با خودت حرف میزنی؟**")

    data = call1.data
    if data == "learn_how_to_recive_id_group":
        await app.send_message(call1.message.chat.id, "🆔**آموزش پیدا کردن آیدی عددی** \nبرای پیدا کردن آیدی یک کاربر میتوانید از ربات زیر استفاده کنید:\n@username_to_id_bot.")

    try:
        if data.split("_/")[0] == "send_reply":
            id_tel  = data.split("_/")[1]
            id_msg = int(data.split("_/")[2])
            answer_id = int(data.split("_/")[3])
            try:
                answer = await app.ask(int(call1.from_user.id), "منتظر پاسخ شما هستیم", timeout=120, disable_web_page_preview=True)

                if answer:
                    if answer.text=="/cancel":
                        await app.send_message(answer.from_user.id, "**کنسل شد!**")

                    else:
                        user_info = (id_msg, id_tel, call1.message.id, call1.from_user.id, answer_id)
                        await Sendـanـanonymousـreply(call1, user_info, answer)
            except:
                pass
    except:
        pass



    see_najva_part = data.split("/")[0]

    if see_najva_part == "see_najva":       
        unique_id = data.split("/")[1]
        cursor.execute("SELECT ecrypt_text, sender_id, receiver_id_username FROM najvas_msg WHERE unique_id=?", (unique_id,))
        result = cursor.fetchone()
        if result:
            ciphertext = result[0]
            sender_id = int(result[1])
            receiver_id = result[2]
            if receiver_id.isdigit():
                receiver_id = int(receiver_id)
            else:
                receiver_id = str(receiver_id)
            print(receiver_id)
            decrypted_text = decrypt_aes(ciphertext, key)
            if call1.from_user.id == sender_id or call1.from_user.username == receiver_id or call1.from_user.id == receiver_id:
                await app.answer_callback_query(call1.id, text=decrypted_text, show_alert=True)

            else:
                 await app.answer_callback_query(call1.id, text="این پیام برای شما نیست", show_alert=True)


@app.on_inline_query()
def inline_query_handler(client, inline_query):
    try:        #show result for najva
        send_btn = []
        query = inline_query.query
        text = query.split("/")[0]

        last_slash = query.split("/")[2]
        if last_slash == " send" or last_slash == "send":
            unique_id = generate_unique_id()

            sender_id = inline_query.from_user.id
            receiver_id_username = query.split("/")[1]

            cipher_text = encrypt_aes(text, key, iv)


            db.execute("""INSERT INTO najvas_msg(unique_id, ecrypt_text, sender_id, receiver_id_username) VALUES(?,?,?,?)""",(unique_id, cipher_text, sender_id, receiver_id_username))
            db.commit()
            send_najva_btn = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("مشاهده نجوا", callback_data="see_najva/" + unique_id)],
                ]
            )
            if receiver_id_username.isdigit():
                receiver_id_username = int(receiver_id_username)

                link_pr = "tg://user?id={}".format(receiver_id_username)
                send_btn = [
                    InlineQueryResultArticle(
                        id=unique_id,  
                        title="همه چیز به نظر درسته",
                        reply_markup=send_najva_btn,
                        input_message_content=InputTextMessageContent(
                            "این یک پیام نجوا برای کاربر زیر است:\n {}".format(link_pr)),
                        
                    )
                ]
                app.answer_inline_query(inline_query.id, send_btn)
            else:
                receiver_id_username = str(receiver_id_username)
                receiver_id_username = ''.join(receiver_id_username.split(" "))
                receiver_id_username = ''.join(receiver_id_username.split("@"))

                link_pr = "@"+(receiver_id_username)
                send_btn = [
                    InlineQueryResultArticle(
                        id=unique_id,  
                        title="همه چیز به نظر درسته",
                        reply_markup=send_najva_btn,
                        input_message_content=InputTextMessageContent(
                            "این یک پیام نجوا برای کاربر زیر است:\n {}".format(link_pr)),
                        
                    )
                ]
                app.answer_inline_query(inline_query.id, send_btn)

    except:         #show result for najva
        najva_info = [
            InlineQueryResultArticle(
                id=1 ,
                title="آموزش استفاده از بخش نجوا",
                input_message_content=InputTextMessageContent(
                    "**برای استفاده از بخش نجوا** بعد از یوزرنیم ربات نام کاربری خود را بنویسید. سپس یک / گذاشته و یوزرنیم یا آیدی عددی کاربر مورد نظر را بنویسید. و در انتها دوباره / گذاشته و عبارت send را بنویسید."+"\n\nمثال:\n @robot text message is here / username(or ID) /send",
                )
            )
        ]

        app.answer_inline_query(inline_query.id, najva_info)

app.run()