#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
### WHEN            WHO         WHAT

"""
Bot do canal Brasil Linux.
"""

BOT_VERSION = '1.10'

### Aqui controlamos se trata-se de uma release candidate ou ja e
### uma versao oficial. Com isso tambem controlamos se as mensagens serao mandadas
### para mim (@FCN74) ou para o @cogumm
RELEASE_CANDIDATE = False

import telegram
from telegram import Updater, ParseMode, Emoji
from telegram.dispatcher import run_async
from time import sleep, time
from datetime import timedelta
import logging
from threading import Timer
import json
import feedparser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


TOKEN = {'rc'       : '', ### Release
         'released' : ''} ### Brasil Linux
         
BOT_IDS = {'Release'     : 123,
           'Brasillinux' : 123}   

ALLOWED_CHATS = {'brasillinux'   : -1001009715607}


### ID do BOT = 123
### ID dos ADM do BOT (FCN e cogumm, por hora)
### Convertido para dicionario pela facilidade de identificacao
ADM_IDs = {'fcn': 123, 'cogumm' : 123} 


# Lista de ADMS
ADMINS = ['Galdino0800', 'CoGUMm', 'NamelessOcculto', 'sergio_slv', 'zennsocial', 'FCN74']

### Primeiro item é o nome da função a ser chamada quando um dos proximos
### argumentos da lista for usado como comando.
###              0          1       n
HELP_CMDS = ['showHelp', 'ajuda', 'help', 'socorro', 'perdido', 'oncoto'] 
SAUD_CMDS = ['showSaudacao', 'ola Bot', 'olá Bot', 'olá Linux', 'ola Linux'] ###, 'bom dia', 'boa tarde', 'boa noite'
LINK_CMDS = ['showLink', 'link', 'links']
VOTE_CMDS = ['showVote', 'votar']
RULES_CMDS = ['showRules', 'regras', 'rules']
COURSE_CMDS = ['showCourses', 'cursos', 'curso', 'apostila', 'apostilas']
ABOUT_CMDS = ['showBotInfo', 'sobre', 'about', 'ver', 'version', 'bot']
HANGOUTS_CMDS = ['showHangouts', 'hangouts']
ADMINS_CMDS = ['showAdmins', 'admin', 'chefes', 'boss']
DUZERU_CMDS = ['showDuzeru', 'duzeru']

### Caracter de comando
CCMD = '!'

### Lista com todos os comandos
ALL_COMMANDS = [HELP_CMDS, 
                #LINK_CMDS, 
                RULES_CMDS, 
                SAUD_CMDS, 
                #COURSE_CMDS, 
                ABOUT_CMDS, 
                HANGOUTS_CMDS, 
                ADMINS_CMDS,
                DUZERU_CMDS] ###  VOTE_CMDS, retirado temporariamente

### Comandos ADM. Lembre-se, o primeiro item é a funcao a ser chamada
BOT_CMDS = ['showBotInfo', 'ver', 'bot']

### Carater Comando Adms
CCMD_ADM = '#'

ALL_COMMANDS_ADMS = [BOT_CMDS]

### Keybord com comandos
def keyboardGenerator(commandsList):
    sKBD = []
    for lc in commandsList:
        sKBD.append('"{cc}{cmd}"'.format(cc=CCMD ,cmd=lc[1]))
    cmdsStr = ','.join(sKBD)
    kbd = '{{"keyboard" : [[{cmds}]], "resize_keyboard" : true}}'.format(cmds=cmdsStr)
    return kbd
        
#KEYBOARD = keyboardGenerator([HELP_CMDS, LINK_CMDS, RULES_CMDS, ABOUT_CMDS, HANGOUTS_CMDS]) ### , VOTE_CMDS
#'{"keyboard" : [["ajuda", "link", "regras"]], "resize_keyboard" : true}'

