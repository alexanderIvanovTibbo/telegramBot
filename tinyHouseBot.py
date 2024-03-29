#!/usr/bin/env python
# pylint: disable=C0116
# -*- coding: utf-8 -*-
import logging
import datetime
import os
import subprocess
import ffmpeg
import time
import binascii
import psutil
import shutil
import RPi.GPIO as GPIO
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineQueryResultCachedPhoto, InputMediaPhoto, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)  # Turn off warnings output
GPIO.setup(22, GPIO.OUT) # Set pin #22 to RELAY output
GPIO.output(22,True)
GPIO.setup(21, GPIO.OUT) # Set pin #21 to MOSFET output
GPIO.setup(19, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)  # Set pin #19 to RELAY input
powerStatus = False

# Enable logging
logging.basicConfig(
#     filename='app.log',
#     filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
MAIN, MEDIA, PHOTO, VIDEO, RASP, MODEM, FILES, ALARM = range(8)

mainFolder = "/home/pi/webcam/usb0/teleBotData"
scriptFolder = "/home/pi/webcam/telegramBot/"
#scriptFolder = ""
users = [882010412,1275463615]
ip_cams=['192.168.0.10','192.168.0.20']
prev_msg = ""

def start(update: Update, _: CallbackContext) -> int:
  """Send message on `/start`."""
  """ Get user that sent /start and log his name"""
  user = update.message.from_user
  chat_id = update.message.chat_id
  logger.info("User %s(id:%s) started the conversation.", user.first_name,user.id)
  if user.id not in users:
      update.message.reply_text("Не авторизованый пользователь. Обратитесь к администратору Telegram канала. Ваш ID пользователя: %s" % user.id)
  else :
    reply_keyboard =\
    [
        ["Получить фото/видео"],
        ["Информация о 3G модеме"],
        ["Информация о системе"],
        ["Информация о тревогах"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.reply_text("Главное меню", reply_markup=reply_markup)
    return MAIN


def start_over(update: Update, _: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Получить фото/видео"],
        ["Информация о 3G модеме"],
        ["Информация о системе"],
        ["Информация о тревогах"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text('Вернулись в главное меню:', reply_markup=reply_markup)
    return MAIN



def media_main(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Получить фото"],
        ["Получить видео"],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(text="Получить фото/видео", reply_markup=reply_markup)
    return MEDIA

def photo_main(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Фото из дома"],
        ["Фото участка"],
        ['Фото со всех камер'],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(text="Какие фото хотите получить: ", reply_markup=reply_markup)
    return PHOTO

def video_main(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Видео из дома"],
        ["Видео участка"],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(text="Какое видео хотите получить: ", reply_markup=reply_markup)
    return VIDEO

def modem_main(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat_id
    reply_keyboard = \
        [
            ["Баланс SIM-карты"],
            ["< Назад"],
        ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(text="Информация о 3G модеме", reply_markup=reply_markup)
    return MODEM


def rasp_main(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Температура CPU"],
        ["Информация о HDD"],
        ["Время работы Telegram-бота"],
        ["Получить логи Telegram-бота"],
        ["Информация о источнике питания"],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(text="Информация о системе", reply_markup=reply_markup)
    return RASP

def alarm_main(update: Update, _: CallbackContext) -> int:
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Статус тревог"],
        ["Поставить на охрану"],
        ["Снять с охраны"],
        ["Отключить все тревоги"],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    update.message.reply_text(text="Информация о тревогах", reply_markup=reply_markup)
    return ALARM

def get_balance(update: Update, _: CallbackContext) -> int:
  update.message.reply_text(text=f'Идет загрузка...')
  sessionID_url='https://lk.megafon.ru/remainders/'
  webpage=subprocess.check_output("w3m -M -dump -no-graph '%s'" % sessionID_url, shell= True).decode('UTF-8')
  index1=webpage.find("Интернет")
  index2=int(webpage.find('В пути'))
  balance=webpage[index1:(index2-2)]
  balance=balance.replace('\n\n','\n')
  update.message.reply_text(text=balance)
  return MODEM

def get_durationtime(update: Update, _: CallbackContext) -> int:
  pid = os.getpid()
  etime = subprocess.check_output("ps -p %s -o etime=" % pid, shell=True).decode('UTF-8')
  update.message.reply_text(text="Время работы:%s" % etime)
  return RASP

def get_disk_usage(update: Update, _: CallbackContext) -> int:
  hdd = psutil.disk_usage("/home/pi/webcam/usb0")
  strText = "Всего: %s \nЗанято: %s \nСвободно: %s " % (getsize(hdd.total),getsize(hdd.used),getsize(hdd.free))
  update.message.reply_text(text=strText)
  return RASP

def get_temp(update: Update, _: CallbackContext) -> int:
  temp = os.popen('vcgencmd measure_temp').readline()
  update.message.reply_text(text="Температура процессора: %s" % temp.replace('temp=',''))
  return RASP

def get_log(update: Update, _: CallbackContext) -> int:
  log_file = open('app.log')
  update.message.reply_document(document=log_file)
  return RASP

def get_powerstatus(update: Update, _: CallbackContext) -> int:
  powerSt = check_power(True)
  update.message.reply_text(text=powerSt)
  return RASP

def get_video(update: Update, _: CallbackContext) -> None:
         if update.message.text == 'Видео из дома':
             ip_camera = ip_cams[0]
         else:
             ip_camera = ip_cams[1]
         if check_ping(ip_camera)==0:
            update.message.reply_text(text=f'Идет загрузка...')
            videoDir = get_folder(1)
            flag = stream_video(videoDir,ip_camera)
            if flag:
                video = open(videoDir, 'rb')
                update.message.reply_video(video=video)
            else:
               update.message.reply_text(text=f'Файл не найден')
         else:
               update.message.reply_text(text= ip_camera + ' нет соединения')
         return VIDEO

def get_photo(update: Update, _: CallbackContext) -> None:
  if update.message.text == 'Фото со всех камер':
      update.message.reply_text(text='Идет загрузка...')
      photos = get_photoGroup()
      for photo in photos:
          if type(photo) is not str:
              update.message.reply_photo(photo=photo)
          else:
              update.message.reply_text(text=photo)
  else:
      if update.message.text == 'Фото из дома':
          ip_camera = ip_cams[0]
      else:
          ip_camera = ip_cams[1]
      if check_ping(ip_camera)==0:
          update.message.reply_text(text='Идет загрузка...')
          fotoDir=get_folder(0)
          flag=snapshot(fotoDir,ip_camera)
          if flag:
               photo = open(fotoDir, 'rb')
               update.message.reply_photo(photo=photo)
          else:
             update.message.reply_text(text='Файл не найден')
      else:
             update.message.reply_text(text=ip_camera + ' нет соединения')
  return PHOTO

def get_photoGroup():
    results = list()
    for ip_cam in ip_cams:
      if check_ping(ip_cam)==0:
          i = 0
          while i < 2:
             fotoDir=get_folder(0)
             flag=snapshot(fotoDir,ip_cam)
             if flag:
                results.append(open(fotoDir, 'rb'))
                i += 1
                time.sleep(2)
             else:
               text='Файл не найден'
               break
          if not results:
             results.append(text)
      else:
           results.append(ip_cam + ' Не подключена')
    return results

def getsize(bytes):
   return str((bytes/1024/1000))+" MB"

def get_folder(num):
   dirDate = datetime.datetime.today().strftime("%y-%m-%d")
   fileDate = datetime.datetime.now().strftime("%H-%M-%S")
   parent_dir = os.path.join(mainFolder,"req")
   path = os.path.join(parent_dir,dirDate)
   if not  os.path.exists(path):
       os.mkdir(path,0o777)
   if num == 0:
        fotoDir ='%s/%s.jpg' %  (path, fileDate)
        return fotoDir
   elif num == 1:
        count = 1
        flag = True
        while  flag:
                fileName = "%02d.mp4" % count
                videoDir = os.path.join(path,fileName)
                flag = os.path.isfile(videoDir)
                count+=1
        return videoDir
   else:
        return path

def check_power(flag):
    global powerStatus
    text = None
    buttonIn = GPIO.input(19)
    if buttonIn:
        if powerStatus:
           text="Основное питание восстановлено"
           powerStatus = False
        if flag:
           text="Основной источник питания"
    else:
        if not powerStatus:
           text="Переход на резервный источник питания"
           powerStatus = True
        if flag:
           text="Резервный источник питания"

    return text

def check_ping(camara_ip):
   resp = os.system("ping -c 1 " +camara_ip)
   return resp

def snapshot(folder,camera_ip):
   subprocess.call("ffmpeg -rtsp_transport tcp -i 'rtsp://%s/user=admin_password=123_channel=1_stream=0.sdp' -vframes 1 -r 1 %s" % (camera_ip,folder), shell = True)
   return os.path.isfile(folder)

def stream_video(videoDir,camera_ip):
  folder = get_folder(2)
  # videoDir = get_folder(1)
  subprocess.call("ffmpeg -rtsp_transport tcp -i 'rtsp://%s/user=admin_password=123_channel=1_stream=0.sdp' -f image2 -threads 1 -t 30 -async 1 -r 1/0.5 -vcodec mjpeg %s/img%s.jpg" % (camera_ip, folder,"%03d"), shell = True)
  time.sleep(1)
  subprocess.call('ffmpeg -f image2 -r 1/0.1 -i %s/img%s.jpg -preset slow %s' % (folder,"%03d", videoDir), shell = True)
  subprocess.call('rm %s/img*.jpg' % folder, shell = True)
  time.sleep(5)
  return os.path.isfile(videoDir)

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    global prev_msg
    job = context.job
    powerSt = check_power(False)
    if powerSt is not None:
        context.bot.send_message(chat_id=str(context.job.name), text=powerSt)
    with open(scriptFolder+"alarmLogger.txt","r") as openfile:
        text_msg = openfile.read()
        if not str(prev_msg) in text_msg:
           context.bot.send_message(chat_id=str(context.job.name), text=str(text_msg))
           photos = get_photoGroup()
           for photo in photos:
               if type(photo) is not str:
                  context.bot.send_photo(
                  chat_id=str(context.job.name),
                  photo=photo
                  )
               else:
                  context.bot.send_message(job.context, text=photo)
    prev_msg = str(text_msg)
    openfile.close()

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def set_timer(update: Update, context: CallbackContext) -> int:
    try:
        match_id = False
        chat_id = update.message.chat_id
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, 10, context=chat_id, name=str(chat_id))
        update.message.reply_text(text="Тревога включена ("+f'{chat_id}'+")")
        text_file = open(scriptFolder + "jobLogger.txt", "r")
        lines = text_file.readlines()
        for line in lines:
            if str(chat_id) in str(line.strip()):
                match_id = True
        text_file.close()
        if not match_id:
            text_file = open('jobLogger.txt', 'a')
            text_file.write(str(chat_id)+'\n')
            text_file.close()

    except (IndexError, ValueError):
        update.message.reply_text(text='Ошибка')
    return ALARM

def restart_job(context: CallbackContext):
        """Restart a job to the queue."""
        if not os.stat(scriptFolder+"jobLogger.txt").st_size == 0:
           text_file = open(scriptFolder+"jobLogger.txt", "r")
           lines = text_file.readlines()
           for line in lines:
               context.job_queue.run_repeating(alarm, 10, context=str(line.strip()), name=str(line.strip()))
           text_file.close()

def check_alarm(update: Update, context: CallbackContext) -> int:
    """Check active jobs"""
    current_jobs = context.job_queue.jobs()
    if not current_jobs:
        update.message.reply_text(text="Все тревоги отключены")
    for job in current_jobs:
        update.message.reply_text(text="Тревога включена ("+f'{job.name}'+")")
    return ALARM

def unset_help(update: Update, _: CallbackContext) -> None:
    reply_keyboard =\
    [
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    update.message.reply_text('Отправь /unset <Имя тревоги> для отключения тревоги', reply_markup=reply_markup)
    return ALARM

def unset(update: Update, context: CallbackContext) -> int:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    reply_keyboard =\
    [
        ["Статус тревог"],
        ["Поставить на охрану"],
        ["Снять с охраны"],
        ["Отключить все тревоги"],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    try:
        alarm_id = str(context.args[0])
        job_removed = remove_job_if_exists(alarm_id, context)
        text = 'Тревога отключена' if job_removed else 'Все тревоги отключены'
        update.message.reply_text(text=text, reply_markup=reply_markup)
        with open("jobLogger.txt", "r") as file:
            lines = file.readlines()
        with open("jobLogger.txt", "w") as file:
            for line in lines:
                if line.strip("\n") != alarm_id:
                    file.write(line)
        file.close()
    except (IndexError, ValueError):
        update.message.reply_text('Синтаксис: /unset <Имя тревоги>', reply_markup=reply_markup)
    return ALARM

def unset_all(update: Update, context: CallbackContext) -> int:
    """Remove the job if the user changed their mind."""
    reply_keyboard =\
    [
        ["Статус тревог"],
        ["Поставить на охрану"],
        ["Снять с охраны"],
        ["Отключить все тревоги"],
        ["< Назад"],
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)
    current_jobs = context.job_queue.jobs()
    if not current_jobs:
        text="Тревоги отсутствуют"
    for job in current_jobs:
        text="Тревога отключена ("+f'{job.name}'+")"
        update.message.reply_text(text=text,reply_markup=reply_markup)
        job_removed = remove_job_if_exists(str(job.name), context)
    with open("jobLogger.txt", "w") as file:
            file.write('')
    file.close()
    return ALARM

def prove_unset_all(update: Update, context: CallbackContext) -> int:
    reply_keyboard =\
    [
        ['Да','Нет']
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard,resize_keyboard =True, one_time_keyboard=True)

    current_jobs = context.job_queue.jobs()
    if not current_jobs:
        update.message.reply_text("Тревоги отсутствуют")
    else:
        update.message.reply_text('Вы действительно хотите отключить все тревоги', reply_markup=reply_markup)
    return ALARM

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("1312160633:AAEbyukZeVW-RAOa7br4hAFNcLSqAwPZMNM", request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    j = updater.job_queue
    j.run_once(restart_job,1)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [
                MessageHandler(Filters.text('Получить фото/видео'),media_main),
                MessageHandler(Filters.text('Информация о 3G модеме'),modem_main),
                MessageHandler(Filters.text('Информация о системе'),rasp_main),
                MessageHandler(Filters.text('Информация о тревогах'),alarm_main)
            ],
            MEDIA: [
                MessageHandler(Filters.text('Получить фото'),photo_main),
                MessageHandler(Filters.text('Получить видео'),video_main)
            ],
            PHOTO: [
                MessageHandler(Filters.text('Фото из дома'),get_photo),
                MessageHandler(Filters.text('Фото участка'),get_photo),
                MessageHandler(Filters.text('Фото со всех камер'),get_photo)
            ],
            VIDEO: [
                MessageHandler(Filters.text('Видео из дома'),get_video),
                MessageHandler(Filters.text('Видео участка'),get_video),
            ],
            MODEM: [
                MessageHandler(Filters.text('Баланс SIM-карты'),get_balance)
            ],

            RASP: [
                MessageHandler(Filters.text('Температура CPU'),get_temp),
                MessageHandler(Filters.text('Информация о HDD'),get_disk_usage),
                MessageHandler(Filters.text('Время работы Telegram-бота'),get_durationtime),
                MessageHandler(Filters.text('Получить логи Telegram-бота'),get_log),
                MessageHandler(Filters.text('Информация о источнике питания'),get_powerstatus)
            ],

            ALARM: [
                MessageHandler(Filters.text('Статус тревог'),check_alarm),
                MessageHandler(Filters.text('Поставить на охрану'),set_timer),
                MessageHandler(Filters.text('Снять с охраны'),unset_help),
                MessageHandler(Filters.text('Отключить все тревоги'),prove_unset_all),
                MessageHandler(Filters.text('Да'),unset_all),
                MessageHandler(Filters.text('Нет'),start_over),
            ],
        },
        fallbacks=[MessageHandler(Filters.text('< Назад'), start_over)],
    )
    # Add ConversationHandler to dispatcher that will be used for handling
    # updates
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("photo", get_photo))
    dispatcher.add_handler(CommandHandler("alarm", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
