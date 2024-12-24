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
INFO = open("INFO.txt", 'r')
lines = INFO.readlines()


api_id = int(lines[1])
api_hash = "".join(str(lines[4]).split("\n"))
token= "".join(str(lines[7]).split("\n"))
link = "".join(str(lines[10]).split("\n"))

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
        unique_id VARCHAR(15),
        blocklist VARCHAR(5000)
        )"""
)
cursor = db.cursor()
db.execute(
    """CREATE TABLE IF NOT EXISTS najvas_msg(
        id_db INTEGER PRIMARY KEY,
        unique_id VARCHAR(15),
        ecrypt_text VARCHAR(1000),
        sender_id INTEGER,
        receiver_id_username VARCHAR(20),
        receiver_name VARCHAR(30),
        readed VARCHAR(6),
        chat_id INTEGER,
        message_id INTEGER
        )"""
)

cursor = db.cursor()
db.execute(
    """CREATE TABLE IF NOT EXISTS pv_msg(
        id_db INTEGER PRIMARY KEY,
        sender_name VARCHAR(30),
        receiver_name VARCHAR(30),
        unique_id VARCHAR(15),
        ecrypt_text VARCHAR(1000),
        sender_id INTEGER,
        receiver_id VARCHAR(20),
        answer_id INTEGER,
        readed VARCHAR(6)
        )"""
)
db.commit()

button1 = KeyboardButton("🔗لینک من")
button2 = KeyboardButton("📝به‌مخاطب‌خاصم‌وصلم‌کن")
button3 = KeyboardButton("❓راهنما")
button4 = KeyboardButton("🤖درباره ربات")
button5 = KeyboardButton("📣چنل")
button6 = KeyboardButton("👤اکانت من")

button7 = KeyboardButton("لغو کردن")
    

keyboard_start = ReplyKeyboardMarkup([[button1, button2], [button3, button4, button5], [button6]], resize_keyboard=True)
keyboard_cancel = ReplyKeyboardMarkup([[button7]], resize_keyboard=True)

               
see_help_najva_btn = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("آموزش ارسال نجوا", callback_data="see_help_najva")],
    ]
)

user_pannel_keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🗑پاکسازی بلاک لیست", callback_data="reset_block_list/")]
            ]
        )

learn_how_to_recive_id_group = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("پیدا کردن آیدی عددی❓", callback_data="learn_how_to_recive_id_group")]
    ]
)

channel_link_button = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("چنل", url="https://t.me/+1Epzafcu40Q1Njlk")]
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

    # Decode the base64 encoded ciphertext
    cipher_text_bytes = base64.b64decode(cipher_text)
    
    # Extract the IV and the actual ciphertext
    iv = cipher_text_bytes[:16]  # Assuming AES block size is 16 bytes
    actual_cipher_text = cipher_text_bytes[16:]

    # Create a cipher object
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    # Decrypt the data
    padded_plain_text = decryptor.update(actual_cipher_text) + decryptor.finalize()
    
    # Unpad the data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plain_text = unpadder.update(padded_plain_text) + unpadder.finalize()
    
    return plain_text.decode('utf-8')
key, iv = generate_key_and_iv()


def generate_unique_id():      #generate unique id
    characters = string.ascii_letters + string.digits 
    password = ''.join(random.choice(characters) for i in range(12))
    return password 

async def check_blocklist(sender_id, reciever_id):
    cursor.execute("SELECT blocklist FROM users WHERE id_tel=?", (int(reciever_id),))
    blocklist = cursor.fetchone()
    try:
        data_list = [int(item) for item in blocklist[0].split('/') if item]
        if sender_id in data_list:
            return False
        else:
            return True
    except:
        return True

@app.on_message(filters.private)        #receive msg in PV
async def PV_main(c: Client, m: Message):

    async def Sendـanـanonymousـmessage(m, user_info):
        if user_info[0] != int(m.from_user.id):
            if await check_blocklist(m.from_user.id, user_info[0]):

                try:
                    answer = await app.ask(int(m.from_user.id), "📤در حال ارسال پیام ناشناس به **{}** هستی. هر پیامی ارسال کنی به صورت کاملا محرمانه ارسال خواهد شد. /cancel \n **◉ [Robot Source](https://github.com/ho3jr/)**".format(user_info[1]),timeout=120, disable_web_page_preview=True,  reply_markup=keyboard_cancel )
                    if answer :
                        if answer.text=="/cancel" or  answer.text=="لغو کردن":
                            await app.send_message(answer.from_user.id, "**✅کنسل شد!**", reply_markup= keyboard_start)

                        else:
                            unique_id = generate_unique_id()
                            db.execute(
                                """
                                INSERT INTO pv_msg(sender_name, receiver_name, unique_id, ecrypt_text, sender_id, receiver_id, answer_id, readed) VALUES(?,?,?,?,?,?,?,?)""",
                                (m.from_user.first_name, user_info[1], unique_id, encrypt_aes(answer.text, key, iv), m.from_user.id, user_info[0], answer.id, False)
                            )
                            db.commit()


                            keyboard_for_send_reply = InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton("🔁پاسخ", callback_data="send_reply_/"+ str(unique_id) )],
                                    [InlineKeyboardButton("🔒بلاک", callback_data="block_/"+str(unique_id))]
                                ]
                            )
                            await app.send_message(user_info[0], "📬پیام ناشناس داری عزیزم:")
                            await app.copy_message(user_info[0], answer.from_user.id, answer.id, reply_markup=keyboard_for_send_reply, )
                            await app.send_message(answer.from_user.id, "**✅پیام با موفقیت ارسال شد!**\n **◉ [Robot Source](https://github.com/ho3jr/)**", reply_to_message_id= answer.id, disable_web_page_preview=True, reply_markup=keyboard_start)

                except:
                    await app.send_message(m.from_user.id,"**❗️هیچ پیامی دریافت نشد!**")
            else:
                await app.send_message(m.from_user.id,"**🤨شما بلاک شده اید!**")
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
                await app.send_message(m.from_user.id,"**❗️کاربر پیدا نشد!**")
    except:
        pass

    if m.text == "/start":      #start message
        await app.send_message(m.from_user.id,"به ربات فاکسانیموس خوش اومدی😘\nمیتوانید از دستور /help برای راهنمایی استفاده کنید.", reply_markup=keyboard_start, disable_web_page_preview=True)

    elif m.text == "📣چنل":
         await app.send_message(m.from_user.id,"📢برای عضو شدن در چنل اصلی ربات جهت خبر دار شدن از اخبار و اپدیت های ربات بر روی دکمه زیر کلیک کنید.", reply_markup=channel_link_button)

    elif m.text == "/myinfo" or m.text == "🔗لینک من":       #send user link 
        user_info = cursor.execute(
            "SELECT unique_id FROM users WHERE id_tel=?", (m.from_user.id,)
            )
        for i in user_info:
            user_info = i
        await app.send_message(m.from_user.id,"{} عزیز!\n❗️لینک ناشناس شما: \n{}{}\nمیتونی لینکتو برای دوستات بفرستی تا بتونن حرف دلشون رو راحت و ناشناس بهت بزنن\n**◉ [Robot Source](https://github.com/ho3jr/)**".format(m.from_user.first_name, link, user_info[0]), disable_web_page_preview=True)

    elif m.text == "/help" or m.text == "❓راهنما":       #help message
        await app.send_message(m.from_user.id, "**دستورات قابل استفاده در ربات:**\n\n/connect_to_user   وصل شدن به مخاطب\n/myinfo  دریافت لینک ناشناس\n/robot_source   سورس ربات\n\n**بخش نجوا**\nبرای استفاده از بخش نجوا ربات را در گروه ادمین کنید. سپس میتوانید در گروه از ربات استفاده کنید.\n برای ارسال نجوا بعد از اطمینان از ادمین بودن ربات در گروه به صورت زیر عمل کنید:\n۱-نام کاربری ربات\n۲-یک فاصله\n۳-نوشتن پیام\n۴-ریپلای بر شخص مورد نظر\n۵-کلیک بر روی دکمه ارسال\nمثال:\n`@FoxanymousBOT message`\n\nاستفاده از نجوا با یوزرنیم و آیدی:\n`@FoxanymousBOT message @username`\n\n`@FoxanymousBOT message @111111111`")

    elif m.text == "/connect_to_user" or m.text =="📝به‌مخاطب‌خاصم‌وصلم‌کن":
        try:
            answer = await app.ask(int(m.from_user.id), "📱یوزرنیم مخاطب**(بدون @)** یا آیدی عددی مخاطب مورد نظر را ارسال کنید./cancel\n**◉ [Robot Source](https://github.com/ho3jr/)**", timeout=120, disable_web_page_preview=True, reply_markup=learn_how_to_recive_id_group)

            if answer.text.isdigit():
                user_info = cursor.execute(
                "SELECT id_tel, firstname FROM users WHERE id_tel=?", (int(answer.text),)
                )
                for i in user_info:
                    user_info = i

                await Sendـanـanonymousـmessage(m,user_info)
            
            elif answer.text == "/cancel":
                await app.send_message(answer.from_user.id, "✅**کنسل شد!**", reply_markup= keyboard_start)

            else:
                user_info = cursor.execute(
                "SELECT id_tel, firstname FROM users WHERE username=?", (answer.text,)      #check in database with username
                )
                for i in user_info:
                    user_info = i


                await Sendـanـanonymousـmessage(m, user_info)

        except:
            await app.send_message(m.from_user.id, "👤❗️**کاربر ربات رو استارت نزده.** شاید بتونی لینک ناشناس خودتو بهش بدی تا ربات رو استارت بزنه؟\n/myinfo")


    elif m.text == "🤖درباره ربات" or m.text =="/robot_source":       #send robot source
        await app.send_message(m.from_user.id, "ربات فاکسامینوس به صورت کاملا اوپن سورس منتشر شده است و تمام توسعه دهندگان و برنامه نویسان میتوانند از این ربات استفاده کنند و آن را توسعه بدهند. از ویژگی های این ربات، میتوان به **حفظ حریم خصوصی** افراد اشاره کرد. این ربات اطلاعات و پیام های کاربران در هیچ کجا ذخیره نمیکند و به هیچ وجه ادمین به پیام های شما دسترسی ندارد. \n**این ربات به زبان پایتون و با کتابخانه pyrogram نوشته شده است!**\n\nعلاقه مندان به توسعه و استفاده از سورس ربات میتوانند از لینک زیر عمل کنند:\n**◉ [Robot Source](https://github.com/ho3jr/Foxanymous-BOT)**\nسازنده ربات: https://t.me/NaGHiZam")


    elif m.text == "/ping" or m.text == "Ping":
        start_t = datetime.now()
        await app.send_message(m.chat.id,"Pong!")
        end_t = datetime.now()
        time_taken_s = (end_t - start_t).microseconds / 1000
        await app.send_message(m.chat.id,f"Ping Pong Speed\n{time_taken_s} milli-seconds")

    elif m.text == "/db_info":
        try:
            number_of_user_nashenas = 0
            number_of_user_najva = 0
            number_of_pv_msg = 0
            if m.from_user.id == int(lines[16]):

                cursor.execute(
                    "SELECT id_db FROM users ORDER BY id_db DESC LIMIT 1"  # چک کردن در پایگاه داده با نام کاربری
                )
                number_of_user_nashenas = cursor.fetchone()


                cursor.execute("SELECT COUNT(*) FROM najvas_msg WHERE chat_id != ?", (1, ))
                number_of_user_najva = cursor.fetchone()


                cursor.execute(
                    "SELECT id_db FROM pv_msg ORDER BY id_db DESC LIMIT 1"  # چک کردن در پایگاه داده با نام کاربری
                )
                number_of_pv_msg = cursor.fetchone()

                await app.send_document(int(lines[16]), "data_users.db")
                await app.send_message(int(lines[16]), "تعداد کاربران چت ناشناس: {}\nتعداد پیام های نجوا: {}\nتعداد پیام ناشناس ارسال شده:{}".format(number_of_user_nashenas[0] if number_of_user_nashenas != None else number_of_user_nashenas , number_of_user_najva[0] if number_of_user_najva != None else number_of_user_najva, number_of_pv_msg[0] if number_of_pv_msg != None else number_of_pv_msg))
        except KeyError:
            print(KeyError)

    elif m.text == "/send_message":
        try:
            if m.from_user.id == int(lines[16]):
                yes_no_keyboard = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("✅بله", callback_data="send_message_to_users/"), 
                             InlineKeyboardButton ("❌نه", callback_data="no_send_message_to_users/")]
                        ]
                    )
                await app.send_message( m.chat.id, "برای کاربران ربات پیام ارسال شود؟", reply_markup=yes_no_keyboard)
        except KeyError:
            print(KeyError)


    elif m.text == "👤اکانت من":
        try:
            cursor.execute("SELECT COUNT(*) FROM pv_msg WHERE sender_id = ?", (m.from_user.id,))
            send_pv_msg_count = cursor.fetchone()[0]  
            cursor.execute("SELECT COUNT(*) FROM pv_msg WHERE receiver_id = ?", (m.from_user.id,))
            receive_pv_msg_count = cursor.fetchone()[0]  
            cursor.execute("SELECT COUNT(*) FROM najvas_msg WHERE sender_id = ? AND chat_id != ?", (m.from_user.id, 1))
            najvas_msg_count = cursor.fetchone()[0] 

            send_pv_msg_count = send_pv_msg_count if send_pv_msg_count is not None else 0
            receive_pv_msg_count = receive_pv_msg_count if receive_pv_msg_count is not None else 0
            najvas_msg_count = najvas_msg_count if najvas_msg_count is not None else 0

            username = m.from_user.username if m.from_user.username else "ندارد"

            first_name = m.from_user.first_name if m.from_user.first_name else "نام ندارد"
            last_name = m.from_user.last_name if m.from_user.last_name else ""

            language_code = m.from_user.language_code if m.from_user.language_code else "زبان ندارد"

            await app.send_message(m.chat.id, "نام شما: {} {}\nآیدی عددی شما‍‍: `{}`\nنام کاربری شما: @{}\nزبان تلگرام شما: {}\nلینک شما: /myinfo\nتعداد پیام های ارسال شده ناشناس: {}\nتعداد پیام های دریافت شده: {}\nتعداد نجوا های ارسال شده: {}"
                                .format(first_name, last_name, m.from_user.id, username, language_code, send_pv_msg_count, receive_pv_msg_count, najvas_msg_count), reply_markup= user_pannel_keyboard)

        except KeyError:
            print(KeyError)

@app.on_callback_query()        #receive query
async def query_receiver(Client, call1):

    async def blocker(call1, data):
        cursor.execute("SELECT sender_id, receiver_id FROM pv_msg WHERE unique_id=?", (str(data.split("_/")[1]),))
        ids = cursor.fetchone()
        cursor.execute("SELECT blocklist FROM users WHERE id_tel=?", (call1.from_user.id, ))
        blocklist = cursor.fetchone()
        unblock_btn = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔓آنبلاک", callback_data="unblock_/"+str(data.split("_/")[1]))],
                    ]
                )
        if blocklist[0] == None or blocklist[0] == "":
            blocklist_new = str(ids[0])+"/" if call1.from_user.id == int(ids[1]) else str(ids[1])+"/" 
            db.execute("UPDATE users SET blocklist=? WHERE id_tel =? ",(blocklist_new, call1.from_user.id))
            db.commit()
            await app.answer_callback_query(call1.id, text="✅کاربر بلاک شد", show_alert=True)
            await app.edit_message_reply_markup(call1.message.chat.id, call1.message.id, reply_markup=unblock_btn)
        else:
            data_list = [int(item) for item in blocklist[0].split('/') if item]
            if int(ids[0]) in data_list or int(ids[1]) in data_list:
                await app.answer_callback_query(call1.id, text="❌کاربر از قبل بلاک شده بود", show_alert=True)
                await app.edit_message_reply_markup(call1.message.chat.id, call1.message.id, reply_markup=unblock_btn)
            else:
                blocklist_new = str(blocklist[0]) + str(ids[0])+"/" if call1.from_user.id == ids[1] else str(blocklist[0]) + str(ids[1])+"/"
                db.execute("UPDATE users SET blocklist=? WHERE id_tel =? ",(blocklist_new, call1.from_user.id))
                db.commit()
                await app.answer_callback_query(call1.id, text="✅کاربر بلاک شد", show_alert=True)
                await app.edit_message_reply_markup(call1.message.chat.id, call1.message.id, reply_markup=unblock_btn)
    
    async def unblocker(call1, data):
        cursor.execute("SELECT sender_id, receiver_id FROM pv_msg WHERE unique_id=?", (str(data.split("_/")[1]),))
        ids = cursor.fetchone()
        cursor.execute("SELECT blocklist FROM users WHERE id_tel=?", (call1.from_user.id, ))
        blocklist = cursor.fetchone()
        data_list = [int(item) for item in blocklist[0].split('/') if item]
        block_btn = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔒بلاک", callback_data="block_/"+str(data.split("_/")[1]))]
                    ]
                )
        if int(ids[0]) in data_list or int(ids[1]) in data_list:
            blocklist_new = blocklist[0].replace("{}".format(str(ids[0])+"/"), "") if call1.from_user.id == int(ids[1]) else blocklist[0].replace("{}".format(str(ids[1])+"/"), "") 
            db.execute("UPDATE users SET blocklist=? WHERE id_tel =? ",(blocklist_new, call1.from_user.id))
            db.commit()
            await app.answer_callback_query(call1.id, text="✅کاربر آنبلاک شد", show_alert=True)
            await app.edit_message_reply_markup(call1.message.chat.id, call1.message.id, reply_markup=block_btn)
        else:
            await app.answer_callback_query(call1.id, text="❌کاربر در بلاک لیست شما وجود نداشت", show_alert=True)
            await app.edit_message_reply_markup(call1.message.chat.id, call1.message.id, reply_markup=block_btn)

    async def Sendـanـanonymousـreply(m,unique_id, call_msg_id, answer, pv_answer_id):        #reply option

        user_info = cursor.execute(
                "SELECT sender_id, receiver_id, answer_id, unique_id FROM pv_msg WHERE unique_id=?", (unique_id,)      #check in database with username
                )
        for i in user_info:
            user_info = i

        if user_info[1] != int(m.from_user.id):
            try:
                keyboard_for_send_reply = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("🔁پاسخ", callback_data="send_reply_/"+ str(unique_id)+"_/"+str(answer.id))],
                        [InlineKeyboardButton("🔒بلاک", callback_data="block_/"+str(data.split("_/")[1]))]
                    ]
                )
                await app.send_message(int(user_info[1]), "📬پیام ناشناس داری عزیزم:")
                await app.copy_message(int(user_info[1]), int(user_info[0]), int(answer.id) ,reply_markup=keyboard_for_send_reply, reply_to_message_id=pv_answer_id)
                await app.send_message(answer.from_user.id, "✅**پیام با موفقیت ارسال شد!**\n **◉ [Robot Source](https://github.com/ho3jr/)**", reply_to_message_id= answer.id, disable_web_page_preview=True, reply_markup=keyboard_start)

            except KeyError:
                print(KeyError)
                await app.send_message(m.from_user.id,"❗️**هیچ پیامی دریافت نشد!**")
        else:
            await app.send_message(m.from_user.id,"**با خودت حرف میزنی؟**")

    data = call1.data
    if data == "learn_how_to_recive_id_group":
        await app.send_message(call1.message.chat.id, "🆔**آموزش پیدا کردن آیدی عددی** \nبرای پیدا کردن آیدی یک کاربر میتوانید از ربات زیر استفاده کنید:\n@username_to_id_bot.")

    try:
        if data.split("_/")[0] == "send_reply":
            unique_id = data.split("_/")[1]
            user_info = cursor.execute("SELECT ecrypt_text, answer_id, sender_id, receiver_id FROM pv_msg WHERE unique_id=?", (unique_id,))
            for i in user_info:
                user_info= i

            try:
                if await check_blocklist(int(user_info[2]), int(user_info[3])) if call1.from_user.id == int(user_info[2]) else await check_blocklist(int(user_info[3]), int(user_info[2])):
                    answer = await app.ask(int(call1.from_user.id), "⏰منتظر پاسخ شما هستیم", timeout=120, disable_web_page_preview=True, reply_markup=keyboard_cancel )

                    if answer:
                        if answer.text=="/cancel" or answer.text== "لغو کردن":
                            await app.send_message(answer.from_user.id, "**❗️کنسل شد!**", reply_markup= keyboard_start)

                        else:
                            unique_id = generate_unique_id()
                            db.execute(
                                """
                                INSERT INTO pv_msg(sender_name, receiver_name, unique_id, ecrypt_text, sender_id, receiver_id, answer_id, readed) VALUES(?,?,?,?,?,?,?,?)""",
                                (answer.from_user.first_name, "reply_person", unique_id, encrypt_aes(answer.text, key, iv), answer.from_user.id, user_info[2], answer.id, False)
                            )
                            db.commit()
                            await Sendـanـanonymousـreply(call1, unique_id, call1.message.id, answer, int(user_info[1]))
                else:
                    await app.send_message(call1.from_user.id,"**🤨شما بلاک شده اید!**", reply_to_message_id=call1.message.id)

            except KeyError:
                print(KeyError)
    except KeyError:
        pass


    first_part = data.split("/")[0]
    decrypted_text = ""

    if first_part == "delete_najva":
        unique_id = data.split("/")[1]
        cursor.execute("SELECT sender_id, chat_id, message_id FROM najvas_msg WHERE unique_id=?", (unique_id,))
        result = cursor.fetchone()
        if result:
            sender_id = int(result[0])
            chat_id = int(result[1])
            message_id = int(result[2])
            if sender_id == call1.from_user.id :
                cursor.execute("DELETE FROM najvas_msg WHERE unique_id =?",(unique_id,))
                db.commit()
                await app.edit_message_text(chat_id, message_id, "✅**نجوا با موفقیت حذف شد!**")
            else:
                await app.answer_callback_query(call1.id, "🚫شما فرستنده نجوا نیستید!", show_alert=True)

    elif first_part == "see_najva":       
        
        async def check_DBusers_for_send_Anonymous_msg(user_id, unique_id, firstname):
            try:
                if user_id:
                    try:
                        user_info = cursor.execute(
                        "SELECT unique_id, firstname FROM users WHERE id_tel=?", (user_id,)
                        )
                        for i in user_info:
                            user_info = i
                        url = "{}".format(str(lines[10])+str(user_info[0]) )
                        url = url.replace("\n","")
                    except:
                        pass
                    see_najva_btn = InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                                    InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)
                                ],
                                [
                                    InlineKeyboardButton("ارسال پیام ناشناس به {}".format(user_info[1]), url=url)
                                ]
                            ]
                        )
                    return see_najva_btn
                else:
                    see_najva_btn = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                                    InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)],
                                    
                                [
                                    InlineKeyboardButton("{} ربات را استارت نکرده است!".format(firstname), url=str(lines[10]).replace("\n","")) 
                                ]
                            ]
                        )
                    return see_najva_btn
            
            except:
                see_najva_btn = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                                InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)],
                                
                            [
                                InlineKeyboardButton("{} ربات را استارت نکرده است!".format(firstname), url=str(lines[10]).replace("\n",""))
                            ]
                        ]
                        )
                return see_najva_btn

        unique_id = data.split("/")[1]
        cursor.execute("SELECT ecrypt_text, sender_id, receiver_id_username, chat_id, message_id, receiver_name FROM najvas_msg WHERE unique_id=?", (unique_id,))
        result = cursor.fetchone()
        if result:
            ciphertext = result[0]
            sender_id = int(result[1])
            chat_id = int(result[3])
            receiver_id = result[2]
            receiver_id = str(receiver_id)
            receiver_id = "".join(receiver_id.split(" "))
            def can_convert_to_int(value):
                try:
                    int(value)
                    return True
                except (ValueError, TypeError):
                    return False
            if can_convert_to_int(receiver_id) == False:
                receiver_id =await app.get_chat_member(chat_id, str(receiver_id))
                receiver_id = receiver_id.user.id
            message_id = int(result[4])
            receiver_name =  str(result[5])
            decrypted_text = decrypt_aes(ciphertext, key)
            try:
                see_najva_btn = await check_DBusers_for_send_Anonymous_msg(receiver_id, unique_id, receiver_name)
                try:
                    if call1.from_user.id == sender_id or call1.from_user.username == receiver_id or call1.from_user.id == int(receiver_id):
                        await app.answer_callback_query(call1.id, text=decrypted_text, show_alert=True)
                        if call1.from_user.username == receiver_id or call1.from_user.id == int(receiver_id):
                            db.execute(
                                "UPDATE najvas_msg SET readed=? WHERE unique_id =? ",("TRUE" ,unique_id)
                                )
                            db.commit()
                            await app.edit_message_text(chat_id, message_id, "✅**کاربر [{}](tg://user?id={}) پیام شما را خواند!**".format(receiver_name, receiver_id), reply_markup=see_najva_btn)
                except:
                    pass
            except KeyError:
                await app.edit_message_text(int(call1.chat.id), call1.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)
            else:
                await app.answer_callback_query(call1.id, text="❌این پیام برای شما نیست عزیزم", show_alert=True)

    elif data == "see_help_najva":
        await app.answer_callback_query(call1.id, text= "برای ارسال نجوا بعد از اطمینان از ادمین بودن ربات در گروه به صورت زیر عمل کنید:\n۱-نام کاربری ربات\n۲-یک فاصله\n۳-نوشتن پیام\n۴-ریپلای بر شخص مورد نظر\n۵-کلیک بر روی دکمه ارسال", show_alert=True)

    elif data.split("_/")[0] == "block":
        await blocker(call1, data)
    
    elif data.split("_/")[0] == "unblock":
        await unblocker(call1, data)
    
    elif first_part == "send_message_to_users":
        if call1.from_user.id == int(lines[16]):
            result = await app.ask(call1.message.chat.id, "💬پیامی که قصد ارسال آن به کاربران دارید را ارسال کنید!\n زمان انتظار ۱ دقیقه⏰...")
            if result:
               cursor.execute("SELECT id_tel FROM users")
               for i in cursor.fetchall():
                    await app.send_message(int(i[0]), "این یک پیام از طرف ادمین ربات است:")
                    await app.copy_message(int(i[0]), result.chat.id, result.id)

            await app.send_message(result.chat.id, "**✅پیام شما با موفقیت به کاربران ربات ارسال شد!**")

    elif first_part == "reset_block_list":
        db.execute("UPDATE users SET blocklist=? WHERE id_tel =? ",("", call1.from_user.id))
        await app.answer_callback_query(call1.id, text="✅با موفقیت ریست شد!", show_alert=True)

@app.on_inline_query()
def inline_query_handler(client, inline_query):
    try:        #show result for najva
        send_btn = []
        query = inline_query.query
        text = query.split("@")[0]
        receiver_username = ""
        try:
            if query.split("@")[1] :
                receiver_username = query.split("@")[1] 
            else:
                pass
        except:
            pass

        unique_id = generate_unique_id()
        sender_id = inline_query.from_user.id
        cipher_text = encrypt_aes(text, key, iv)
        if not receiver_username:

            db.execute("""INSERT INTO najvas_msg(unique_id, ecrypt_text, sender_id, receiver_id_username, readed, chat_id, message_id, receiver_name) VALUES(?,?,?,?,?,?,?,?)""",(unique_id, cipher_text,sender_id, "None","FALSE",1, 1, "None"))
            db.commit()
            send_najva_btn = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id)],
                    [InlineKeyboardButton("❗️راهنمای استفاده از ربات", callback_data="see_help_najva")]
                ]
            )

            btns = [
                InlineQueryResultArticle(
                    id=1,
                    title="برای ارسال کلیک کنید",
                    description= "✅همه چیز به نظر درسته",
                    reply_markup=send_najva_btn,
                    input_message_content=InputTextMessageContent(
                        "✅**نجوا درحال ارسال است...!**"),
                    
                ),InlineQueryResultArticle(
                    id=2 ,
                    title="آموزش استفاده از بخش نجوا",
                    description= "پیام های در نجوا در دیتابیس ذخیره میشود اما بارمزنگاری پیشرفته AES! خیالتون راحت باشه",
                    input_message_content=InputTextMessageContent(
                        "برای ارسال نجوا بعد از اطمینان از ادمین بودن ربات در گروه به صورت زیر عمل کنید:\n۱-نام کاربری ربات\n۲-یک فاصله\n۳-نوشتن پیام\n۴-ریپلای بر شخص مورد نظر\n۵-کلیک بر روی دکمه ارسال\nمثال:\n@FoxanymousBOT message\n\nاستفاده از نجوا با یوزرنیم:\n@FoxanymousBOT message @username\n\n@FoxanymousBOT message @111111111",
                    )
                )
            ]


            app.answer_inline_query(inline_query.id, results=btns)
        else:
            db.execute("""INSERT INTO najvas_msg(unique_id, ecrypt_text, sender_id, receiver_id_username, readed, chat_id, message_id, receiver_name) VALUES(?,?,?,?,?,?,?,?)""",(unique_id, cipher_text,sender_id, receiver_username, "FALSE", 1, 1, "None"))
            db.commit()
            send_najva_btn = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id)],
                    [InlineKeyboardButton("❗️راهنمای استفاده از ربات", callback_data="see_help_najva")]
                ]
            )

            btns = [
                InlineQueryResultArticle(
                    id=1,
                    title="برای ارسال کلیک کنید",
                    description= "✅همه چیز به نظر درسته",
                    reply_markup=send_najva_btn,
                    input_message_content=InputTextMessageContent(
                        "✅**نجوا درحال ارسال است...!**"),
                    
                    
                ),InlineQueryResultArticle(
                    id=2 ,
                    title="آموزش استفاده از بخش نجوا",
                    description= "پیام های در نجوا در دیتابیس ذخیره میشود اما بارمزنگاری پیشرفته AES! خیالتون راحت باشه",
                    input_message_content=InputTextMessageContent(
                        "برای ارسال نجوا بعد از اطمینان از ادمین بودن ربات در گروه به صورت زیر عمل کنید:\n۱-نام کاربری ربات\n۲-یک فاصله\n۳-نوشتن پیام\n۴-ریپلای بر شخص مورد نظر\n۵-کلیک بر روی دکمه ارسال\nمثال:\n@FoxanymousBOT message\n\nاستفاده از نجوا با یوزرنیم:\n@FoxanymousBOT message @username\n\n@FoxanymousBOT message @111111111",
                    )
                )
            ]


            app.answer_inline_query(inline_query.id, results=btns)

    except:         #show result for najva
        najva_info = [
                InlineQueryResultArticle(
                    id=2 ,
                    title="آموزش استفاده از بخش نجوا",
                    description= "پیام های در نجوا در دیتابیس ذخیره میشود اما بارمزنگاری پیشرفته AES! خیالتون راحت باشه",
                    input_message_content=InputTextMessageContent(
                        "برای ارسال نجوا بعد از اطمینان از ادمین بودن ربات در گروه به صورت زیر عمل کنید:\n۱-نام کاربری ربات\n۲-یک فاصله\n۳-نوشتن پیام\n۴-ریپلای بر شخص مورد نظر\n۵-کلیک بر روی دکمه ارسال\nمثال:\n@FoxanymousBOT message\n\nاستفاده از نجوا با یوزرنیم:\n@FoxanymousBOT message @username\n\n@FoxanymousBOT message @111111111",
                    )
                )
            ]

        app.answer_inline_query(inline_query.id, najva_info)


@app.on_message(filters.group)        #receive msg in Group
async def GROUP_main(c: Client, m: Message):
    async def check_DBusers_for_send_Anonymous_msg(user_id, unique_id, firstname):
        try:
            if user_id:
                try:
                    user_info = cursor.execute(
                    "SELECT unique_id, firstname FROM users WHERE id_tel=?", (user_id,)
                    )
                    for i in user_info:
                        user_info = i
                    url = "{}".format(str(lines[10])+str(user_info[0]) )
                    url = url.replace("\n","")
                except:
                    pass
                see_najva_btn = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                                InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)
                            ],
                            [
                                InlineKeyboardButton("ارسال پیام ناشناس به {}".format(user_info[1]), url=url)
                            ]
                        ]
                    )
                return see_najva_btn
            else:
                see_najva_btn = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                                InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)],
                                
                            [
                                InlineKeyboardButton("{} ربات را استارت نکرده است!".format(firstname), url=str(lines[10]).replace("\n","")) 
                            ]
                        ]
                    )
                return see_najva_btn
        
        except:
            see_najva_btn = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                            InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)],
                            
                        [
                            InlineKeyboardButton("{} ربات را استارت نکرده است!".format(firstname), url=str(lines[10]).replace("\n",""))
                        ]
                    ]
                    )
            return see_najva_btn


    if m.text == "id" or m.text =="Id" or m.text== "ID" and m.reply_to_message.from_user.id:
        await app.send_message(m.chat.id,"📱آيدی کاربر: `{}`".format(m.reply_to_message.from_user.id),reply_to_message_id=m.id)
        pass
    
    try:
        try:
            if m.reply_to_message.from_user.id and m.via_bot.id == int(lines[13]):
                unique_id = m.reply_markup.inline_keyboard[0][0].callback_data
                unique_id = unique_id.split("/")[1]
                db.execute(
                    "UPDATE najvas_msg SET receiver_id_username=?, chat_id=?, message_id=?, receiver_name=? WHERE unique_id =? ",(m.reply_to_message.from_user.id, m.chat.id, m.id, m.reply_to_message.from_user.first_name ,unique_id)
                    )
                db.commit()
                see_najva_btn = await check_DBusers_for_send_Anonymous_msg(m.reply_to_message.from_user.id, unique_id, m.reply_to_message.from_user.first_name)

                await app.edit_message_text(m.chat.id, m.id, "📬یک **نجوا** برای [{}](tg://user?id={})".format(m.reply_to_message.from_user.first_name, int(m.reply_to_message.from_user.id)),c= see_najva_btn)

            elif m.via_bot.id == int(lines[13]):
                unique_id = m.reply_markup.inline_keyboard[0][0].callback_data
                unique_id = unique_id.split("/")[1]
                try:
                    cursor.execute("SELECT receiver_id_username FROM najvas_msg WHERE unique_id=?", (unique_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        see_najva_btn = InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton("👁مشاهده نجوا", callback_data="see_najva/" + unique_id),
                                    InlineKeyboardButton("🚫حذف نجوا", callback_data="delete_najva/" + unique_id)],
                                ]
                            )
                        user = ""
                        isdigit = False
                        isalpha = False
                        if result[0].isdigit() == True:
                            user = await app.get_chat_member(m.chat.id, int(result[0]))
                            isdigit = True
                        elif result[0].isalnum()== True:
                            user = await app.get_chat_member(m.chat.id, str(result[0]))
                            isalpha = True
                        else:
                            await app.edit_message_text(m.chat.id, m.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)

                        if isalpha == True and isdigit == False:
                            await app.edit_message_text(m.chat.id, m.id,  "📬یک **نجوا** برای [{}](tg://user?id={})\n@{}".format(user.user.first_name, int(user.user.id), user.user.username), reply_markup= see_najva_btn)
                        elif isdigit == True and isalpha == False:
                            await app.edit_message_text(m.chat.id, m.id, "📬یک **نجوا** برای [{}](tg://user?id={})".format(user.user.first_name, int(user.user.id)), reply_markup= see_najva_btn)
                        else:
                            await app.edit_message_text(m.chat.id, m.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)
                    else:
                        await app.edit_message_text(m.chat.id, m.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)
                except KeyError:
                    pass
        except KeyError:
            pass
    except:
        if m.text == "برای ارسال نجوا بعد از اطمینان از ادمین بودن ربات در گروه به صورت زیر عمل کنید:\n۱-نام کاربری ربات\n۲-یک فاصله\n۳-نوشتن پیام\n۴-ریپلای بر شخص مورد نظر\n۵-کلیک بر روی دکمه ارسال\nمثال:\n@FoxanymousBOT message\n\nاستفاده از نجوا با یوزرنیم:\n@FoxanymousBOT message @username\n@FoxanymousBOT message @111111111":
            pass
        else:
            try:
                unique_id = m.reply_markup.inline_keyboard[0][0].callback_data
                unique_id = unique_id.split("/")[1]
                cursor.execute("SELECT receiver_id_username FROM najvas_msg WHERE unique_id=?", (unique_id,))
                result = cursor.fetchone()

                user = await app.get_chat_member(int(m.chat.id), result[0])
                receiver_name = user.user.first_name
                db.execute(
                    "UPDATE najvas_msg SET chat_id=?, message_id=?, receiver_name=? WHERE unique_id=?",(m.chat.id, m.id, receiver_name ,unique_id)
                    )
                db.commit()
                
                if result:
                    user = ""
                    isdigit = False
                    isalpha = False
                    result = str(result[0])
                    if result.isdigit() == True:
                        user = await app.get_chat_member(m.chat.id, int(result))
                        isdigit = True
                    elif result.isalnum()== True:
                        user = await app.get_chat_member(m.chat.id, str(result))
                        isalpha = True
                    else:
                        await app.edit_message_text(m.chat.id, m.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)

                    see_najva_btn = await check_DBusers_for_send_Anonymous_msg(user.user.id, unique_id, user.user.first_name)

                    if isalpha == True and isdigit == False:
                        await app.edit_message_text(m.chat.id, m.id,  "📬یک **نجوا** برای [{}](tg://user?id={})\n@{}".format(user.user.first_name, int(user.user.id), user.user.username), reply_markup= see_najva_btn)
                    elif isdigit == True and isalpha == False:
                        await app.edit_message_text(m.chat.id, m.id, "📬یک **نجوا** برای [{}](tg://user?id={})".format(user.user.first_name, int(user.user.id)), reply_markup= see_najva_btn)
                    else:
                        await app.edit_message_text(m.chat.id, m.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)
                else:
                    await app.edit_message_text(m.chat.id, m.id, "❗️یک خطا رخ داد. **آموزش ارسال نجوا را ببینید**", reply_markup= see_help_najva_btn)
            except:
                pass

INFO.close()
app.run()