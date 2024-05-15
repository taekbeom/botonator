import subprocess
from dotenv import load_dotenv
from pathlib import Path
import re
import paramiko
import logging
import os
import psycopg2
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
logging.basicConfig(filename=Path().cwd()/'logfile.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Heya {user.full_name}!\nType /help to receive help from a Regular lemming')
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPglmOFdByzDQl45bWTGR7-2qPRJaKAACNyYAAncluEv5RtBEaUu9ezUE')

def help(update: Update, context):
    help_text = """
<b><u>Trying to help . . .</u></b>
You received Available /help
find an email in the text <s>why</s> /find_email
find phone numbers in text <s>i will call them all</s> /find_phone_number
check strongness of your password <s>i will log in your account</s> /verify_password
check your submitted <s>freely handed to me</s> /get_emails
and those numbers you\'ve gladfully given to me /get_phone_numbers
also some linux commands <s>i wouldn\'t use them if i were you</s>
/get_release
/get_uname
/get_uptime
/get_df
/get_free
/get_mpstat
/get_w
/get_auths
/get_critical
/get_ps
/get_ss
/get_repl_logs
these ones are even cooler <s>nah still lame</s>
/get_apt_list
/get_services
    """
    update.message.reply_text(help_text, parse_mode='HTML')
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgQAAxkBAAErPhFmOFietFZYCKxOc60PYpc8uPZiOAACZw0AAoROcFHa0saNtVPIFTUE')

def ssh_connect(str_command):
    host = os.getenv("RM_HOST")
    port = os.getenv("RM_PORT")
    username = os.getenv("RM_USER")
    password = os.getenv("RM_PASSWORD")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(str_command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data

def db_connect():
    return psycopg2.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), database=os.getenv("DB_DATABASE"))

def find_phone_number_command(update: Update, context):
    update.message.reply_text('Type in text for phone number searching')
    return 'find_phone_number'

def find_email_command(update: Update, context):
    update.message.reply_text('Type in text for email searching')
    return 'find_email'

def verify_password_command(update: Update, context):
    update.message.reply_text('Type in password')
    return 'verify_password'

def get_apt_list_command(update: Update, context):
    result = ssh_connect('apt list | head -n 30')
    update.message.reply_text(f'{result}\nType in package')
    return 'get_apt_list'

def get_services_command(update: Update, context):
    result = ssh_connect('systemctl list-units --type=service | head -n 30')
    update.message.reply_text(f'{result}\nType in service')
    return 'get_services'

def get_emails(update: Update, context):
    user_name = update.message.from_user['username']
    try:
        connection = db_connect()
        with connection.cursor() as cursor:
            query = "SELECT * FROM email_info WHERE username = %(user_name)s"
            cursor.execute(query, {"user_name": user_name})
            emails = cursor.fetchall()
        if not emails:
            update.message.reply_text("Nothing was found on you, i haven\'t stolen anything, give me more info with /find_email")
            return ConversationHandler.END
        data = []
        for email in emails:
            data.append(f"Record {email[3]} was accepted on {email[2]} by {email[1]}")
        result = '\n'.join(val for val in data)
        update.message.reply_text("<u>Protocol</u>\n" + result, parse_mode='HTML')
    except (Exception, Error) as error:
        update.message.reply_text("You broke my PostgreSQL, congratulations", error)
    finally:
        connection.close()
        return ConversationHandler.END
    
def get_phone_numbers(update: Update, context):
    user_name = update.message.from_user['username']
    try:
        connection = db_connect()
        with connection.cursor() as cursor:
            query = "SELECT * FROM phone_info WHERE username = %(user_name)s"
            cursor.execute(query, {"user_name": user_name})
            phones = cursor.fetchall()
        if not phones:
            update.message.reply_text("Nothing was found on you, i haven\'t stolen anything, give me more info with /find_phone_number")
            return ConversationHandler.END
        data = []
        for phone in phones:
            data.append(f"Record {phone[3]} was accepted on {phone[2]} by {phone[1]}")
        result = '\n'.join(val for val in data)
        update.message.reply_text("<u>Protocol</u>\n" + result, parse_mode='HTML')
    except (Exception, Error) as error:
        update.message.reply_text("You broke my PostgreSQL, congratulations", error)
    finally:
        connection.close()
        return ConversationHandler.END

def find_phone_number(update: Update, context):
    user_input = update.message.text
    user_name = update.message.from_user['username']
    phoneNumRegex = re.compile(r'[\+7|8][\s|-]?\(?[489]\d{2}\)?[\s|-]?\d{3}[\s|-]?\d{2}[\s|-]?\d{2}')
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('You think you are so smart? But there are not so many phones')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPlBmOF0L9W-LCQXEFVqEiDGexqyYhwACBjAAAg-6YEl7_58ESLzsbzUE')
        return ConversationHandler.END
    phoneNumbers = '\n'.join(f'{i + 1}. {phoneNumber}' for i, phoneNumber in enumerate(phoneNumberList))
    update.message.reply_text(phoneNumbers)
    try:
        connection = db_connect()
        with connection.cursor() as cursor:
            for phone_number in phoneNumberList:
                query = "INSERT INTO phone_info(username, phone) VALUES (%(user_name)s, %(phone_number)s)"
                cursor.execute(query, {"user_name": user_name, "phone_number": phone_number})
                connection.commit()
        update.message.reply_text(f"Your private data was stolen and saved under name {user_name}. You better change your name")
    except (Exception, Error) as error:
        update.message.reply_text("You broke my PostgreSQL, congratulations", error)
    finally:
        connection.close()
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPilmOFsGA1RdbYZZelgdMBGXn0a7DwAC7AgAAlwCZQNNzI3Zu2BEsjUE')
        return ConversationHandler.END

