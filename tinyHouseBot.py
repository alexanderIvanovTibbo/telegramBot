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
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineQueryResultCachedPhoto, InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
MAIN, MEDIA, RASP, MODEM, FILES, ALARM = range(6)
# Callback data
ONE, TWO, THREE, FOUR, FIVE, BACK = range(6)

mainFolder = "/home/pi/webcam/usb0/teleBotData"
users = [882010412,1275463615]
ipCam="192.168.0.10"
prev_msg = ""

def start(update: Update, _: CallbackContext) -> int:
  """Send message on `/start`."""
  # Get user that sent /start and log his name
  user = update.message.from_user
  global chat_id
  chat_id = update.message.chat_id
  logger.info("User %s(id:%s) started the conversation.", user.first_name,user.id)
  if user.id not in users:
      update.message.reply_text("Not authorized ID. Contact with chat admin. Your ID: %s" % user.id)
  else :
    keyboard = [
        [
            InlineKeyboardButton("Get Photo/Video", callback_data=str(ONE)),
            InlineKeyboardButton("3G Modem Info", callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton("Rasp Info", callback_data=str(THREE)),
            InlineKeyboardButton("Alarm", callback_data=str(FIVE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Start handler, Choose a route", reply_markup=reply_markup)
    return MAIN


def start_over(update: Update, _: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Get Photo/Video", callback_data=str(ONE)),
            InlineKeyboardButton("3G Modem Info", callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton("Rasp Info", callback_data=str(THREE)),
            InlineKeyboardButton("Alarm", callback_data=str(FIVE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text('Please choose:', reply_markup=reply_markup)
    return MAIN



def media_main(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="Send /photo to get photo")
    return MEDIA


def modem_main(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Check SIM Balance", callback_data=str(ONE)),
        ],
        [   InlineKeyboardButton("Back", callback_data=str(BACK)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="3G modem Info. Please choose:", reply_markup=reply_markup
    )
    return MODEM


def rasp_main(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Check CPU Temp", callback_data=str(ONE)),
        ],
        [
            InlineKeyboardButton("Check Disk Usage", callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton("Bot Duration Time", callback_data=str(THREE)),
        ],
        [
            InlineKeyboardButton("Back", callback_data=str(BACK)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Raspberry Info. Please choose:", reply_markup=reply_markup
    )
    return RASP

def alarm_main(update: Update, _: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Alarm Status", callback_data=str(ONE)),
        ],
        [
            InlineKeyboardButton("Set Alarm", callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton("Unset Alarm", callback_data=str(THREE)),
        ],
        [
            InlineKeyboardButton("Back", callback_data=str(BACK)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Alarm settings. Please choose:", reply_markup=reply_markup
    )
    return ALARM

def get_balance(update: Update, _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  sessionID_url='https://lk.megafon.ru/remainders/'
  webpage=subprocess.check_output("w3m -M -dump -no-graph '%s'" % sessionID_url, shell= True).decode('UTF-8')
  index1=webpage.find("Интернет")
  index2=int(webpage.find('В пути'))
  balance=webpage[index1:(index2-2)]
  balance=balance.replace('\n\n','\n')
  keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(TWO)),
        ],
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text=balance, reply_markup=reply_markup)
  return MAIN

def get_durationtime(update: Update, _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  pid = os.getpid()
  etime = subprocess.check_output("ps -p %s -o etime=" % pid, shell=True).decode('UTF-8')
  keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(THREE)),
        ],
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text="Bot duration time:%s" % etime, reply_markup=reply_markup)
  return MAIN

def get_disk_usage(update: Update, _: CallbackContext) -> int:
  keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(THREE)),
        ],
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  query = update.callback_query
  query.answer()
  hdd = psutil.disk_usage("/home/pi/webcam/usb0")
  strText = "Total: %s \nUsed: %s \nFree: %s " % (getsize(hdd.total),getsize(hdd.used),getsize(hdd.free))
  query.edit_message_text(text=strText, reply_markup=reply_markup)
  return MAIN

def get_temp(update: Update, _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  temp = os.popen('vcgencmd measure_temp').readline()
  keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(THREE)),
        ],
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(text="Core temperature: %s" % temp.replace('temp=',''), reply_markup=reply_markup)
  return MAIN

#def get_video(update: Update, _: CallbackContext) -> None:
#  if check_ping()==0:
#     update.message.reply_text(text=f'Wait a few minutes')
#     videoDir = get_folder(1)
#     flag = stream_video()
#     if flag:
#         video = open(videoDir, 'rb')
#         update.message.bot.send_video(chat_id=chat_id, video=video)
#     else:
#        update.message.reply_text(text=f'Video not found')
#  else:
#        update.message.reply_text(text=f'IP cam not connected')

def get_photo(update: Update, _: CallbackContext) -> None:
  keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(ONE)),
        ],
    ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  if check_ping()==0:
      update.message.reply_text(text='Wait a few minutes')
      fotoDir=get_folder(0)
      flag=snapshot(fotoDir)
      if flag:
           photo = open(fotoDir, 'rb')
           chat_id = update.message.chat_id
           update.message.bot.send_photo(chat_id=chat_id, photo=photo)
      else:
         update.message.reply_text(text='Video not found')
  else:
         update.message.reply_text(text='IP cam not connected', reply_markup=reply_markup)
  return MAIN

def get_photoGroup():
  if check_ping()==0:
      photos = list()
      i = 0
      while i < 3:
         fotoDir=get_folder(0)
         flag=snapshot(fotoDir)
         if flag:
            photos.append(InputMediaPhoto(open(fotoDir, 'rb')))
            i += 1
            time.sleep(2)
         else:
           text='Video not found'
#           update.message.reply_text(text=f'Video not found')
           break
      if not photos:
         return text
      else:
         return photos
  else:
      return 'IP cam not connected'

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

def check_ping():
   resp = os.system("ping -c 1 " +ipCam)
   return resp

def snapshot(folder):
   subprocess.call("ffmpeg -rtsp_transport tcp -i 'rtsp://%s/user=admin_password=123_channel=1_stream=0.sdp' -vframes 1 -r 1 %s" % (ipCam,folder), shell = True)
   return os.path.isfile(folder)

#def stream_video():
#   folder = get_folder(2)
#   videoDir = get_folder(1)
#   subprocess.call("ffmpeg -rtsp_transport tcp -i 'rtsp://%s/user=admin_password=123_channel=1_stream=0.sdp' -f image2 -threads 1 -t 30 -async 1 -r 1/0.5 -vcodec mjpeg %s/img%s.jpg" % (ipCam, folder,"%03d"), shell = True)
#   time.sleep(1)
#   subprocess.call('ffmpeg -f image2 -r 1/0.1 -i %s/img%s.jpg -preset slow %s' % (folder,"%03d", videoDir), shell = True)
#   subprocess.call('rm %s/img*.jpg' % folder, shell = True)
#   time.sleep(5)
#   return os.path.isfile(videoDir)

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    global prev_msg
    with open("alarmLogger.txt","r") as openfile:
        text_msg = openfile.read()
        if not str(prev_msg) in text_msg:
           context.bot.send_message(chat_id=str(chat_id), text=str(text_msg))
#          context.bot.send_message(chat_id=job.context, text=str(line))
           media = get_photoGroup()
           if type(media) is not str:
              context.bot.send_media_group(
              chat_id=chat_id,
#             chat_id=job.context,
              media=media
              )
           else:
              context.bot.send_message(job.context, text=media)
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
    """Add a job to the queue."""
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(FIVE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    try:
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, 10, context=chat_id, name=str(chat_id))
        query.edit_message_text(text='Alarm turn ON', reply_markup=reply_markup)

        job_file = open("jobLogger.txt", "w")
        job_file.write(str(chat_id))
        job_file.close()

    except (IndexError, ValueError):
        query.edit_message_text(text='Usage: /set <seconds>', reply_markup=reply_markup)
    return MAIN

def restart_job(context: CallbackContext):
        """Restart a job to the queue."""
        global chat_id
        if not os.stat("jobLogger.txt").st_size == 0:
           text_file = open("jobLogger.txt", "r")
           chat_id = text_file.read()
           text_file.close()
           context.job_queue.run_repeating(alarm, 10, context=str(chat_id), name=str(chat_id))

def check_alarm(update: Update, context: CallbackContext) -> int:
    """Check active jobs"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(FIVE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not current_jobs:
        query.edit_message_text(text="Alarm all off", reply_markup=reply_markup)
    for job in current_jobs:
        query.edit_message_text(text="Alarm turn ON ("+f'{job.name}'+")", reply_markup=reply_markup)
    return MAIN

def unset(update: Update, context: CallbackContext) -> int:
    """Remove the job if the user changed their mind."""
    keyboard = [
        [
            InlineKeyboardButton("Back", callback_data=str(FIVE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    query.answer()
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Alarm turn OFF' if job_removed else 'Alarm all ready off'
    query.edit_message_text(text=text, reply_markup=reply_markup)
    job_file = open("jobLogger.txt", "w")
    job_file.write("")
    job_file.close()
    return MAIN

def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater("1312160633:AAFMtHytCMbW9GIFVIEMUlsaUnqJZG3meGs", request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    j = updater.job_queue
    j.run_once(restart_job,1)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [
                CallbackQueryHandler(media_main, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(modem_main, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(rasp_main, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(alarm_main, pattern='^' + str(FIVE) + '$'),
            ],
            MEDIA: [
#                CommandHandler('photo', get_photoGroup),
                CommandHandler('photo', get_photo),
#                CommandHandler('video', get_video)
            ],
            MODEM: [
                CallbackQueryHandler(get_balance, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(BACK) + '$'),
            ],

            RASP: [
                CallbackQueryHandler(get_temp, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(get_disk_usage, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(get_durationtime, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(BACK) + '$'),
            ],

            ALARM: [
                CallbackQueryHandler(check_alarm, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(set_timer, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(unset, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(BACK) + '$'),
            ],

        },
        fallbacks=[CommandHandler('start', start)],
    )
    # Add ConversationHandler to dispatcher that will be used for handling
    # updates
    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("photo", get_photo))
    dispatcher.add_handler(CommandHandler("alarm", set_timer))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
