from pyobigram.utils import sizeof_fmt,nice_time
import datetime
import time
import os

def dashboard():
    start_msg = '<b>f</b>\n'
    return start_msg

def text_progres(index,max,size=21,step_size=5):
    try:
        if max<1:
            max += 1
        porcent = index / max
        porcent *= 100
        porcent = round(porcent)
        make_text = ''
        index_make = 1
        make_text += '['
        while(index_make<size):
            if porcent >= index_make * step_size:make_text+='▣'
            else:make_text+='□'
            index_make+=1
        make_text += ']'
        return make_text
    except Exception as ex:
            return ''

def porcent(index,max):
    porcent = index / max
    porcent *= 100
    porcent = round(porcent)
    return porcent

def createDownloading(filename,totalBits,currentBits,speed,time,tid=''):
    msg = '📥Descargando...\n'
    msg += '' + filename + '\n'
    msg += text_progres(currentBits, totalBits) + ''
    msg += '💯Porcentaje: ' + str(porcent(currentBits, totalBits)) + '%\n'
    msg += '📥Descagado: ' + sizeof_fmt(currentBits) + '\n'
    msg += '📦Tamaño: ' + sizeof_fmt(totalBits) + '\n'
    msg += '⚡Velocidad: ' + sizeof_fmt(speed) + '/s\n'
    msg += '🕛Tiempo: ' + str(datetime.timedelta(seconds=int(time))) + 's\n\n'
    return msg

def createUploading(filename,totalBits,currentBits,speed,time,originalname=''):
    msg = '🌩️Subiendo...\n'
    msg += '' + filename + '\n'
    msg += text_progres(currentBits, totalBits) + ' '+str(porcent(currentBits,totalBits))+'%\n'
    msg += '📦Tamaño: ' + sizeof_fmt(totalBits) + '\n'
    msg += '🌩️Subido: ' + sizeof_fmt(currentBits) + '\n'
    msg += '⚡Velocidad: ' + sizeof_fmt(speed) + '/s\n'
    msg += '🕛Tiempo: ' + str(datetime.timedelta(seconds=int(time))) + 's\n\n'
    return msg

def createCompresing(filename,filesize,splitsize):
    msg = '🗜️Comprimiendo... \n\n'
    msg+= '' + str(filename)+'\n'
    msg+= '📦Tamaño: ' + str(sizeof_fmt(filesize))+'\n'
    msg+= '✂️Zips: ' + str(sizeof_fmt(splitsize))+'\n'
    msg+= '🧩# de Zips: ' + str(round(int(filesize/splitsize)+1,1))+'\n\n'
    return msg

def createFinishUploading(filename,filesize,zips):
    msg = '🔱Subida Finalizada🔱\n\n'
    msg += '📄Nombre: ' + str(filename)+'\n'
    msg += f'📦Tamaño: {str(sizeof_fmt(filesize))}\n'
    msg += '✂️Zips : ' + sizeof_fmt(zips*1024*1024) + '\n'
    msg += '⚡¡Siempre su mejor opción¡⚡'
    return msg

def createFileMsg(filename,files):
    import urllib
    if len(files)>0:
        msg= '<b>🖇Enlaces🖇</b>\n'
        for f in files:
            url = urllib.parse.unquote(f['directurl'],encoding='utf-8', errors='replace')
            #msg+= '<a href="'+f['url']+'">🔗' + f['name'] + '🔗</a>'
            msg+= "<a href='"+url+"'>🔗"+f['name']+'🔗</a>\n'
        return msg
    return ''

def createFilesMsg(evfiles):
    msg = '📑Archivos ('+str(len(evfiles))+')📑\n\n'
    i = 0
    for f in evfiles:
            try:
                fextarray = str(f['files'][0]['name']).split('.')
                fext = ''
                if len(fextarray)>=3:
                    fext = '.'+fextarray[-2]
                else:
                    fext = '.'+fextarray[-1]
                fname = f['name'] + fext
                msg+= '/txt_'+ str(i) + ' /del_'+ str(i) + '\n' + fname +'\n\n'
                i+=1
            except:pass
    return msg

def createStat(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = '🌩️Configuraciones de usuario🌩️\n\n'
    msg+= '🆔Id: @' + str(username)+'\n'
    msg+= '✂️Zips : ' + sizeof_fmt(userdata['zips']*1024*1024) + '\n'
    msgAdmin = '☑️'
    if isadmin:
        msgAdmin = '✅'
    msg+= '🎩Admin : ' + msgAdmin + '\n'
    proxy = '☑️'
    if userdata['proxy'] !='':
       proxy = '✅'
    msg+= '🛰️Proxy : ' + proxy + '\n'
    return msg

def createStatAdmin(username,userdata,isadmin):
    from pyobigram.utils import sizeof_fmt
    msg = '🌩️Configuraciones de usuario🌩️\n\n'
    msg+= '🆔Id: @' + str(username)+'\n'
    msg+= '👤Usuario: ' + str(userdata['moodle_user'])+'\n'
    msg+= '🗳️Contraseña: ' + str(userdata['moodle_password']) +'\n'
    msg+= '🌐Host: ' + str(userdata['moodle_host'])+'\n'
    if userdata['cloudtype'] == 'moodle':
        msg+= '🧩RepoID: ' + str(userdata['moodle_repo_id'])+'\n'
        msg+= '📤UpType: ' + str(userdata['uploadtype'])+'\n'
    msg+= '✂️Zips : ' + sizeof_fmt(userdata['zips']*1024*1024) + '\n'
    msgAdmin = '☑️'
    if isadmin:
        msgAdmin = '✅'
    msg+= '🎩Admin : ' + msgAdmin + '\n'
    proxy = '☑️'
    if userdata['proxy'] !='':
       proxy = '✅'
    msg+= '🛰️Proxy : ' + proxy + '\n'
    shorturl = (userdata['urlshort'] == 1)
    shortener = '☑️'
    if shorturl:
       shortener = '✅'
    msg += '🔗ShortUrl : ' + shortener
    return msg