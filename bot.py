
from telegram import Update , ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes , ConversationHandler ,MessageHandler,filters
from databaseconfig import dbconnect
from datetime import datetime ,timezone
from dotenv import load_dotenv
import os

load_dotenv()


#conversion states
CLASS,STUDENTID,ATTCODE = range(3)


#collection name
COLLECTION_NAME = "attendances"


#Ask for class
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
     reply_keyboard = [['Nodejs B1','Python B2','Reactjs B3','WDF 15']]
     markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
     await update.message.reply_text("Please choose your class : ",reply_markup=markup)
     return CLASS
     

#Temp save getclass and ask for studentid
async def getclass(update: Update, context: ContextTypes.DEFAULT_TYPE):
      context.user_data["class"] = update.message.text
      await update.message.reply_text("Enter your student ID (eg.,WDF1001) : ")
      return STUDENTID

#Temp save email and insert to DB
async def getstudentid(update: Update, context: ContextTypes.DEFAULT_TYPE):
     context.user_data["studentid"] = update.message.text
     await update.message.reply_text("Enter your ATT code (eg.,12CB) : ")
     return ATTCODE


async def getattcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
     context.user_data["attcode"] = update.message.text
     user = update.effective_user

     user_class = context.user_data["class"]
     user_studentid = context.user_data["studentid"]
     user_attcode = context.user_data["attcode"]



     # Insert into Mongodb
     db = dbconnect()
     collection = db[COLLECTION_NAME]


     data = {
         "user_id":str(user.id),
         "class":user_class,
         "studentid":user_studentid,
         "attcode":user_attcode,
         "createdAt":datetime.now(timezone.utc)
     }

     try:
         collection.insert_one(data)
         await update.message.reply_text("Attendance record successfully.")
     except Exception as e:
         print("Error inserting attendence : ",e)
         await update.message.reply_text("Failed to record attendances.")
         

     return ConversationHandler.END




#Cancel command "/cancel"
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
     await update.message.reply_text("Registration cancelled.")
     return ConversationHandler.END




# Fetch own DB
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)

    #fetch firebase
    db = dbconnect()
    collection = db[COLLECTION_NAME]

    try:
         
         records = list(
              collection.find({"user_id":user_id}).sort("createdAt",-1) #pymongo.Asscending
         )

         if records:
              message = "Your Attendance records:\n\n"

              for record in records:
                   createdAt = record.get("createdAt")
                   createdAtstr = record.get("createdAt").strftime("%Y-%M-%d %H:%M:%S") if createdAt else "N/A"
                   message += (
                        f"class : {record.get('class')}\n"
                        f"student ID : {record.get("studentid")}\n"
                        f"Attendance code : {record.get('attcode')}\n"
                        f"Date : {createdAtstr}\n\n"
                   )

         else:
              message = "No attendance records found!"


         await update.message.reply_text(message)
  

    except Exception as e:
         print("Error fetching attendence : ",e)
         await update.message.reply_text("Failed to fetch attendence records.")

    return ConversationHandler.END





def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, getclass)],
            STUDENTID: [MessageHandler(filters.TEXT & ~filters.COMMAND, getstudentid)],
            ATTCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, getattcode)]
        
        },
        fallbacks=[CommandHandler("cancel",cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("report", report))
    print('Bot is running...')
    app.run_polling()



if __name__ == '__main__':
    main()