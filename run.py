import telebot
import time
from iqoptionapi.stable_api import IQ_Option
import json
from datetime import datetime, timezone

######################### CONEXÃO COM IQ OPTION ################################################################
API = IQ_Option("email@gmail.com","senha")
API.connect()

######################### CONEXÃO COM TELEBOT POR TOKEN ########################################################
bot = telebot.TeleBot('TOKEN')


lista_sinais = []


@bot.message_handler(commands=['add'])
def add_sinal(session):
    msg = str(session.text).split()
    position = len(lista_sinais)+1
    horario = msg[1]
    par = msg[2]
    entrada = msg[3]
    direcao = msg[4]
    tempo = msg[5]
    lista_sinais.append((position, horario, par, entrada, direcao, tempo))
    bot.send_message(session.chat.id, str('##### Sinal Adicionado #####\nPosição: '+str(position)+'\nHorário: '+horario+'\nParidade: '+par+'\nValor de entrada: '+entrada+'\nDireção: '+direcao+'\nExpiração: '+tempo+' minutos\n#######################'))

######################### LISTAR SINAIS ########################################################################
@bot.message_handler(commands=['listar'])
def listar_sinais(session):
    bot.send_message(session.chat.id, str('##### Listando Sinais ('+str(len(lista_sinais))+') #####'))
    for sinal in lista_sinais:
        bot.send_message(session.chat.id, str('Posição: '+str(sinal[0])+'\nHorário: '+sinal[1]+'\nParidade: '+sinal[2]+'\nValor de entrada: '+sinal[3]+'\nDireção: '+sinal[4]+'\nExpiração: '+sinal[5]+' minutos'))


######################### REMOVER SINAL #######################################################################
@bot.message_handler(commands=['remover'])
def remover_sinal(session):
    msg = str(session.text).split()
    position = msg[1]
    for sinal in lista_sinais:
        if int(sinal[0]) == int(position):
            lista_sinais.remove(sinal)          
            bot.reply_to(session, str('Sinal da posição : '+position+' removido com sucesso. '))
            

######################### Operando Sinais #####################################################################

@bot.message_handler(commands=['operar'])
def operar_lista(session):
    while len(lista_sinais) > 0:                
        for sinal in lista_sinais:
            minutos = str(datetime.now().strftime('%H:%M'))
            if str(sinal[1]) == minutos:
                status, id = API.buy_digital_spot(str(sinal[2]), int(sinal[3]), str(sinal[4]), int(sinal[5]))
                if status:
                    while True:                    
                        resultado, valor = API.check_win_digital_v2(id)
                        if resultado:
                            if valor > 0:
                                bot.send_message(session.chat.id, str('###### Resultado: Win ######\nDados Op:'+sinal[2]+' | '+str(sinal[3])+',00 | '+sinal[4]+' | '+str(sinal[5])+' min\nLucro: '+str(round(valor,2))+'\n####################'))                                                                
                                lista_sinais.remove(sinal)
                                bot.send_message(session.chat.id, str('Sinal da posição : '+str(sinal[0])+' removido. '))
                                break
                            elif valor < 0:
                                bot.send_message(session.chat.id, str('###### Resultado: Loss ######\nDados Op:'+sinal[2]+' | '+str(sinal[3])+',00 | '+sinal[4]+' | '+str(sinal[5])+' min\nLucro: '+str(round(valor,2))+'\n####################'))                                                                
                                lista_sinais.remove(sinal)
                                bot.send_message(session.chat.id, str('Sinal da posição : '+str(sinal[0])+' removido. '))
                                break
                            else:
                                bot.send_message(session.chat.id, str('###### Resultado: Error na operação ######\nDados Op:'+sinal[2]+' | '+str(sinal[3])+',00 | '+sinal[4]+' | '+str(sinal[5])+' min\nLucro: Error \n####################'))                                                                
                                lista_sinais.remove(sinal)
                                bot.send_message(session.chat.id, str('Sinal da posição : '+str(sinal[0])+' removido. '))                                
                                break    


bot.polling()