def generateCMDList(listComandos):
    returnListOfCommands = ''
    for lc in listComandos:
        ### Cada elemento #1 é o coamndo padrao
        if lc[1] not in SAUD_CMDS:
            returnListOfCommands += CCMD+lc[1]+'\n'
    return returnListOfCommands

cmdsList = generateCMDList(ALL_COMMANDS)
cmdsListADM = generateCMDList(ALL_COMMANDS_ADMS)

### Distro list
distroList = ['Antergos', 'Arch Linux', 'CentOS', 'Clear Linux', 'Debian GNU/Linux',\
                'DuZeru', 'Elementary OS', 'Fedora', 'Gentoo GNU/Linux', 'Kali Linux', \
                'Mageia OS', 'Manjaro', 'Mint', 'Tails', 'OpenSUSE', 'Puppy Linux', \
                'Sabayon', 'Slackware', 'Zorin', 'Ubuntu', 'PCLinuxOS', 'Deepin', \
                'Chromixium', 'Simplicity', 'Bodhi', 'Chakra', 'KaOS', 'Solus', \
                'Red Hat', 'Parrot Security OS', 'BlackBox', \
                'Ultimate', 'SparkyLinux', 'Metamorphose Linux', 'Linux Educacional', 'nda']
                # Lista atualizada com a ajuda do Toca do Tux em 17-01-2016
### Aqui sorteamos a lista de distros alfabeticamente.
distroList = sorted(distroList)

# Enable Logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
### Variavel para sabermos o uptime do bot
START_TIME = time()

### Variavel HEARTBEAT para checagem do ultimo pulso
LAST_HEARTBEAT = time()

### Tempo minimo entre pulsos, em segundos
HEARTBEAT_INTERVAL = 30.0

### Funcao para salvar ultimo pulso do bot em disco.
### Será usado pelo bot Baymax para ver se esse bot
### continua respondendo...
def heartbeat():
    global LAST_HEARTBEAT
    global USERS
    ### Usamos o heartbeat para salvar dict com info dos users....
    ### caso o dicionario tenha sido modificado.
    global USERS_CHANGED
    if (USERS_CHANGED == True):
        print('Users changed...')
        if (saveDictAsJson(USERS, USERS_FILE_PATH)):
            USERS_CHANGED = False
    print('Last heartbeat was {dh}s ago. Setting new heartbeat: ♥ ♥.'.format(dh=time()-LAST_HEARTBEAT))
    LAST_HEARTBEAT = time()
    try:
        with open('heartbeat.info', 'w+') as f:
            f.write(str(LAST_HEARTBEAT))
    finally:
        timerHeartBeat = Timer(HEARTBEAT_INTERVAL, heartbeat)
        timerHeartBeat.start()

### Aqui armamos e ativamos o timer
timerHeartBeat = Timer(HEARTBEAT_INTERVAL, heartbeat)

### Var para ontar numero de mensagens. Apenas para estatística...
MESSAGE_COUNTER = 1

### Salvamos aqui o id da ultima conversa, para quando precisarmos dar um reply
last_chat_id = 0

### Aqui definimos todas funcoes que responderao a algum comando
def showHelp(bot, update):
    textHelp = loadText('newHelp.txt') 
    textHelpFMT = textHelp.format(c0 = HELP_CMDS[1],
                                  c2 = RULES_CMDS[1],
                                  c4 = ABOUT_CMDS[1],
                                  c5 = HANGOUTS_CMDS[1],
                                  c6 = ADMINS_CMDS[1],
                                  c7 = DUZERU_CMDS[1])
    sendMessage(bot, update, textToSend = textHelpFMT)

def isADM(update):
    """ Determina se username presente no update faz parte do grupo adm """
    username = update.message.from_user['username']
    return username in ADMINS

def loadText(textName):
    textsFolder = '/brasillinux/Texts/'
    try:
        with open(textsFolder+textName, 'r+', encoding='utf-8') as f:
            txt = f.read()
        return txt
    except:
        print('Erro lendo arquivo: {arq}'.format(arq=textName))
        return ''

