import win32com.client
from models import session, FactSet, User, NameValue, LogDb
from datetime import datetime, date
from MoveEmail import move_factset_email, find_mapi_folder_num
from utils import add_log_db
import logging

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.INFO, filename='app.log')

def forward_email():
    move_factset_email()
    outlook = win32com.client.Dispatch('outlook.application')
    mapi = outlook.GetNamespace('MAPI')
    mapi_num = find_mapi_folder_num(mapi, 'media@ananda-am.com')

    for index, folder in enumerate(mapi.Folders(mapi_num).Folders(2).folders):
        if folder.name == 'FactSet':
            fs_num = index + 1
            fs_folder = folder
            break

    # myTime = datetime.now() - timedelta(hours=10)
    # last_time_str = '2022-01-23 15:43:02.894000'
    fact_set_obj = session.query(NameValue).filter(NameValue.name == 'fact_set_last_time').first()
    last_time_str = fact_set_obj.value

    last_time_real = datetime.strptime(last_time_str, '%Y-%m-%d %H:%M:%S.%f')
    max_time = last_time_real
    last_time = last_time_real.strftime('%m/%d/%Y %H:%M %p')
    messages = fs_folder.Items.restrict(f"[ReceivedTime] > '{last_time}'")
    count = 0

    # don't do nothing for Araceli
    fact_set_db = session.query(FactSet).join(User).filter(User.first_name != 'Araceli').all()

    for message in reversed(messages):
        send_to_list = []
        body = message.body
        subject = message.subject
        received_time_str = message.receivedTime.strftime('%Y-%m-%d %H:%M:%S.%f')
        received_time = datetime.strptime(received_time_str, '%Y-%m-%d %H:%M:%S.%f')
        if "From: FactSet Alerts <FactSet_Alerts@factset.com>" in body:
            for fact_set in fact_set_db:
                symbol = fact_set.symbol
                if symbol in body:
                    first_name = fact_set.user.first_name
                    if not first_name in send_to_list and received_time > last_time_real:
                        # new_subject = f'{subject} - {symbol} - {fact_set.user.first_name} - {received_time}'
                        new_subject = f'{subject} - {symbol} - {fact_set.user.first_name}'
                        NewMsg = message.Forward()
                        NewMsg.Body = message.Body
                        NewMsg.Subject = new_subject  # message.Subject
                        NewMsg.To = "olivier@ananda-am.com"
                        NewMsg.Send()

                        if received_time > max_time:
                            max_time = received_time
                        send_to_list.append(first_name)
                        count += 1

    fact_set_obj.value = max_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    session.commit()
    my_text = f'{count} email forwarded - Last update: {max_time}'
    print(my_text)
    logging.info(my_text, exc_info=True)

    today = date.today()
    today_dt = datetime(year=today.year, month=today.month, day=today.day)

    factset_log = session.query(LogDb).filter(LogDb.date_time > today_dt).order_by(LogDb.date_time.desc()).first()
    if factset_log:
        factset_log.date_time = datetime.now()
        session.commit()
    else:
        add_log_db("Factset", "loop", "NA", "Last loop", "Info")

if __name__ == '__main__':
    logging.info(" Schedule Task Factset Started", exc_info=True)
    forward_email()

