import os

import requests


class YaUploader:

    def __init__(self, token: str):
        self.token = token
        self.folder = ''

    def create_new_folder(self, new_folder: str):
        my_headers = {'Authorization': 'OAuth ' + self.token}
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        new_folder = ''.join(x for x in new_folder if x.isalnum() or x.isspace() or x == '/' or x == '_' or x == '-')
        new_folder = new_folder.replace(' ', '_')
        while '//' in new_folder:
            new_folder = new_folder.replace('//', '/')
        self.folder = new_folder
        path_folder = ''
        message = ''

        folders_list = new_folder.split('/')
        for i, folder in enumerate(folders_list):
            path_folder = path_folder + '/' + folder
            my_params = {'path': path_folder}
            resp = requests.put(url, headers=my_headers, params=my_params)
            if (i == len(folders_list) - 1) and resp.status_code == 409:
                message += f'   Папка {path_folder} уже существует на Яндекс.Диске!'
        return message

    def upload(self, file_path: str):
        """Метод загружает файл file_path на яндекс диск"""
        my_headers = {'Authorization': 'OAuth ' + self.token}
        fname = os.path.split(file_path)[1]
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        my_params = {'path': self.folder + '/' + fname, 'overwrite': 'true'}

        resp1 = requests.get(url, headers=my_headers, params=my_params)
        if resp1.status_code != requests.codes.ok:
            return f'При получении ссылки для загрузки произошла ошибка (код: {resp1.status_code})'
        href = resp1.json()['href']
        with open(file_path, 'rb') as f:
            resp2 = requests.put(href, files={'file': f})
        if resp2.status_code not in (requests.codes.created, requests.codes.accepted):
            return f'При загрузке файла произошла ошибка (код: {resp2.status_code})'
        return f'Файл {fname} успешно загружен на Яндекс.Диск'


if __name__ == '__main__':
    my_token = input('Введите токен Яндекс.Диск: ')
    uploader = YaUploader(my_token)
    create_new_folder = input('Создать новую папку, куда потом загрузится файл? (Y/N): ').lower()
    if create_new_folder in ['y', 'yes']:
        new_folder = input('Введите название новой папки: ')
        print(uploader.create_new_folder(new_folder))

    file = input(
        'Введите имя файла с расширением из папки "src/files/" данного проекта,\n который хотите загрузить на Яндекс.Диск: ')
    file_path = os.path.join('files', file)
    result = uploader.upload(file_path)
    print(result)