def saveDictAsJson(dictToSave, filename):
    """
    Funcao para salvar dicionario no disco, usando o formato
    json, que alem de ser legivel para humanos tambem suporta 
    texto unicode...
    """
    try:
        with open(filename, 'w') as f:
            json.dump(dictToSave, f)
            f.close()
        print('Arquivo [{dn}] salvo ok.'.format(dn=filename))
        res = True
    except:
        print('Erro salvando arquivos [{dn}].'.format(dn=filename))
        res = False
    return res

def loadJsonAsDict(filename):
    """
    Funcao para ler dicionario do disco, usando o formato
    json, que alem de ser legivel para humanos tambem suporta 
    texto unicode...
    """
    try:
        with open(filename, 'r+') as f:
            d = json.load(f)
            f.close()
        print('Arquivo [{dn}] carregado com sucesso.'.format(dn=filename))
    except:
        print('Erro lendo arquivo [{dn}].'.format(dn=filename))
        d = {} ### Dicionario vazio. Se erro, é o que será retornado...
        
    return d

def sendMessage(bot, update, textToSend):
    """
    Send message que enviará mensagem somente se o chat_id
    estiver no dicionario ALLOWED_CHATS
    """
    if (int(update.message.chat_id) in ALLOWED_CHATS.values()):
        bot.sendMessage(update.message.chat_id,
                        text=textToSend,
                        disable_web_page_preview=True)
    else:
        print('Chat não permitido...')
        # TODO:
        # Pensar em como enviar para o grupo de ADMIN ou para os ADM_IDs
        # textNotAllowed = 'Grupo: {ct} não permitido...'.format(ct=update.message.chat_name)
        # sendMessage(bot, update, textToSend = textNotAllowed)

def showRules(bot, update):
    #regrasText  = 'Bem Vindo (a) ao grupo "Brasil Linux"\n\n'
    regrasText = loadText('rules.txt')
    print(type(regrasText))
    regrasTextFormatada = regrasText.format(jp = ADMINS[0],
                                            cogum = ADMINS[1],
                                            noculto = ADMINS[2],
                                            sergio = ADMINS[3],
                                            whoami = ADMINS[4],
                                            FCN = ADMINS[5])
    sendMessage(bot, update, textToSend = regrasTextFormatada)
    
def showHangouts(bot, update):
    textHangouts = loadText('hangouts.txt') # Não necessita ter .txt
    print(type(textHangouts))
    sendMessage(bot, update, textToSend = textHangouts)
    
def showCourses(bot, update):
    textCourses = loadText('courses.txt')
    print(type(textCourses))
    sendMessage(bot, update, textToSend = textCourses)
    
def showDuzeru(bot, update):
    textDuzeru = loadText('duzeru.txt')
    print(type(textDuzeru))
    sendMessage(bot, update, textToSend = textDuzeru)
    
def showAdmins(bot, update):
    textAdmins = loadText('admins.txt')
    print(type(textAdmins))
    adminsTextFormatada = textAdmins.format(jp = ADMINS[0],
                                            cogum = ADMINS[1],
                                            noculto = ADMINS[2],
                                            sergio = ADMINS[3],
                                            whoami = ADMINS[4],
                                            FCN = ADMINS[5])
    sendMessage(bot, update, textToSend = adminsTextFormatada)

def showSaudacao(bot, update):
    textReturn  = 'Olá @{u}!\n'.format(u=update.message.from_user['username'])
    textReturn += 'Para os comandos disponiveis, digite: {cc}{aj}'.format(cc=CCMD, aj=HELP_CMDS[1])
    sendMessage(bot, update, textToSend = textReturn)

