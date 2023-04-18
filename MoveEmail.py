import win32com.client
import logging

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', level=logging.INFO, filename='app.log')


def find_mapi_folder_num(mapi, my_email):
    num = 1
    while str(mapi.folders(num)) != my_email:
        num += 1
    return num


def move_factset_email():
    outlook = win32com.client.Dispatch('outlook.application')
    mapi = outlook.GetNamespace('MAPI')
    mapi_num = find_mapi_folder_num(mapi, 'olivier@ananda-am.com')

    for index, folder in enumerate(mapi.Folders(mapi_num).Folders(2).folders):
        if folder.name == 'FactSet':
            fs_num = index + 1
            fs_folder = folder
            break

    messages = mapi.Folders(mapi_num).Folders(2).Items
    count = 0

    logging.info(f"Messages size {len(messages)}", exc_info=True)
    for message in reversed(messages):
        if "From: FactSet Alerts <FactSet_Alerts@factset.com>" in message.body:
            count += 1
            message.Move(fs_folder)
    my_text = f'{count} email(s) transferred'

    print(my_text)
    logging.info(my_text, exc_info=True)


if __name__ == '__main__':
    move_factset_email()

