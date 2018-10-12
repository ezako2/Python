# -*- coding: utf-8 -*-
import re
import sys
import os
import pymysql.cursors
import datetime
import urllib.request
import json
from ftplib import FTP_TLS
from bs4 import BeautifulSoup
import requests
import xml.etree.ElementTree as ET
import xmltodict, json
if sys.version_info[0] < 3:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse

from Models import *
from Lang import *

if sys.version_info[0] < 3:
    pass
else:
    pass
from colorama import init
from termcolor import colored

init()

import argparse
parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('--page', type=str,
                    help='An optional integer argument')
args = parser.parse_args()
print(args.page)
page_number = ''
page_number = args.page
page_number = '35'

NON_MODEL = []
connection = pymysql.connect(host='94.130.18.174',
                                             user='firm_support',
                                             password='5v4gVuyMBNMzaW',
                                             db='firmware_dcp',
                                             charset='utf8',
                                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:

        for page_number in range(179, 101, -1):
            print('Page: ' + str(page_number))
            page_number = str(page_number)


            WorkingPath = '/public/download/Mobile/Huawei/11-10-2018/00/01'
            NewUrlPath = 'https://srv3.gem-flash.com/download/Mobile/Huawei/11-10-2018/00/01/'

            def write_text_info():
                info_text_name = firmware_name_model + '_' + firmware_name + '_' + firmware_version + '_' + lang[
                    firmware_name_lang_short] + '.txt'
                info_text_name = info_text_name.replace('\n', '_')
                info_text_name = info_text_name.replace('__', '_')
                info_text_name2 = firmware_name + '_' + firmware_version + '_' + lang[
                    firmware_name_lang_short]
                info_text_name2 = info_text_name2.replace('__', '_')
                print(info_text_name)
                if re.findall('^8', firmware_version):
                    firmware_version_text = firmware_version + '\n' + 'OS Version: Android Oreo V8'
                elif '5.' in firmware_version or 'EMUI 5.' in change_log_text:
                    firmware_version_text = '5.0' + '\n' + 'OS Version: Android Nougat V7'
                elif '4.' in firmware_version or 'EMUI 4.' in change_log_text:
                    firmware_version_text = '4.0' + '\n' + 'OS Version: Android Marshmallow V6'
                elif '3.' in firmware_version or 'EMUI 3.' in change_log_text:
                    firmware_version_text = '3.0' + '\n' + 'OS Version: Android Lollipop V5'
                else:
                    firmware_version_text = firmware_version

                if key['type'] == 'FullOTA-MF':
                    firmware_type = key['type']
                elif key['type'] == 'FullOTA-MF-PV':
                    firmware_type = key['type'] + ' | for upgrade from major android version (from v7 to v8)'

                lang_text_info = lang[firmware_name_lang_short].replace('_', ' ')
                if firmware_name_lang_short == 'C185' or firmware_name_lang_short == 'C199' or firmware_name_lang_short == 'C433':
                    lang_text_info = lang_text_info + '\nCountry and Language supported: Bahrain, Cyprus, Egypt, Iran, Iraq, Israel, Jordan, Kuwait, Lebanon, Oman, Qatar, Saudi Arabia, Syria, Turkey, United Arab Emirates, Yemen, Arabic, Hebrew, Persian, Turkish'
                info_content = """{1}
Model Code Name: {2}
Model Name: {3}
Language Code: {4}
Region / Country: {5}
EMUI Version: {6}
Firmware Type: {7}
File Size: {9} GB
{8}
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
How to flash this firmware to your phone:

1- Rename the downloaded file to update.zip
2- Extract the Update.zip file
3 -Create a folder named Dload in the device’s internal storage or on your SD card and put the update.app (Extracted Update.zip) file there
4- Then go to Settings > About phone > System Update, and then select Local Update.
5- After that, Give the downloaded update file’s location on the next screen
6- The installation will start automatically
Once completed, reboot your device
Done!!! Your device should now have the latest update running
-= OR =-
You can start update from dialer *#*#2846579#*#* and ProjectMenu -> Software Upgrade -> SDCard Upgrade
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
{1}.zip

{0}"""
                info_content = info_content.format(newurl, info_text_name2, firmware_name_model, Models_Name[firmware_name_model],
                                                   firmware_name_lang_short, lang_text_info,
                                                   firmware_version_text, firmware_type, change_log_text, file_size)
                # print(info_content)

                with open('text/' + info_text_name, 'w', encoding="utf-8") as f:
                    f.write(info_content)


            def uploadtoftp(filecat, filename):
                ftps = FTP_TLS('95.216.75.58')
                ftps.login(user='srv3', passwd='kDs\!ND[&L|$`"&O30~f@')
                ftps.cwd(WorkingPath)
                if filecat not in ftps.nlst():
                    ftps.mkd(filecat)
                ftps.cwd(filecat)
                fh = open(filename, 'rb')
                ftps.storbinary('STOR ' + filename, fh)
                fh.close()
                print('file uploaded#1: ' + filename)
                ftps.close()

            def downloadnow(url , filename):
                r = os.system('aria2c --console-log-level=warn --continue=true --connect-timeout=60 --summary-interval=0 --file-allocation=none --allow-overwrite=false -x8 --split=8 --timeout=180  {0} -o {1}'.format(url, filename))
                if r == 0:
                    print('Download Completed')
                else:
                    print('there is error while download , error code: ' + str(r))
                return str(r)


            def checkinftp(FileName):
                ftps = FTP_TLS('95.216.75.58')
                ftps.login(user='srv3', passwd='kDs\!ND[&L|$`"&O30~f@')
                ftps.cwd(WorkingPath)
                # print(FileName)
                # print(ftps.nlst())
                folderlist = ftps.nlst()
                folderlist.remove('.')
                folderlist.remove('..')
                filelist = []  # to store all files
                for f in folderlist:
                    # print(f)
                    ftps.cwd(f)
                    ftps.retrlines('NLST', filelist.append)  # append to list
                    ftps.cwd('..')

                # print(filelist)
                if FileName in filelist:
                    # print('Found in FTP')
                    ftps.close()
                    return 0
                else:
                    ftps.close()
                    return 1
                    # exit()


            NON_lang = []
            ALL_MODELS = []

            headers = {'Referer': 'http://pro-teammt.ru',
                       'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}

            page3 = requests.get('http://pro-teammt.ru/projects/hwff/info/ff_get_data.php?page_json=' + page_number, headers=headers)
            # print(page3.text)
            # exit()


            url = page3.text
            # page = urllib.request.urlopen(url)
            # pagecontent = page.read()
            pagecontent = url
            data = json.loads(pagecontent, strict=False)
            # with open('#New_list.log', mode='w', encoding='utf-8') as f:
            #     f.write(str(data))

            for key in data:
                firmwares = data['firmwares']
            # print(len(firmwares))
            x = 0
            # firmwares = [{'firmware': 'MLA-B166,MLA-TL10C01B166', 'type': 'FullOTA-MF', 'changelog_link': 'http://update.hicloud.com:8180/TDS/data/files/p3/s15/G1440/g104/v79112/f2/full/changelog.xml', 'filelist_link': 'http://update.hicloud.com:8180/TDS/data/files/p3/s15/G1440/g104/v79112/f2/full/filelist.xml', 'size': '2239298939', 'date': '2017.02.28', 'g_big': '1440', 'g_small': '104', 'v': '79112', 'f': '2'}]

            for key in firmwares:

                # print(key['firmware'])
                # print(key)
                if key['type'] == 'FullOTA-MF' or key['type'] == 'FullOTA-MF-PV':
                    # print(key)

                    firmware = key['firmware']

                    firmware = firmware.replace('BND-TL10-cmcc-cn:', '')
                    firmware = firmware.replace('?', '')
                    firmware = firmware.replace('\n', '')

                    print(firmware)
                    changelog_link = key['changelog_link']
                    filelist_link = key['filelist_link']
                    # print(filelist_link)
                    file_size = key['size']
                    file_size = round(int(file_size) / 1024 / 1024/1024, 2)
                    # print(file_size)
                    # exit()
                    file_date = key['date']

                    firmware_split = firmware.split(',')

                    # print(firmware_split)

                    firmware_name_compain = []

                    for firmware_split2 in firmware_split:
                        firmware_split3 = firmware_split2.split(' ')
                        print(firmware_split3)
                        firmware_name = firmware_split3[0]
                        firmware_version = ''
                        if len(firmware_split3) == 2:
                             firmware_version = firmware_split3[1]
                        firmware_name_compain.append(firmware_name)

                    firmware_name_compain1 = '_'.join(firmware_name_compain)
                    print(firmware_name_compain1)
                    firmware_name_compain2 = firmware_name_compain1.split('_')
                    for firmware_name_compain3 in firmware_name_compain2:

                        print(filelist_link)
                        print(changelog_link)
                        download_link = re.sub('filelist.xml', 'update.zip', filelist_link)
                        print(download_link)

                        firmware_name = firmware_name_compain3
                        # print(firmware_name)
                        if re.findall('[A-Za-z0-9]+-[A-Za-z]+[0-9]+[A-Z]+', firmware_name):
                            firmware_name_model = re.findall('[A-Za-z0-9]+-[A-Za-z]+[0-9]+[A-Z]+', firmware_name)[0]

                            firmware_name_model = re.sub('C$', '', firmware_name_model)

                        else:
                            firmware_name_model = ''
                            print('firmware_name_model: Empty')
                            continue

                        if firmware_name_model in IGNORE_LIST:
                            print('this model in ignore list: ' + firmware_name_model)
                            firmware_name_model = ''
                            continue
                        if firmware_name_model in IGNORE_FIRMWARE:
                            print('this model in ignore list: ' + firmware_name_model)
                            firmware_name_model = ''
                            continue
                        if firmware_name in IGNORE_FIRMWARE:
                            print('this firmware in ignore list: ' + firmware_name_model)
                            firmware_name_model = ''
                            continue
                        if '-B' in firmware_name_model:
                            print('this model has -B: ' + firmware_name_model)
                            firmware_name_model = ''
                            continue
                        if '-log' in firmware_name_model:
                            print('this model has -log: ' + firmware_name_model)
                            firmware_name_model = ''
                            continue

                        if firmware_name_model not in Models_Name:
                            print(colored('this model is not in our list: ' + firmware_name_model, 'red'))
                            NON_MODEL.append(firmware_name_model)
                            continue
                            # exit()

                        # resp = requests.get(changelog_link)
                        # msg = resp.content
                        change_log_text = ''
                        # print(changelog_link)
                        request = requests.get(changelog_link)
                        if request.status_code == 200:
                            print('Web site exists')
                            # print(changelog_link)
                            page2 = urllib.request.urlopen(changelog_link, timeout=180)
                            msg = page2.read()
                            # msg = pagecontent2.decode()
                            try:
                                o = xmltodict.parse(msg)
                            except:
                                print('xmk error')
                                # exit()
                            # o = xmltodict.parse(msg)
                            u = json.dumps(o)  # '{"e": {"a": ["text", "text"]}}'
                            data2 = json.loads(u, strict=False)
                            aaa = data2['root']['language']
                            # print(type(aaa))
                            en_us_features = None
                            if type(aaa) is dict:
                                for keys, value in aaa.items():
                                    # print(type(keys))
                                    # print(value)
                                    if keys == 'en-us':
                                        en_us_features = keys['features']
                                    # else:
                                    #     en_us_features = None

                            elif type(aaa) is list:
                                for keys in aaa:
                                    # print(keys)
                                    if keys['@name'] == 'en-us':
                                        en_us_features = keys['features']
                                        # print(en_us_features)
                                    # else:
                                    #     en_us_features = None

                            # print(en_us_features)
                            # exit()

                            if en_us_features is not None:
                                change_log_text = []
                                # print(en_us_features)
                                # print(type(en_us_features))
                                if type(en_us_features) is dict:
                                    for keys, value in en_us_features.items():
                                        change_log_text.append(keys)
                                        change_log_text.append(value)
                                elif type(en_us_features) is list:
                                    for keys in en_us_features:
                                        if '@module' in keys:
                                            change_log_text.append(str(keys['@module']))
                                        if '@module' in keys:
                                            change_log_text.append(str(keys['feature']))

                                # print(change_log_text)
                                try:
                                    change_log_text = '\n'.join(change_log_text)

                                    change_log_text = change_log_text.replace('@module\n', '')
                                    change_log_text_2 = """=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Whats New in this release (Change Log):

"""
                                    change_log_text = change_log_text_2 + change_log_text
                                    change_log_text = change_log_text.replace('\n\n', '\n')
                                except:
                                    change_log_text = ''
                                # print(change_log_text)
                            # exit()
                        else:
                            print('Web site does not exist')
                            continue




                        # print(firmware_name_model)
                        # print(firmware)
                        print(firmware_name_model)
                        ALL_MODELS.append(firmware_name_model)
                        firmware_name2 = firmware_name.replace(firmware_name_model, '')
                        firmware_name_lang = re.sub('B.*', '', firmware_name2)
                        # print(firmware_name_lang)
                        firmware_name_lang_short = re.sub('.*CUST', '', firmware_name_lang)
                        firmware_name_lang_short = re.sub('D.*', '', firmware_name_lang_short)

                        if re.findall('B.*', firmware_name2):
                            firmware_name_build = re.findall('B.*', firmware_name2)[0]
                            firmware_name_build = re.sub('-.*', '', firmware_name_build)
                        else:
                            firmware_name_build = ''


                        if firmware_name_lang_short in lang:
                            print(firmware_name_lang_short)
                        else:
                            NON_lang.append(firmware_name_lang_short)
                            print('lang is not defind: ' + firmware_name_lang_short)
                        print(firmware_name_build)
                        sql = "SELECT * FROM dcp_files where file_title like %s and file_title like %s and (file_title like %s or file_title like %s)"

                        firmware_name_model2 = firmware_name_model.replace('-', '_')
                        cursor.execute(sql, ('%' + firmware_name_build + '%', '%' + firmware_name_lang_short + '%', '%' + firmware_name_model + '%', '%' + firmware_name_model2 + '%'))
                        if cursor.rowcount == 0:
                            x += 1
                            print(colored(x, 'yellow'))
                            print(firmware_name + '------ Not-Found')
                            firmware_version = firmware_version.replace('(', '')
                            firmware_version = firmware_version.replace(')', '')
                            firmware_version2 = firmware_version + '_'

                            if firmware_name_lang_short not in lang:
                                lang[firmware_name_lang_short] = firmware_name_lang_short

                            file_name = firmware_name_compain1 + '_' + firmware_version2 + lang[firmware_name_lang_short] + '.zip'
                            file_name = file_name.replace('\n', '_')
                            file_name = file_name.replace('___', '_')
                            file_name = file_name.replace('__', '_')
                            file_name = file_name.replace('__', '_')
                            file_name = file_name.replace('_.zip', '.zip')

                            print(file_name)

                            if re.findall('^\d', firmware_name_model):
                                print('model has digist in first')
                                exit()

                            search_section = "SELECT * FROM `dcp_categories` WHERE category_title = %s"
                            cursor.execute(search_section, (firmware_name_model))
                            if cursor.rowcount == 0:
                                print(firmware_name_model + ' No section there')
                                section_letter = firmware_name_model[:1] + '-Series'
                                # print(section_letter)
                                search_parent_sction = "SELECT * FROM `dcp_categories` WHERE category_title = %s and category_parent_id = 191"
                                cursor.execute(search_parent_sction, (section_letter))
                                result = cursor.fetchone()
                                # print(result)
                                parent_cateogry = result['category_id']
                                parent_cateogry_title = result['category_title']
                                # print(parent_cateogry)
                                if firmware_name_model not in Models_Name:
                                    Models_Name[firmware_name_model] = firmware_name_model
                                print('Create New Section: ' + firmware_name_model )
                                create_new_category = "INSERT INTO `dcp_categories`(`category_title`, `category_desc`, `category_status`, `category_parent_id`, `category_parent_title`, `category_disfree`, category_icon, category_visits) VALUE (%s, %s, %s, %s, %s, %s, %s, %s)"

                                cursor.execute(create_new_category, (firmware_name_model, Models_Name[firmware_name_model], 1, parent_cateogry, parent_cateogry_title, 0, '', '1'))
                                new_cateogry_id = cursor.lastrowid
                                # print(new_cateogry_id)
                            else:
                                result = cursor.fetchone()
                                # print(result)
                                new_cateogry_id = result['category_id']
                                # print(new_cateogry_id)

                            # print(new_cateogry_id)

                            model_firmware_cateogry = "SELECT * FROM `dcp_categories` WHERE category_title = %s and category_parent_id = %s"
                            cursor.execute(model_firmware_cateogry, (firmware_name_model + ' Firmware', new_cateogry_id))
                            if cursor.rowcount == 0:
                                print('Create New Section: ' + firmware_name_model + ' Firmware')

                                create_new_category = "INSERT INTO `dcp_categories`(`category_title`, `category_desc`, `category_status`, `category_parent_id`, `category_parent_title`, `category_disfree`, category_icon, category_visits) VALUE (%s, %s, %s, %s, %s, %s, %s, %s)"

                                cursor.execute(create_new_category, (firmware_name_model + ' Firmware', firmware_name_model + ' ' + Models_Name[firmware_name_model] + ' Stock Firmware', 1, new_cateogry_id, firmware_name_model, 0, '', '1'))
                                new_cateogry_fiemware_id = cursor.lastrowid
                                # print(new_cateogry_fiemware_id)
                            else:
                                result = cursor.fetchone()
                                # print(result)
                                new_cateogry_fiemware_id = result['category_id']
                                # print(new_cateogry_fiemware_id)

                            # print(new_cateogry_fiemware_id)

                            # print(key['type'])

                            print(firmware_version)



                            ##### check if file downlaoded before
                            # ftps = FTP_TLS('88.99.71.43')
                            # ftps.login(user='srv2', passwd='fYiBmPq9aCp3oAtoj8JUz')
                            # # ftps.set_debuglevel(1)
                            # ftps.cwd(WorkingPath)
                            # files = list(ftps.nlst())
                            # filelist = []
                            # for file in files:
                            #     ftps.cwd(file)
                            #     filelist2 = list(ftps.nlst())
                            #     filelist.append(filelist2)
                            #     ftps.cwd(WorkingPath)
                            # # print(filelist)
                            # third2 = []
                            # for third in filelist:
                            #     # print(third)
                            #     third2.extend(third)
                            #     third2.remove(".")
                            #     third2.remove("..")
                            # # print(third2)
                            # # print(third2[:1])
                            # ftps.close()



                            with open ('all.list', 'r') as f:
                                third2 = f.read()
                            if file_name in third2:
                                print(colored('This file was downloaded before: ' + file_name, 'green'))
                                File_server = re.findall('.*'+file_name+'.*', third2)[0]
                                # print(File_server)
                                # print(File_server[2:])
                                newurl = NewUrlPath + File_server[2:]
                                print(newurl)

                                write_text_info()

                            else:
                                if not firmware_name_model == '':
                                    print(file_name)
                                    print('File Download from the first time')

                                    r = downloadnow(download_link, file_name)
                                    if r != '0':
                                        print('download failed')
                                        exit()

                                    print(file_name)
                                    localfilesize = os.path.getsize(file_name)
                                    # print(localfilesize)


                                    uploadtoftp(firmware_name_model, file_name)
                                    os.remove(file_name)

                                    newurl = NewUrlPath + firmware_name_model + '/' + file_name
                                    print(newurl)

                                    write_text_info()

                                    newurl_for_file = './' + firmware_name_model + '/' + file_name
                                    print(newurl_for_file)
                                    with open('all.list', 'a+') as f:
                                        f.write('\n' + newurl_for_file)
                                    # exit()

                            # break

                            # exit()
                        else:
                            # print(cursor.fetchone())
                            print(firmware)
                            print(firmware_name + '********** Has Found')




                            # else:
                        # print(firmware_name + ' Length: ' + str(firmware_name.__len__()))
                        # print(firmware)
                    # exit()
                    print('***************************')
                        # exit()

            print(set(NON_lang))
            print(set(ALL_MODELS))
            print(len(set(ALL_MODELS)))
            print(args.page)


finally:
    connection.close()

print(colored(set(NON_MODEL), 'red'))