def showLink(bot, update):
    #linkText  = 'Brasil@Linux:~# man link\n'
    #linkText += 'https://telegram.me/joinchat/AWNRQjwvCZefRiFXpZ0_wA'
    linkText = '➖➖➖🔰 Link do Grupo 🔰➖➖➖\n\n'
    linkText += 'Olá @{us}, segue o link abaixo! 🖖🏼\n\n'.format(us=update.message.from_user['username'])
    linkText += '🇧🇷 https://telegram.me/BrasilLinux 🐧'
    linkText += '\n\n➖➖➖🔰 Link do Grupo 🔰➖➖➖'
    sendMessage(bot, update, textToSend = linkText)

def any_message(bot, update):
    """ Print to console """
    ### Responde somente se chats autorizados
    ###if update.message.chat_id in ALLOWED_CHATS:
    # Save last chat_id to use in reply handler
    global last_chat_id
    last_chat_id = update.message.chat_id

    logger.info("New message\nFrom: %s\nchat_id: %d\nText: %s" %
                (update.message.from_user,
                update.message.chat_id,
                update.message.text))

def showWelcome(bot, update):
    """ Para responder quando novo user entrar no grupo"""
    ### Tá um pouco over... sMsg = '➖➖➖ 🇧🇷 BEM-VINDO AO  BRASIL LINUX 🐧➖➖➖\n\n'
    ### Se user sem username difinido, aparecerá Olá SEM @nomedeUsuário
    sUsername = update.message.new_chat_participant['username']
    if (sUsername == ''):
        sUsername = 'SEM @nomedeUsuário!'
    else:
        sUsername = '@'+sUsername
    sMsg = '👥 Olá {us}! Seja bem-vindo(a) ao 🇧🇷🐧!\n'.format(us=sUsername)
    sMsg += 'Usa qual distribuição?\n'
    sMsg += 'Para nossas regras, digite {cc}{cmd} \n\n'.format(cc=CCMD, cmd=RULES_CMDS[1])
    ### sMsg += '➖➖➖ 🇧🇷 BEM-VINDO AO  BRASIL LINUX 🐧➖➖➖'
    sendMessage(bot, update, textToSend = sMsg)
    
def showUnknowncommand(bot, update):
    """ Answer in Telegram """
    textUnknow  = update.message.text
    textResult  = 'bash: {uc}: Comando não encontrado'.format(uc=textUnknow)
    textResult += '\nTente digitar !{aj}'.format(aj=HELP_CMDS[1])
    sendMessage(bot, update, textToSend = textResult)

def showBotInfo(bot, update):
    """
    Mostra informacoes do bot. 
    """
    ### Checamos se bot é uma instancia do
    ### vision ou Braillinux
    if (bot.getMe()['id'] == BOT_IDS['Release']):
        sBotName = '☠ Release Bot ☠'
    else:
        sBotName = '🤖 Brasil Linux BOT'
    textResult  = sBotName
    textResult += '\n👾 Versão: {v}'.format(v=BOT_VERSION)
    dTime = time() - START_TIME
    sdTime = str(timedelta(seconds=dTime))
    sdTime = sdTime.split('.')[0] + '.' +sdTime.split('.')[1][0:2]
    textResult += '\n🗓 Uptime: {ut}'.format(ut=sdTime)
    textResult += '\n♥ Ultimo pulso: {pulso:.4f}s atras.'.format(pulso=time()-LAST_HEARTBEAT)
    textResult += '\n🚻 Users cadastrados: {udb}.'.format(udb=len(USERS))
    textResult += '\n✉️ Mensagens até agora: {cm}'.format(cm=MESSAGE_COUNTER)
    textResult += '\n🗣 Duvidas ou sugestões, tratar com:'
    textResult += '\n@{cgm} 😷 ou @{fcn} ☠'.format(cgm=ADMINS[1], fcn=ADMINS[5])
    sendMessage(bot, update, textToSend = textResult)

