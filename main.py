import logging
from storage.storage_factory import StorageFactory
from telegram import Update
from telegram.ext import  CommandHandler, CallbackContext, ApplicationBuilder, ConversationHandler, MessageHandler, filters
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv('TOKEN')
OWNER = os.getenv('OWNER')

storage = StorageFactory.get_storage('sqlite')

def is_owner(user):
    return user == OWNER

def user_exist(user_name):
    return storage.user_exist(user_name)

def insert(user_name_list):
    existed_users = []
    for user_name in user_name_list: 
        if user_exist(user_name):
            existed_users.append(user_name)
        else:
            storage.insert_user(user_name)
    if len(existed_users) > 0:
        return False, existed_users
    else:
        return True, None
    
def remove(user_name_list):
    for user_name in user_name_list:
        storage.delete_user(user_name)

async def remove_member(update, context):
    username = update.message.from_user.username
    if is_owner(username):
        user_name_list = update.message.text
        if len(user_name_list) > 0:    
            remove(user_name_list)
            await update.message.reply_text(f'Xóa người dùng thành công')
        else:
            await update.message.reply_text(f'Dữ liệu nhập vào rỗng')
    else:
        await update.message.reply_text("You are not authorized to use this bot.")
    context.user_data.clear()
    return ConversationHandler.END

async def add_member(update, context):
    username = update.message.from_user.username 
    if is_owner(username):
        user_name_list = update.message.text.split(',')
        if len(user_name_list) > 0:
            res , existed_users = insert(user_name_list)
            if not res:
                await update.message.reply_text(f'Người dùng {", ".join(existed_users)} đã tồn tại')
            else:
                await update.message.reply_text(f'Thêm người dùng thành công')
        else:
            await update.message.reply_text(f'Dữ liệu nhập vào rỗng')
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
    context.user_data.clear()
    return ConversationHandler.END

async def show_member(update, context):
    username = update.message.from_user.username
    if is_owner(username):
        users = storage.get_all_users()
        if users:
            user_list = '\n'.join([f"{user[1]}" for user in users])
            await update.message.reply_text(f'Danh sách người dùng:\n{user_list}')
        else:
            await update.message.reply_text('Danh sách người dùng rỗng.')
        await update.message.reply_text("Bạn có muốn thực hiện thay đổi member ?\n1.Thêm mới\n2.Xóa bỏ\nq.Thoát")
        return MODIFY_MEMBER
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
        return ConversationHandler.END

