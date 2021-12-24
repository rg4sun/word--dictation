from datetime import time
import requests
from bs4 import BeautifulSoup
import os
import re
import shutil
import random
# Python播放MP3音频文件参考
#  https://blog.csdn.net/yzy_1996/article/details/86992770
from playsound import playsound

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

ROOT_PATH = os.getcwd()
AUDIO_PATH = os.path.join(ROOT_PATH, 'audio_data')
if not os.path.exists(AUDIO_PATH):
    os.mkdir(AUDIO_PATH)
WORD_LISTS_DIR = os.path.join(ROOT_PATH, 'word_lists')
REPORT_PATH = os.path.join(ROOT_PATH, 'dictation_reports')

def get_list_path(WORD_LISTS_DIR=WORD_LISTS_DIR):
    lists = os.listdir(WORD_LISTS_DIR)
    return [ os.path.join(WORD_LISTS_DIR, list_name) for list_name in lists]

def get_words(list_path:str)->list:
    with open(list_path, 'r') as fp:
        return fp.read().split('\n')

def download_audios(word_list:list, accent_type=0, AUDIO_SAVED_PATH=AUDIO_PATH, save_info=True):
    ''' accent_type={0:us(default), 1:en}
    '''
    # 有道单词发音api 参考 https://blog.csdn.net/humanking7/article/details/88630856
    # base_url = 'https://dict.youdao.com/w/'
    base_url = 'http://dict.youdao.com/dictvoice?type={}&audio='.format(accent_type)
    count = 0
    for word in word_list:
        count+=1
        url = base_url + word
        response = requests.get(url, headers=headers)
        audio_bitstream = response.content
        audio_save_path = os.path.join(AUDIO_SAVED_PATH, word + '.mp3')
        with open(audio_save_path, 'wb') as fp:
            fp.write(audio_bitstream)
        if save_info == False:
            return
        print('Downloading audios {}/{}...'.format(count, len(word_list)))
    print('All done! Audios saved in {}'.format(AUDIO_SAVED_PATH))

def get_explanations(word:str)->list:
    base_url = 'https://dict.youdao.com/w/'
    url = base_url + word
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    explanations = soup.select('.trans-container')[0] # 取第一个
    return re.findall('<li>(.*?)</li>', str(explanations))


def play_audio(word:str, times=1, accent_type=0, explanations=True, AUDIO_PATH=AUDIO_PATH):
    audio_path = os.path.join(AUDIO_PATH, word+'.mp3')
    if not os.path.exists(audio_path):
        print("It seems that there's no audio file of '{}', \
plz add this word to your word list or \
use search_word() function.".format(word))
        return 
    if explanations:
        print('{}'.format(word))
        for e in get_explanations(word):
            print(e)
    for i in range(times):
        playsound(audio_path)

def search_word(word:str, times=1, accent_type=0, explanations=True):
    TEMP_AUDIO = os.path.join(ROOT_PATH, 'temp_audio')
    if not os.path.exists(TEMP_AUDIO):
        os.mkdir(TEMP_AUDIO)
    download_audios([word], accent_type=accent_type, AUDIO_SAVED_PATH=TEMP_AUDIO, save_info=False)
    play_audio(word, times=times, accent_type=accent_type, explanations=explanations, AUDIO_PATH=TEMP_AUDIO)
    # python 删除文件、清空目录的方法总结
    # https://blog.csdn.net/baoxiao7872/article/details/90340163
    # https://blog.csdn.net/lidashent/article/details/121892422
    # os.removedirs(TEMP_AUDIO) # 文件夹有内容不可用
    shutil.rmtree(TEMP_AUDIO)

def audio_data_clean():
    shutil.rmtree(AUDIO_PATH)
    print('All the saved audios have been cleaned.')

def dictate(list_path:str, alphabetical=False, repeat_times=1, report_save=True, save_path=REPORT_PATH)->str:
    # print(word_list)
    print("Now let's start dictation!")
    word_list = get_words(list_path)
    list_name = re.findall('(.*?).txt', list_path.split(os.path.sep)[-1])[0] # 这里findall的结果是list，记得取出来
    if alphabetical:
        word_list.sort(reverse=False) # 大写优先（比如 Christmas < ardent）; True 为逆序
    else:
     random.shuffle(word_list)
    comparing_sheet = []
    for w in word_list:
        play_audio(w, times=repeat_times, explanations=False)
        ans = input('write ur answer here = ')
        comparing_sheet.append(ans==w)
        if report_save:
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            report_path = os.path.join(save_path, list_name + '_report.txt')
            # https://www.runoob.com/python/python-func-open.html
            with open(report_path, 'a+') as fp:
                # fp.write('{}: {} = {}\n'.format(w, ans, '✅' if ans==w else '❌'))
                fp.write('\n%-20s: %-20s = %s'%(w, ans, '✅' if ans==w else '❌'))
    result = 'Acc:{} ({}/{})'.format(sum(comparing_sheet)/len(comparing_sheet), sum(comparing_sheet), len(comparing_sheet))
    if report_save:
        with open(report_path, 'a+') as fp:
            fp.write('\n')
            fp.write('-'*50)
            fp.write('\n{}'.format(result))
    return result

# download_audios(get_words(get_list_path()[0]), accent_type=0)
# audio_data_clean()
# w = input('word = ')
# # play_audio(w, times=3)
# search_word(w)

print(dictate(get_list_path()[0]))