@run_async
def message(bot, update, **kwargs):
    """
    Aqui logamos toda e qualquer mensagem
    Será util para avaliarmos floods....
    Por exemplo, podemos ter um buffer (FIFO) e contabilizarmos
    os ID's. Se uma pessoa mantar mais que tres mensagens, com em menos
    de 2s de intervalo, poderia ser classificado como flood...De
    Uma mesangem de warning seria dada e os adms seriam avisados...
    """
    # Save last chat_id to use in reply handler
    global last_chat_id
    global USERS
    global USERS_CHANGED
    global MESSAGE_COUNTER
    last_chat_id = update.message.chat_id
    
    logger.info("Nova mensagem:\n\t\t\t %s,\n\t\t\t chat_id: %d,\n\t\t\t Text: %s" %
                (update.message.from_user,
                 update.message.chat_id,
                 update.message.text))
    
    
    ### Checamos se é uma mensagem de inclusão de membro no grupo
    ### Se sim, passamos os parametros para a funcao
    ### showWelcome tratar do novo usuario...
    if (update.message.new_chat_participant != None):
        ### Checamos para ver se o novo convidado não
        ### é uma das proprias instacias (vision ou brasillinux)
        if (update.message.from_user['id'] not in BOT_IDS.values()):
            showWelcome(bot, update)
        
    ### Incrementa contador de mensagens...
    MESSAGE_COUNTER += 1
    
    ### Aqui Adicionamos, caso já não exista as informaçoes do usuario
    ### ao dicionario USERS.
    user_id = int(update.message.from_user['id'])
    for u in USERS:
        print('User in DB: {u}'.format(u=u))
    if (user_id in USERS.keys()):
        print('User [{uid}] already in databse. Skiping...'.format(uid=user_id))
        USERS_CHANGED = False
    else:
        print('User <{uid}> not in databse. adding...'.format(uid=user_id))
        USERS[user_id] = {'last_name'  : update.message.from_user['last_name'],
                          'username'   : update.message.from_user['username'],
                          'first_name' : update.message.from_user['first_name']}
        USERS_CHANGED = True

# These handlers are for updates of type str. We use them to react to inputs
# on the command line interface
def cli_reply(bot, update, args): # MARKDOWN
    """
    For any update of type telegram.Update or str that contains a command, you
    can get the argument list by appending args to the function parameters.
    Here, we reply to the last active chat with the text after the command.
    """
    if last_chat_id is not 0:
        bot.sendMessage(chat_id=last_chat_id, text=' '.join(args))
    # TODO:
    # tentando fazer com que leia MARKDOWN ou HTML
    #bot.sendMessage(chat_id=last_chat_id, text=' '.join(args), parse_mode=telegram.ParseMode.MARKDOWN)
    #bot.sendPhoto(chat_id=last_chat_id, photo=' '.join(args))

def cli_noncommand(bot, update, update_queue):
    """
    You can also get the update queue as an argument in any handler by
    appending it to the argument list. Be careful with this though.
    Here, we put the input string back into the queue, but as a command.

    To learn more about those optional handler parameters, read:
    http://python-telegram-bot.readthedocs.org/en/latest/telegram.dispatcher.html
    """
    update_queue.put('/%s' % update)

def unknown_cli_command(bot, update):
    logger.warn("Command not found: %s" % update)

def errosHandler(bot, update, error):
    """ Send errors to ADM """
    logger.warn('Update %s causou o seguinte erro %s' % (update, error))
    if RELEASE_CANDIDATE:
        ID2SEND = ADM_IDs['fcn']
    else:
        ID2SEND = ADM_IDs['cogumm']
    bot.sendMessage(ID2SEND, text='Update %s causou o seguinte erro %s' % (update, error))
        
def showVote(bot, update):
    un = update.message.from_user['username']
    fn = update.message.from_user['first_name']
    idVotante = update.message.from_user['id']
    msgText  = '{f} (@{u}), a votacao será feita em privado.'.format(f=fn, u=un)
    msgText += '\nLhe enviei as opcoes... De uma olhada, por favor...'
    
    sendMessage(bot, update, textToSend = msgText)
    sendMessage(bot, update, textToSend = 'Quer votar em que, {f} ({u})'.format(f=fn, u=un))

