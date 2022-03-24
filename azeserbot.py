from genericpath import exists
from shutil import move
import telebot
from time import sleep
import os
import glob
bot = telebot.TeleBot("HIDDEN", parse_mode=None) 

sentences = ['Qonşu evin yanında danışır', 'Onlar qapının ağzında dayanırlar']
emotions = ['xoşbəxt', "neytral", "qəmgin", "qəzəbli"]
total = {(0,0),(0,1),(0, 2),(0,3),(1,0),(1,1),(1, 2),(1,3)}
exist = set()
isent = 0
iemo = 0

@bot.message_handler(commands=['start'])
def start_message(message): 
    global isent, iemo, exist
    exist.clear()
    isent = 0
    iemo = 0
    username = 'undefined'
    user_id = message.from_user.id
    try:
        username= message.chat.username
    except:
        pass
    print(f"{username} initiated bot!")
    bot.send_message(message.chat.id,
        """Salam! Azərbaycan nitqinin emosiyaların tanınması proyektinə xoş gəlmisiniz!\n
Sizə cümlə və emosiya veriləcək və həmin emosiyaya əsasən cümləni oxuyub səsini yazmağınızı xahiş edirəm.\n
Başlamaq üçün /continue komandasından istifadə edin.
        """)
    sleep(0.5)
    help(message)

@bot.message_handler(commands=['restart'])
def restart_message(message): 
    confirm = bot.send_message(message.chat.id,
            """Bütün səs yazılmaları silməsini təsdiqləyirsinizsə 'y' yazın, əks halda davam edin.""")
    bot.register_next_step_handler(confirm, restart2)
    
def restart2(message):
    if message.text.lower() == 'y':
        global isent, iemo, exist
        username = 'undefined'
        user_id = message.from_user.id
        try:
            username= message.chat.username
        except:
            pass
        path = f"./voices/{user_id}_{username}"
        files = os.listdir(path)
        for f in files:
            os.remove(f"{path}/{f}")
        isent = 0
        iemo = 0
        exist.clear()
        res = bot.send_message(message.chat.id,
            """Bütün yazılmalar silindi və yenidən başlayırıq!""")
        sent_emo(res)
    else:
        move_continue(message)


def sent_emo(message):
    sent = sentences[isent]
    emo = emotions[iemo]
    new = bot.send_message(message.chat.id, f"İndi '{sent}' cümləsini '{emo}' emosiyası ilə oxuyun.")
    bot.register_next_step_handler(new, voice_processing)

@bot.message_handler(commands=['redo'])
def redo(message):
    global isent, iemo
    isent = isent-1 if isent>0 else 0
    iemo = iemo if iemo>0 else 0
    sent = sentences[isent]
    emo = emotions[iemo]
    new2 = bot.send_message(message.chat.id, f"Yenidən dənəyin: '{sent}' cümləsini '{emo}' emosiyası ilə oxuyun.")
    bot.register_next_step_handler(new2, voice_processing)

@bot.message_handler(commands=['change'])
def change(message):
    global isent, iemo
    username = 'undefined'
    user_id = message.from_user.id
    try:
        username= message.chat.username
    except:
        pass
    path = f"./voices/{user_id}_{username}"

    if not os.path.exists(path) or len(os.listdir(f"{path}") ) == 0:
        bot.send_message(message.chat.id, 'Siz əvvəl səs yazdırmadınız! Sıfırdan başlayırıq!')
        sent_emo(message)
    else:
        change = bot.send_message(message.chat.id,"""Əgər xüsusi bir səsi dəyişdirmək istəyirsinizsə həmin kombinasiyanın nömrələrini boş aralıqla yazın:\n
Cümlələr:
0 - Qonşu evin yanında danışır
1 - Onlar qapının ağzında dayanırlar

Emosiyalar:
0 - xoşbəxt
1 - neytral
2 - qəmgin
3 - qəzəbli

Məsələn:
'Qonşu evin yanında danışır' cümləni 'qəmgin' emosiyası ilə yenidən yazmaq istəyirsinizsə '0 2' yazın.
""")
        bot.register_next_step_handler(change, change2)