def find_email(update: Update, context):
    user_input = update.message.text
    user_name = update.message.from_user['username']
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Are you trying to trick me with your non-existing emails?')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPjlmOFwquoIjEw7waYcI-mpfx-bWIgAClSYAAoW0IErdPo0wuSCYrzUE')
        return ConversationHandler.END
    emails = '\n'.join(f'{i + 1}. {email}' for i, email in enumerate(emailList))
    update.message.reply_text(emails)
    try:
        connection = db_connect()
        with connection.cursor() as cursor:
            for email in emailList:
                query = "INSERT INTO email_info(username, email) VALUES (%(user_name)s, %(email)s)"
                cursor.execute(query, {"user_name": user_name, "email": email})
                connection.commit()
        update.message.reply_text(f"Your private data was stolen and saved under name {user_name}. It\'s too late to escape")
    except (Exception, Error) as error:
        update.message.reply_text("You broke my PostgreSQL, congratulations", error)
    finally:
        connection.close()
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPjVmOFv2XV9vIqn16KC8IzPJYYL0wwACkREAAjyzxQeC90t0k0HOxjUE')
        return ConversationHandler.END

def verify_password(update: Update, context):
    user_input = update.message.text
    password_re = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$')
    password_check = password_re.search(user_input)
    if not password_check:
        update.message.reply_text('Too pathetic even for lemming, i died from cringe')
        context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPhVmOFk_KtHe0yVpFgtCsrDXabkH8QACfQcAAnx4-EhYsawzOmyhRzUE')
        return ConversationHandler.END
    update.message.reply_text('Lemming accepted your password and will use it')
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPhdmOFlUovrs5d9Fr9XrPIlKoBlTmgAC5RUAAuG62EvY0Cs6e4a3wjUE')
    return ConversationHandler.END

def get_apt_list(update: Update, context):
    user_input = update.message.text
    result = ssh_connect("apt show " + user_input + " | head -n 30")
    update.message.reply_text(result)
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgEAAxkBAAErPi9mOFtMuNcbUx_l1BqQ8aIw2bot-wACgAEAAkVfBy_uK5NwnHdBaDUE')
    return ConversationHandler.END

def get_services(update: Update, context):
    user_input = update.message.text
    result = ssh_connect("systemctl status " + user_input + " | head -n 30")
    update.message.reply_text(result)
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker='CAACAgIAAxkBAAErPjNmOFuLbKWU4hZbL5kpy2ZdeArYtwACXREAAjyzxQe_cv5Hoxvs4TUE')
    return ConversationHandler.END

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def linux(update: Update, context):
    user_command = update.message.text.split()[0].replace("/", "")
    
    if user_command not in commands_linux:
        update.message.reply_text("Invalid command")
        return ConversationHandler.END
    
    command = commands_linux[user_command]
    result = ssh_connect(command)
    update.message.reply_text(result)
    return ConversationHandler.END

def create_handler(command_func, execute_func, string_func):
    new_handler =  ConversationHandler(
        entry_points=[CommandHandler(string_func, command_func)],
        states={
            string_func: [MessageHandler(Filters.text & ~Filters.command, execute_func)],
        },
        fallbacks=[]
    )
    return new_handler

def get_repl_logs(update: Update, context):
    try:
        result = subprocess.run(["tac", "/var/log/postgresql/postgresql-15-main.log"], capture_output=True, text=True, check=True)
        grep_result = subprocess.run(["grep", "-E", "repl|accept connection"], input=result.stdout, capture_output=True, text=True, check=True)
        head_result = subprocess.run(["head", "-n", "20"], input=grep_result.stdout, capture_output=True, text=True, check=True)
        update.message.reply_text(head_result.stdout)
    except subprocess.CalledProcessError as e:
        update.message.reply_text(f"Error: {e}")
    return ConversationHandler.END


commands_linux = {
    "get_release": "lsb_release -a",
    "get_uname": "uname -a",
    "get_uptime": "uptime",
    "get_df": "df -h",
    "get_free": "free -h",
    "get_mpstat": "mpstat -A",
    "get_w": "w",
    "get_auths": "last -n 10",
    "get_critical": "journalctl -p 3 -n 5",
    "get_ps": "ps -e | head -n 30",
    "get_ss": "ss -tulnp",
}

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(create_handler(find_phone_number_command, find_phone_number, 'find_phone_number'))
    dp.add_handler(create_handler(find_email_command, find_email, 'find_email'))
    dp.add_handler(create_handler(verify_password_command, verify_password, 'verify_password'))
    dp.add_handler(create_handler(get_apt_list_command, get_apt_list, 'get_apt_list'))
    dp.add_handler(create_handler(get_services_command, get_services, 'get_services'))
    dp.add_handler(CommandHandler(commands_linux.keys(), linux))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()