def add_handler(tgDispatcher, cmdStr, isADM = False):
    """Funcao para adicionar os comandos a serem
       "ouvidos" pelo bot """
    posicao = 0
    callFunc = None
    for c in cmdStr:
        if (posicao == 0):
            ### Primeiro elemento da lista, é o nome da funcao a ser chamada
            callFunc = eval(c)
        else:
            ### Comandos a serem registrados...
            ### Se comando é uma saudacao, o registramos sem o 
            ### caracter de comando
            if (isADM):
                caracterComando = CCMD_ADM
            else:
                caracterComando = CCMD
                
            if c in SAUD_CMDS:
                ### Registra apenas o comando, sem ! ou #
                regexStr = '(?i){cmd}$'.format(cmd=c)
            else:
                regexStr = '^[{cc}](?i){cmd}$'.format(cc=caracterComando, cmd=c)
            
            tgDispatcher.addTelegramRegexHandler(regexStr, callFunc)
        posicao += 1

### Usado para sabermos quando o docionario com usuarios foi modificado e assim
### precisa ser salvo no disco. if custa bem menos em ciclos do que a operacao 
### de escrita no disco
USERS_CHANGED = False 
### Com esquema de versao released rodando dentro da pasta 'run', precisamos
### indicar o caminho de forma absoluta...
USERS_FILE_PATH = '/brasillinux/users.json'
### Dicionario com users do canal. O id do usuario será usado como key, sob o qual
### serão guardadas as outras informacoes do mesmo...
USERS = loadJsonAsDict(USERS_FILE_PATH)

### E aqui começamos o timer...
logging.info('Starting heartbeat...')
timerHeartBeat.start()

def main():
    ### Updater será vinculado ao token informado,
    ### no caso, o token do grupo Brail Linux se não
    ### for mais release candidate
    if RELEASE_CANDIDATE:
        TOKEN2USE = TOKEN['rc']
    else:
        TOKEN2USE = TOKEN['released']
    updater = Updater(TOKEN2USE , workers=10)

    # Get the dispatcher to register handlers (funcoes...)
    dp = updater.dispatcher
    
    ### Adiciona comandos ao handler...
    ### Loop pela lista com todos comandos
    for lc in ALL_COMMANDS:
        add_handler(dp, lc, isADM=False)
        
    ### Adiciona comandos adm ao handler
    ### É preciso por o flag isADM como true...
    for lca in ALL_COMMANDS_ADMS:
        add_handler(dp, lca, isADM=True)
    
    ### aqui tratamos comandos não reconhecidos.
    ### Tipicamente comandos procedidos por "/" que é o caracter
    ### default para comandos telegram
    dp.addUnknownTelegramCommandHandler(showUnknowncommand)
    
    ### Loga todas mensagens para o terminal
    ### Pode ser util para funcoes anti-flood
    dp.addTelegramMessageHandler(message)

    ### Aqui logamos todos erros que possam vir a acontecer...
    dp.addErrorHandler(errosHandler)

    # Start the Bot and store the update Queue, so we can insert updates
    update_queue = updater.start_polling(poll_interval=0.1, timeout=10)
    
    ### Aqui lemos o dicionarios de usuarios do disco
    ##- global USERS
    ##- USERS = 
    logging.info('Quantia de users no DB: {udb}.'.format(udb=len(USERS)))
    for u in USERS:
        logging.info('User {un}, id: {uid}'.format(un=USERS[u]['username'],uid=u))

    # Start CLI-Loop and heartbeat
    while True:
        try:
            text = raw_input()
        except NameError:
            text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue to be handled by our handlers
        elif len(text) > 0:
            update_queue.put(text)

if __name__ == '__main__':
    main()