async def modify_member(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    if is_owner(username):
        user_choice = update.message.text.lower()
        if user_choice == '1':
            await update.message.reply_text("Điền member mà bạn muốn thêm")
            return ADD_MEMBER
        if user_choice == '2':
            await update.message.reply_text("Điền member mà bạn muốn xóa")
            return REMOVE_MEMBER    
        elif user_choice == 'q':
            await update.message.reply_text("Kết thúc việc chỉnh sửa")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Lựa chọn không phù hợp. Hay điền lựa chọn phù hợp hoặc q để kết thúc.")
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
        return ConversationHandler.END

async def tag_all(update, context):
    users = storage.get_all_users()
    user_list = ' '.join([f"@{user[1]}" for user in users])
    await update.message.reply_text(f'{user_list}')

def validate_day(day):
    try:
        # Check if day is a valid integer between 1 and 31
        day_int = int(day)
        if 1 <= day_int <= 31:
            return True
        else:
            return False
    except ValueError:
        # If conversion to integer fails, check if it's a valid weekday
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if day.lower() in weekdays:
            return True
        else:
            return False
def validate_id(id):
    try:
        # Check if id is a valid integer
        id_int = int(id)
        return True
    except ValueError:
        # If conversion to integer fails
        return False


# def validate_message(message):
#     # Use regex to check if the message contains only alphanumeric characters and spaces
#     return bool(re.match("^[a-zA-Z0-9 \n.:()/\\-]+$", message))

def validate_time(time):
    try:
        # Check if time is a valid HH:MM format
        hours, minutes = map(int, time.split(':'))
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return True
        else:
            return False
    except (ValueError, AttributeError):
        # If conversion or split fails
        return False

async def show_job(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    if is_owner(username):
        # Logic to fetch and display jobs
        jobs = storage.get_all_jobs()
        status = ['Tắt','Bật']

        if jobs and len(jobs[0]) >= 6:
            job_list = '\n'.join([f"---\nID: {job[0]}\n Ngày: {job[1]}\n Công việc: {job[2]}\n Thời gian: {job[3]}\n Trạng thái: {status[job[4]]}\n Nhóm: {job[5]}" for job in jobs])
            await update.message.reply_text(f"Danh sách nhắc việc:\n{job_list}")
        else:
            await update.message.reply_text("Danh sách rỗng")
        # ...
        await update.message.reply_text("Bạn có muốn thực hiện thay đổi các công việc ?\n1.Thêm mới\n2.Xóa bỏ\n3.Tắt/Bật lịch\nq.Thoát")
        return MODIFY_JOB
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
        return ConversationHandler.END

async def modify_job(update: Update, context: CallbackContext) -> int:
    username = update.message.from_user.username
    if is_owner(username):
        user_choice = update.message.text.lower()
        if user_choice == '1':
            await update.message.reply_text("Điền thông tin về công việc bạn muốn thêm")
            await update.message.reply_text("Nhập ngày (1-31 hoặc monday-sunday):")
            context.user_data['step'] = 'day'
            return ADD_JOB
        elif user_choice == '2':
            await update.message.reply_text("Điền ID mà bạn muốn xóa")
            context.user_data['step'] = 'remove'
            return REMOVE_JOB
        elif user_choice == '3':
            await update.message.reply_text("Điền ID mà bạn muốn tắt/bật")
            context.user_data['step'] = 'switch'
            return SWITCH_JOB
        elif user_choice == 'q':
            await update.message.reply_text("Kết thúc việc chỉnh sửa")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Lựa chọn không phù hợp. Hay điền lựa chọn phù hợp hoặc q để kết thúc.")
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
        return ConversationHandler.END     

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Hủy Hành động.")
    return ConversationHandler.END

async def add_job(update: Update, context: CallbackContext) -> int:
    step = context.user_data.get('step', None)
    username = update.message.from_user.username
    if is_owner(username):
        if step == 'day':
            day_input = update.message.text
            # Split the input string into a list of days
            days = [day.strip() for day in day_input.split(',')]

            if all(validate_day(day) for day in days):
                if 'days' not in context.user_data:
                    context.user_data['days'] = []
                context.user_data['days'].extend(days)
                await update.message.reply_text(f"Nhập thông tin về công việc bạn muốn thêm:")
                context.user_data['step'] = 'message'
            else:
                await update.message.reply_text("Ngày không hợp lệ. Nhập lại ngày (1-31 hoặc monday-sunday):")

        elif step == 'message':
            message_input = update.message.text
            # if validate_message(message_input):
            context.user_data['message'] = message_input
            await update.message.reply_text(f"Nhập thời gian (HH:MM,HH:MM,...):")
            context.user_data['step'] = 'time'

        elif step == 'time':
            time_input = update.message.text
            # Split the input string into a list of times
            times = [time.strip() for time in time_input.split(',')]

            if all(validate_time(time) for time in times):
                if 'times' not in context.user_data:
                    context.user_data['times'] = []
                context.user_data['times'].extend(times)
                context.user_data['step'] = 'group'
                await update.message.reply_text(f"Nhập danh sách nhóm (CHAT_ID_1,CHAT_ID_2,...):")
            else:
                await update.message.reply_text("Thời gian không hợp lệ. Nhập lại thời gian (HH:MM,HH:MM,...):")
        
        elif step == 'group':
            groups = update.message.text

            # Process the collected data and insert into the database
            days = context.user_data.get('days', [])
            message = context.user_data.get('message', '')
            times = context.user_data.get('times', [])

            days_str = ','.join(days)
            times_str = ','.join(times)

            storage.insert_job(days_str, message, times_str, groups)

            # Clear user_data for the next conversation
            context.user_data.clear()

            await update.message.reply_text("Công việc đã được thêm thành công.")
            return ConversationHandler.END
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
        return ConversationHandler.END
    return ADD_JOB

async def remove_job(update: Update, context: CallbackContext):
    step = context.user_data.get('step', None)
    username = update.message.from_user.username
    if is_owner(username):
        if step == 'remove':
            input_ID = update.message.text
            IDs = (ID.strip() for ID in input_ID.split(','))
            for ID in IDs:
                if validate_id(ID):
                    storage.delete_job(ID)
                    await update.message.reply_text(f"Việc có ID {ID} đã được xóa.")
                else:
                    await update.message.reply_text(f"ID {ID} không hợp lệ.")
            
            # Clear user_data for the next conversation
            context.user_data.clear()
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
    return ConversationHandler.END

async def switch_job(update: Update, context: CallbackContext):
    step = context.user_data.get('step', None)
    username = update.message.from_user.username
    if is_owner(username):
        if step == 'switch':
            input_ID = update.message.text
            IDs = (ID.strip() for ID in input_ID.split(','))
            for ID in IDs:
                if validate_id(ID):
                    current_status = storage.get_job_status(ID)
                    new_status = 1 if current_status[0] == 0 else 0

                    # Update the 'status' column for a specific ID
                    storage.switch(new_status, ID)
                await update.message.reply_text(f"Đổi trạng thái lịch số {ID} thành công")
            context.user_data.clear()
    else:
        # Notify unauthorized user
        await update.message.reply_text("You are not authorized to use this bot.")
    return ConversationHandler.END

async def help(update,context):
    await update.message.reply_text("Bot Nhắc việc:\n/help: Thông tin các lệnh\n/all: tag all member\n/member: hiển thị danh sách thành viên\n/job: hiển thị danh sách công việc")

class NotCommandFilter(filters.BaseFilter):
    def filter(self, message: Update) -> bool:
        return message.text and not message.text.startswith('/')
    
MODIFY_MEMBER, ADD_MEMBER, REMOVE_MEMBER, MODIFY_JOB, ADD_JOB, REMOVE_JOB, SWITCH_JOB = range(7)

def main():

    application = ApplicationBuilder().token(TOKEN).build()

    shout_handler = CommandHandler("all",tag_all)
    help_hanlder = CommandHandler("help",help)

    not_command_filter = NotCommandFilter()

    member_handler = ConversationHandler(
        entry_points=[CommandHandler('member', show_member)],
        states={
            MODIFY_MEMBER: [MessageHandler(not_command_filter, modify_member)],
            ADD_MEMBER: [MessageHandler(not_command_filter, add_member)],
            REMOVE_MEMBER: [MessageHandler(not_command_filter, remove_member)],
        },
        fallbacks=[CommandHandler('c', cancel)],
    )

    job_handler = ConversationHandler(
        entry_points=[CommandHandler('job', show_job)],
        states={
            MODIFY_JOB: [MessageHandler(not_command_filter, modify_job)],
            ADD_JOB: [MessageHandler(not_command_filter, add_job)],
            REMOVE_JOB: [MessageHandler(not_command_filter, remove_job)],
            SWITCH_JOB: [MessageHandler(not_command_filter, switch_job)],
        },
        fallbacks=[CommandHandler('c', cancel)],
    )

    application.add_handler(help_hanlder)
    application.add_handler(member_handler)
    application.add_handler(job_handler)
    application.add_handler(shout_handler)
    
    application.run_polling()

if __name__ == "__main__":
    main()