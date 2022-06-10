import win32com.client


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

    for message in reversed(messages):
        if "From: FactSet Alerts <FactSet_Alerts@factset.com>" in message.body:
            count += 1
            message.Move(fs_folder)

    print(f'{count} email(s) transferred')


if __name__ == '__main__':
    move_factset_email()

