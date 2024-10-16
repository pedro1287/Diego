from cProfile import run
import pstats
from pyobigram.utils import sizeof_fmt,get_file_size,createID,nice_time
from pyobigram.client import ObigramClient,inlineQueryResultArticle
from pyobigram.client import inlineKeyboardMarkup,inlineKeyboardMarkupArray,inlineKeyboardButton

from JDatabase import JsonDatabase
import shortener
import zipfile
import os
import infos
import xdlink
import datetime
import time
from pydownloader.downloader import Downloader
from ProxyCloud import ProxyCloud
import ProxyCloud
import socket
import tlmedia
import S5Crypto
import asyncio
import aiohttp
from yarl import URL
import re
import random
from draft_to_calendar import Draft2Calendar
import draft_to_calendar
import moodlews
import moodle_client
from moodle_client import MoodleClient
import S5Crypto

listproxy = []

def sign_url(token: str, url: URL):
    query: dict = dict(url.query)
    query["token"] = token
    path = "webservice" + url.path
    return url.with_path(path).with_query(query)

def nameRamdom():
    populaton = 'abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    name = "".join(random.sample(populaton,10))
    return name

def downloadFile(downloader,filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        thread = args[2]
        if thread.getStore('stop'):
            downloader.stop()
        downloadingInfo = infos.createDownloading(filename,totalBits,currentBits,speed,time,tid=thread.id)
        reply_markup = inlineKeyboardMarkup(
            r1=[inlineKeyboardButton('✘Cancelar✘', callback_data='/cancel '+str(thread.id))]
        )
        bot.editMessageText(message,downloadingInfo,reply_markup=reply_markup)
    except Exception as ex: print(str(ex))
    pass

def uploadFile(filename,currentBits,totalBits,speed,time,args):
    try:
        bot = args[0]
        message = args[1]
        originalfile = args[2]
        thread = args[3]
        downloadingInfo = infos.createUploading(filename,totalBits,currentBits,speed,time,originalfile)
        bot.editMessageText(message,downloadingInfo)
    except Exception as ex: print(str(ex))
    pass

#upload    
def processUploadFiles(filename,filesize,files,update,bot,message,thread=None,jdb=None):
    try:
        err = None
        evidence = None
        fileid = None
        user_info = jdb.get_user(update.message.sender.username)
        cloudtype = user_info['cloudtype']
        proxy = ProxyCloud.parse(user_info['proxy'])
        draftlist=[]
        if cloudtype == 'moodle':
            host = user_info['moodle_host']
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            repoid = user_info['moodle_repo_id']
            token = user_info['token']
            if token:
                print(token)
                bot.editMessageText(message,'🌩️Subiendo x token... ')                
                for file in files:
                    data = asyncio.run(moodlews.webservice_upload_file(host,token,file,progressfunc=uploadFile,proxy=proxy,args=(bot,message,filename,thread)))
                    print(data)
                    while not moodlews.store_exist(file):pass
                    data = moodlews.get_store(file)
                    if data[0]:
                        urls = moodlews.make_draft_urls(data[0])
                        draftlist.append({'file':file,'url':urls[0]})
                    else:
                        err = data[1]
                        bot.editMessageText(message,'Error',err)
            else:
                if host != 'https://moodle.uclv.edu.cu/' or 'https://cursad.jovenclub.cu/':
                    print('no chilvio el otro v:')
                    bot.editMessageText(message,'⚜️Subiendo x login... ')                    
                    cli = MoodleClient(host,user,passw,repoid,proxy)
                    for file in files:
                        data = asyncio.run(cli.LoginUpload(file, uploadFile, (bot, message, filename, thread)))
                        while cli.status is None: pass
                        data = cli.get_store(file)
                        if data:
                            if 'error' in data:
                                err = data['error']
                                bot.editMessageText(message,'Error',err)
                            else:
                                draftlist.append({'file': file, 'url': data['url']})
                pass
        return draftlist,err
   #     return None,err
    except:pass

def processFile(update,bot,message,file,thread=None,jdb=None):
    print(file)
    user_info = jdb.get_user(update.message.sender.username)
    name =''
    if user_info['rename'] == 1:
        ext = file.split('.')[-1]
        if '7z.' in file:
            ext1 = file.split('.')[-2]
            ext2 = file.split('.')[-1]
            name = nameRamdom() + '.'+ext1+'.'+ext2
        else:
            name = nameRamdom() + '.'+ext
    else:
        name = file
    os.rename(file,name)
    file_size = get_file_size(name)
    getUser = jdb.get_user(update.message.sender.username)
    max_file_size = 1024 * 1024 * getUser['zips']
    file_upload_count = 0
    client = None
    findex = 0
    if file_size > max_file_size:
        compresingInfo = infos.createCompresing(name,file_size,max_file_size)
        bot.editMessageText(message,compresingInfo)
        zipname = str(name).split('.')[0] + createID()
        mult_file = zipfile.MultiFile(zipname,max_file_size)
        zip = zipfile.ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
        zip.write(name)
        zip.close()
        mult_file.close()
        data,err = processUploadFiles(name,file_size,mult_file.files,update,bot,message,jdb=jdb)
        try:
            os.unlink(name)
        except:pass
        file_upload_count = len(zipfile.files)
    else:
        data,err = processUploadFiles(name,file_size,[name],update,bot,message,jdb=jdb)
        file_upload_count = 1
#    bot.editMessageText(message,'colectando Informacion...')
    evidname = ''
    files = []
    if data:
        for draft in data:
            files.append({'name':draft['file'],'directurl':draft['url']})
        if user_info['urlshort']==1:
            if len(files)>0:
                i = 0
                while i < len(files):                    
                    files[i]['directurl'] = shortener.short_url(files[i]['directurl'])
                    i+=1
        bot.deleteMessage(message)
        markup_array = []
        i=0
        while i < len(files):
            print('e un link')
            bbt = [inlineKeyboardButton(files[i]['name'],url=files[i]['directurl'])]
            if i+1 < len(files):
                print('on do o ma link')
                bbt.append(inlineKeyboardButton(files[i+1]['name'],url=files[i+1]['directurl']))
            markup_array.append(bbt)
            i+=2
        zips = getUser['zips']
        finishInfo = infos.createFinishUploading(name,file_size,zips)
        if len(files) > 0:
            txtname = str(file).split('/')[-1].split('.')[0] + '.txt'
            print(files)
            txtname = txtname.replace(' ','')
        reply_markup = inlineKeyboardMarkupArray(markup_array)
        bot.sendMessage(message.chat.id,finishInfo,parse_mode='html',reply_markup=reply_markup)
        bot.sendMessage(message.chat.id,'🔱Enlaces Draft🔱')
        sendTxt(txtname,files,update,bot)    
        host = user_info['moodle_host']      
        ####Convertir a calenario####
        if host == 'https://uvs.ltu.sld.cu/':
            bot.sendMessage(message.chat.id,'📅Enlaces de Calendario📅')
            sendTxtUvs(txtname,files,update,bot)
        if host != 'https://uvs.ltu.sld.cu/':
            user_info = jdb.get_user(update.message.sender.username)
            proxy = ProxyCloud.parse(user_info['proxy'])
            user = user_info['moodle_user']
            passw = user_info['moodle_password']
            if getUser['uploadtype'] == 'calendar':
                nuevo = []
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    nuevo.append(f['directurl']+separator)
                    fi += 1
                    parser = Draft2Calendar()
                    urls = asyncio.run(parser.sendcalendar(host,user,passw,nuevo,proxy))
              #   print('convertido con éxito a calendar',urls)
                    nuevito = []
                    token = moodlews.get_webservice_token(host,user,passw,proxy=proxy)  
                ####FIRMAR ENLACES####
                    enlaces_firmados = 0                
                    for url in urls:
                        enlaces_firmados += 1         
                        url_signed = sign_url(token, URL(url)) 
                        nuevito.append(url_signed)
                    loco = '\n'.join(map(str, nuevito))
                    fname = str(txtname)
                    with open(fname, "w") as f:
                        f.write(str(loco))
                    if len(files) == enlaces_firmados:
                        bot.sendMessage(message.chat.id,'📅Enlaces de Calendario📅')
                        bot.sendFile(update.message.chat.id,fname)
                else:
                    return        
    else:
        bot.editMessageText(message,'❌Error: ',err)

def ddl(update,bot,message,url,file_name='',thread=None,jdb=None):
    downloader = Downloader()
    file = downloader.download_url(url,progressfunc=downloadFile,args=(bot,message,thread))
    if not downloader.stoping:
        if file:
            processFile(update,bot,message,file,jdb=jdb)

def sendTxtUvs(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                jdb = JsonDatabase('database')
                jdb.check_create()
                jdb.load()               
                getUser = jdb.get_user(update.message.sender.username)
                for f in files:
                    separator = ''
                    print(f)
                    host = f['directurl'].split('/draftfile')[0]+'/'
                    linkdraft = f['directurl'].split(host)[1]
                    token = '?token='+getUser['token']
                    urls = host+'webservice/'+linkdraft+token
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(urls+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def sendTxt(name,files,update,bot):
                txt = open(name,'w')
                fi = 0
                for f in files:
                    separator = ''
                    if fi < len(files)-1:
                        separator += '\n'
                    txt.write(f['directurl']+separator)
                    fi += 1
                txt.close()
                bot.sendFile(update.message.chat.id,name)
                os.unlink(name)

def onmessage(update,bot:ObigramClient):
    try:
        thread = bot.this_thread
        username = update.message.sender.username
        #tl_admin_user = os.environ.get('tl_admin_user')

        #set in debug
        tl_admin_user = 'JAGB2021'

        jdb = JsonDatabase('database')
        jdb.check_create()
        jdb.load()

        user_info = jdb.get_user(username)
        
        if username == tl_admin_user or user_info :  # validate user
            if user_info is None:
                if username == tl_admin_user:
                    jdb.create_admin(username)
                else:
                    jdb.create_user(username)
                user_info = jdb.get_user(username)
                jdb.save()
        else:
            mensaje = "🚷No tienes acceso al bot🚷"
            reply_markup = inlineKeyboardMarkup(
                r1=[inlineKeyboardButton('📭Soporte📭',url='https://t.me/diago8888')]
            )
            bot.sendMessage(update.message.chat.id,mensaje,reply_markup=reply_markup)
            return


        msgText = ''
        try: msgText = update.message.text
        except:pass

        # comandos de admin
        if '/your_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                username = str(msgText).split(' ')[1]
                getUser = jdb.get_user(username)
                statInfo = infos.createStatAdmin(username,getUser,jdb.is_admin(username))                
                bot.sendMessage(update.message.chat.id,statInfo)
                return

        if '/add_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_user(user)
                    jdb.save()
                    msg = '👤Usted a dado acceso a @'+user+' '
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permisos❌')
            return

        if '/add_admin' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    jdb.create_admin(user)
                    jdb.save()
                    msg = '👤Usted ha dado acceso @'+user+' de admin'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permiso❌')
            return

        if '/ban_user' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    user = str(msgText).split(' ')[1]
                    if user == username:
                        bot.sendMessage(update.message.chat.id,'❌No Se Puede Banear Usted❌')
                        return
                    jdb.remove(user)
                    jdb.save()
                    msg = '🚷Usted a baneado a @'+user+'🚷'
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permiso❌')
            return

        if '/add_proxy' in msgText:
            isadmin = jdb.is_admin(username)
            global listproxy
            if isadmin:
                try:
                    proxy = str(msgText).split(' ')[1]
                    listproxy.append(proxy)
                    zize = len(listproxy)-1
                    bot.sendMessage(update.message.chat.id,f'Proxy Registrado en la Posicion {zize}')
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error❌')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permiso❌')
            return

        if '/check_proxy' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    msg = 'Proxys Registrados\n'
                    cont = 0
                    for proxy in listproxy:
                        msg += str(cont) +'--'+proxy+'\n'
                        cont +=1
                    bot.sendMessage(update.message.chat.id,msg)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permiso❌')
            return

        if '/short_url' in msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                try:
                    for user in jdb.items:
                        if jdb.items[user]['urlshort']==0:
                            jdb.items[user]['urlshort'] = 1
                            continue
                        if jdb.items[user]['urlshort']==1:
                            jdb.items[user]['urlshort'] = 0
                            continue
                    jdb.save()
                    bot.sendMessage(update.message.chat.id,'✅ShortUrl Cambiado✅')
                    statInfo = infos.createStat(username, user_info, jdb.is_admin(username))

                    bot.sendMessage(update.message.chat.id, statInfo)
                except:
                    bot.sendMessage(update.message.chat.id,'❌Error❌')
            return

        if '/get_db' == msgText:
            isadmin = jdb.is_admin(username)
            if isadmin:
                bot.sendMessage(update.message.chat.id,'data👇')
                bot.sendFile(update.message.chat.id,'database.jdb')
            else:
                bot.sendMessage(update.message.chat.id,'❌No Tiene Permiso❌')
            return
        # end

        # comandos de usuario
        if '/set_proxy' in msgText:
            getUser = user_info
            if getUser:
                try:
                   pos = int(str(msgText).split(' ')[1])
                   proxy = str(listproxy[pos])
                   getUser['proxy'] = proxy
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = 'Su Proxy esta Listo'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'❌Error❌')
                return

        if '/myuser' == msgText:
            getUser = user_info
            if getUser:
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))                
                bot.sendMessage(update.message.chat.id,statInfo)
                return

        if '/zips' in msgText:
            getUser = user_info
            if getUser:
                try:
                   size = int(str(msgText).split(' ')[1])
                   getUser['zips'] = size
                   jdb.save_data_user(username,getUser)
                   jdb.save()
                   msg = 'Los zips seran de '+ sizeof_fmt(size*1024*1024)+' las partes'
                   bot.sendMessage(update.message.chat.id,msg)
                except:
                   bot.sendMessage(update.message.chat.id,'❌Error❌')
                return

        if '/acc' in msgText:
            try:
                account = str(msgText).split(' ',2)[1].split(',')
                user = account[0]
                passw = account[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_user'] = user
                    getUser['moodle_password'] = passw
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))                    
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error❌')
            return

        if '/host' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                host = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['moodle_host'] = host
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))                   
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error❌')
            return

        if '/repo' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                repoid = int(cmd[1])
                getUser = user_info
                if getUser:
                    getUser['moodle_repo_id'] = repoid
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))                 
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error❌')
            return

        if '/set_token' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                token = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['token'] = token
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '🔮Token guardado🔮'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                bot.sendMessage(update.message.chat.id,'❌Error❌')
            return

        if '/off_token' == msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['token'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '☑️Token apagado☑️'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                getUser = user_info
                if getUser:
                    getUser['token'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '☑️Token apagado☑️'
                    bot.sendMessage(update.message.chat.id,msg)
            return

        if '/get_token' == msgText:
            try:
                getUser = user_info
                if getUser:
                	host = user_info['moodle_host']
                	user = user_info['moodle_user']
                	passw = user_info['moodle_password']
                	proxy = ProxyCloud.parse(user_info['proxy'])
                	token = moodlews.get_webservice_token(host,user,passw,proxy=proxy)
                	bot.sendMessage(update.message.chat.id,'🔮Su token es: '+token)
            except:
                getUser = user_info
                if getUser:
                    getUser['token'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))               
                    bot.sendMessage(update.message.chat.id,statInfo)
            return
               
        if '/off_proxy' == msgText:
            try:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '☑️Proxy apagado☑️'
                    bot.sendMessage(update.message.chat.id,msg)
            except:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    msg = '☑️Proxy apagado☑️'
                    bot.sendMessage(update.message.chat.id,msg)
            return
         
        if '/proxy' in msgText:
            try:
                cmd = str(msgText).split(' ',2)
                proxy = cmd[1]
                getUser = user_info
                if getUser:
                    getUser['proxy'] = proxy
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            except:
                getUser = user_info
                if getUser:
                    getUser['proxy'] = ''
                    jdb.save_data_user(username,getUser)
                    jdb.save()
                    statInfo = infos.createStat(username,user_info,jdb.is_admin(username))
                    bot.sendMessage(update.message.chat.id,statInfo)
            return

        if '/crypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy = S5Crypto.encrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🔒Proxy encryptado:\n{proxy}')
            return

        if '/decrypt' in msgText:
            proxy_sms = str(msgText).split(' ')[1]
            proxy_de = S5Crypto.decrypt(f'{proxy_sms}')
            bot.sendMessage(update.message.chat.id, f'🔓Proxy decryptado:\n{proxy_de}')
            return
  
        if '/nube1' in msgText:
            getUser = user_info
            if getUser:
                getUser['moodle_host'] = "https://eva.uo.edu.cu/"
                getUser['uploadtype'] =  "calendar"
                getUser['moodle_user'] = " "
                getUser['moodle_password'] = " "
                getUser['moodle_repo_id'] = 4
                getUser['token'] = ""
                getUser['zips'] = 50
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
                
        if '/nube2' in msgText:
            getUser = user_info
            if getUser:
                getUser['moodle_host'] = "https://aulauvs.gtm.sld.cu/"
                getUser['uploadtype'] =  "calendar"
                getUser['moodle_user'] = "diago"
                getUser['moodle_password'] = "Diagogoogle$4"
                getUser['moodle_repo_id'] = 4
                getUser['token'] = "92c37f59c2d6ef12f352f998f7bd27ab"
                getUser['proxy'] = "socks5://KGCHLHYEKGGJYKKEGKDDYEFJKERHCDLKHJDI"
                getUser['zips'] = 7
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
                
        if '/nube3' in msgText:
            getUser = user_info
            if getUser:
                getUser['moodle_host'] = "https://uvs.ltu.sld.cu/"
                getUser['uploadtype'] =  "calendar"
                getUser['moodle_user'] = "pedroamh01"
                getUser['moodle_password'] = "01062862726Aa*"
                getUser['token'] = "489802772f67104f0c11536d140f8322"
                getUser['moodle_repo_id'] = 4
                getUser['proxy'] = "socks5://KGCHLHYEKGGJYKKEGKDDYEFJKERHCDLKHJDI"
                getUser['zips'] = 100
                jdb.save_data_user(username,getUser)
                jdb.save()
                statInfo = infos.createStat(username,getUser,jdb.is_admin(username))
                bot.sendMessage(update.message.chat.id,statInfo)
                return
          
        message = bot.sendMessage(update.message.chat.id,'🧩Analizando...')

        thread.store('msg',message)

        if '/start' in msgText:
            mensaje = "🔱Upload-DV Free🔱\n\nHola👋 @"+username+"\nSoy un bot de descargas gratis en Cuba a través de Moodle, cualquier duda puedes contactar con el soporte."
            reply_markup = inlineKeyboardMarkup(
                r1=[inlineKeyboardButton('📭Soporte📭',url='https://t.me/diago8888')]
            )
            bot.editMessageText(message,mensaje,reply_markup=reply_markup)
        elif '/reupload' in msgText:
            try:
                file = str(msgText).split(' ')[1]
                processFile(update,bot,message,file,thread=thread,jdb=jdb)
            except:
                bot.editMessageText(message,'🚯El archivo no existe🚯')
        elif 'http' in msgText:
            url = msgText
            ddl(update,bot,message,url,file_name='',thread=thread,jdb=jdb)
        else:
            bot.editMessageText(message,'🧩Error analizando🧩')
    except Exception as ex:
           print(str(ex))
           bot.sendMessage(update.message.chat.id,str(ex))

def cancel_task(update,bot:ObigramClient):
    try:
        cmd = str(update.data)
        tid = cmd
        tcancel = bot.threads[tid]
        msg = tcancel.getStore('msg')
        tcancel.store('stop', True)
        time.sleep(3)
        bot.editMessageText(msg,'🚯Descarga cancelada...')
    except Exception as ex:
        print(str(ex))
    return
    pass

def main():
    #bot_token = os.environ.get('bot_token')
    print('🌩️Bot iniciado🌩️')
    bot_token = '5887442268:AAG-lcurssR91PbCoh-8-oY7coveUdIz8po'
    bot = ObigramClient(bot_token)
    bot.onMessage(onmessage)
    bot.onCallbackData('/cancel ',cancel_task)
    bot.run()

if __name__ == '__main__':
    try:
        main()
    except:
        main()