def change2(message):
    global isent, iemo
    username = 'undefined'
    user_id = message.from_user.id
    try:
        username= message.chat.username
    except:
        pass
    path = f"./voices/{user_id}_{username}"

    filename = message.text.split()
    if int(filename[0]) > 1 or int(filename[1]) > 3:
        bot.send_message(message.chat.id, 'Kombinasiya səhvdir! Yenidən dənəyək!')
        change(message)
    elif int(filename[0]) <= 1 or int(filename[1]) <= 3:
        check_path = f"{path}/{user_id}_{username}_s{filename[0]}_e{filename[1]}.wav"
        if os.path.exists(check_path):
            isent = int(filename[0])
            iemo = int(filename[1])
            sent = sentences[isent]
            emo = emotions[iemo]
            new4 = bot.send_message(message.chat.id, f"Qeyd etdiyiniz kombinasiyanı yenidən yazaq!\n'{sent}' cümləsini '{emo}' emosiyası ilə oxuyun.")
            bot.register_next_step_handler(new4, voice_processing)
        else:
            bot.send_message(message.chat.id, 'Kombinasiya səhvdir! Bu səs yazılmamışdır. Yenidən dənəyək!')
            change(message)

    else:
        bot.send_message(message.chat.id, 'Kombinasiya səhvdir! Yenidən dənəyək!')
        change(message)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, """Kömək edə biləcək komandalar:\n
/change - hər hansı bir səsi yenidən yazdırmaq istəyirsinizsə,\n
/redo - əvvəlki səsi yenidən yazdırmaq istəyirsinizsə,\n
/restart - başdan başlamaq istəyirsinizsə (bu bütün səs yazılmaları siləcək),\n
/continue - dayandığınız yerdən davam etmək istəyirsinizsə,\n
/help - komandaların siyahısını göstərmək üçün.

DİQQƏT: Bəzən bot komandaları ilk dəfədən qeyd etmir, bu halda yenidən eyni komandanı yazmağınız xahiş olunur.
    """)

@bot.message_handler(commands=['continue'])
def move_continue(message):
    global isent, iemo
    username = 'undefined'
    user_id = message.from_user.id
    try:
        username= message.chat.username
    except:
        pass
    path = f"./voices/{user_id}_{username}"
    if (not os.path.exists(path)) or (len(os.listdir(f"{path}")) == 0):
        bot.send_message(message.chat.id, 'Siz əvvəl səs yazdırmadınız! Sıfırdan başlayırıq!')
        sent_emo(message)
    else:
        files = os.listdir(path)
        file = files[len(files)-1]
        filename = os.path.basename(file).split('_')
        if int(filename[2][1]) == 1 and int(filename[3][1]) == 3:
            bot.send_message(message.chat.id, 'Siz bütün səsləri yazdırmısınız! Əgər yenidən başlamaq istəyirsinizsə, /restart komandasını yazın.')
        elif int(filename[2][1]) == 0 and int(filename[3][1]) == 3:
            isent = int(filename[2][1])+1
            iemo = 0
            new3 = bot.send_message(message.chat.id, 'Davam edək!')
            sent_emo(new3)
        else:
            iemo = int(filename[3][1])+1
            new3 = bot.send_message(message.chat.id, 'Davam edək!')
            sent_emo(new3)
      

@bot.message_handler(content_types=['voice', 'text'])
def voice_processing(message):
    global isent, iemo, exist
    username = 'undefined'
    user_id = message.from_user.id
    try:
        username= message.chat.username
    except:
        pass
    
    if not os.path.exists("./voices"):
        os.mkdir("./voices")

    if message.content_type =='voice':
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f"./voices/{user_id}_{username}"
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        with open(f"{file_path}/{user_id}_{username}_s{isent}_e{iemo}.wav", 'wb') as new_file:
            new_file.write(downloaded_file)


        for file in os.listdir(file_path):
            filename = os.path.basename(file).split('_')
            exist.add((int(filename[2][1]), int(filename[3][1])))
        next_combo = sorted(list(total.difference(exist)))
        if len(next_combo)>0:
            isent = next_combo[0][0]
            iemo = next_combo[0][1]
            new3 = bot.send_message(message.chat.id, 'Səs yazıldı!')
            sent_emo(new3)

        else:
            bot.send_message(message.chat.id, 'Səs yazma bitdi. Təşəkkürlər!')
            bot.send_sticker(message.chat.id, 'CAACAgEAAxkBAAM2Yjut8XZSY-oBnMQAAXtDE-05wOd3AAJrAQACUSkNObYurhORVpOoIwQ')
    elif message.content_type not in ['voice', 'text']:
        move_continue(message)
bot.infinity_polling(timeout=10, long_polling_timeout = 5)