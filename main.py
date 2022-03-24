import win32com.client


if __name__ == '__main__':

    outlook = win32com.client.Dispatch('outlook.application')
    mapi = outlook.GetNamespace('MAPI')

    for index, folder in enumerate(mapi.Folders(1).Folders(2).folders):
        if folder.name == 'FactSet':
            fs_num = index + 1
            fs_folder = folder
            break

    messages = mapi.Folders(1).Folders(2).Items
    count = 0

    for message in reversed(messages):
        if "From: FactSet Alerts <FactSet_Alerts@factset.com>" in message.body:
            count += 1
            message.Move(fs_folder)

    print(f'{count} email(s) transferred')
