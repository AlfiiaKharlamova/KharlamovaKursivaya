#!/usr/bin/env python
# coding: utf-8

# ## Запустите все ячейки до раздела "Для пользователя"

# In[ ]:


import requests
from bs4 import BeautifulSoup
from time import sleep
from itertools import groupby
import pymorphy2
morph = pymorphy2.MorphAnalyzer()


# In[ ]:


def parsing_urls(link, search_element):
    
    """Parsing links from news agencies front page"""
    
    page = requests.get(link)
    soup = BeautifulSoup(page.text)
    find = soup.findAll('a') # looking for all links
    
    urls = []
    for l in find:
        variable = str(l.get('href')) # links to string
        if search_element in variable:
            urls.append(l.get('href'))
        sleep(0.5) # delay to avoid disconnection
    new_urls = [el for el, _ in groupby(urls)] # to remove duplicates
    
    full_urls = [link + x for x in new_urls]
    
    j = 0
    if 'lenta' in link: # loop to avoid ConnectionError while parsing Lenta headlines and news
        # program hasn't ConnectionError while parsing TASS or Izvestia headlines and news
        while j < len(full_urls):
            if 'lenta.ruhttps' in full_urls[j]:
                del full_urls[j]
            else:
                j = j + 1
    
    j = 0
    if 'kommersant' in link: # loop to avoid ConnectionError while parsing Kommersant headlines and news
        while j < len(full_urls):
            if 'kommersant.ruhttps' in full_urls[j]:
                del full_urls[j]
            elif '\t' in full_urls[j]:
                del full_urls[j]
            else:
                j = j + 1
        
    return full_urls


# In[ ]:


def parsing_heads(urls):
    
    """News headlines parser"""
    
    headlines = []
    i = 0
    while i < len(urls):
        p = requests.get(urls[i])
        s = BeautifulSoup(p.text)
        headline = s.findAll('meta', {'property':'og:title'})
        if len(headline) > 0: #to avoid index error for empty lists
            headlines.append(headline[0]['content'])
        i = i + 1
        sleep(0.5)
    return headlines

def parsing_news(urls, clss):
    
    """Bodies of news parser"""
    
    texts = []
    i = 0
    while i < len(urls):
        p = requests.get(urls[i])
        s = BeautifulSoup(p.text)
        text = s.findAll('p', {'class': clss})
        texts.append(text)
        i = i + 1
        sleep(0.5)
    return texts


# In[ ]:


def text_form(news, title):
    
    """Text formatting for easy visualization"""
    
    i = 0
    texts = news
    texts_new = []
    for r in texts:
        while i < len(r):
            texts_new.append(r[i]) 
            i = i + 1
        i = 0
                
    final_texts = []
    for r in texts_new:
        final_texts.append(r.text) # pastes text with the exception of HTML elements
    final = ' '.join(final_texts) # everything into one string
    joined_heads = ' '.join(title)
    final = joined_heads + final
    
    final = final.replace('МОСКВА', '').strip()
    final = final.replace('/ТАСС/.', '')
    final = final.replace('\xa0с', '')
    final = final.replace('Авторское право на систему визуализации содержимого портала iz.ru, а также на исходные данные, включая тексты, фотографии, аудио- и видеоматериалы, графические изображения, иные произведения и товарные знаки принадлежит ООО «МИЦ «Известия». Указанная информация охраняется в соответствии с законодательством РФ и международными соглашениями', '')
    final = final.replace('Частичное цитирование возможно только при условии гиперссылки на iz.ru', '')
    final = final.replace('АО «АБ «РОССИЯ» — партнер рубрики «Экономика»', '')
    final = final.replace('Сайт функционирует при финансовой поддержке Федерального агентства по печати и массовым коммуникациям', '')
    final = final.replace('Ответственность за содержание любых рекламных материалов, размещенных на портале, несет рекламодатель', '')
    final = final.replace('Новости, аналитика, прогнозы и другие материалы, представленные на данном сайте, не являются офертой или рекомендацией к покупке или продаже каких-либо активов', '')
    final = final.replace('Зарегистрировано Федеральной службой по надзору в сфере связи, информационных технологий и массовых коммуникаций', '')    
    final = final.replace('Свидетельства о регистрации', '')
    final = final.replace('Все права защищены © ООО «МИЦ «Известия»', '')
    final = final.replace('ЭЛ № ФС', '')
    final = final.replace('\xa0', '')
    final = final.replace('\n', '')
        
    return final


# In[ ]:


tass_urls = parsing_urls('https://tass.ru', '/8')
tass_heads = parsing_heads(tass_urls)
tass_news = parsing_news(tass_urls, None)


# In[ ]:


izvestia_urls = parsing_urls('https://iz.ru', '/2020')
izvestia_heads = parsing_heads(izvestia_urls)
izvestia_news = parsing_news(izvestia_urls, None)


# In[ ]:


kommersant_urls = parsing_urls('https://www.kommersant.ru', '/4')
kommersant_heads = parsing_heads(kommersant_urls)
kommersant_news = parsing_news(kommersant_urls, 'b-article__text')


# In[ ]:


lenta_urls = parsing_urls('https://lenta.ru', '/news')
lenta_heads = parsing_heads(lenta_urls)
lenta_news = parsing_news(lenta_urls, None)


# In[ ]:


tass_form = text_form(tass_news, tass_heads)
izvestia_form = text_form(izvestia_news, izvestia_heads)
kommersant_form = text_form(kommersant_news, kommersant_heads)
lenta_form = text_form(lenta_news, lenta_heads)


# In[ ]:


def normalize_words(result):
    
    """Getting rid of word cases"""
    
    list_of_words = []
    split_text = result.split(' ')
    for word in split_text: # brings words (except verbs) to initial form
        p = morph.parse(word)[0] 
        if('VERB' in p.tag):
            list_of_words.append(word)
        elif(~('VERB' in p.tag)):
            list_of_words.append(p.normal_form)
    norm_text = ' '.join(list_of_words).upper()
    return norm_text


# In[ ]:


tass = normalize_words(tass_form)
izvestia = normalize_words(izvestia_form)
lenta = normalize_words(lenta_form)
kommersant = normalize_words(kommersant_form)


# In[ ]:


full = tass + izvestia + lenta + kommersant


# In[ ]:


import numpy as np
import pandas as pd
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import ipywidgets as widgets


# In[ ]:


def word_cloud(newsag, cloud_title):
    
    """Word cloud generating"""
    
    STOPWORDS.update({'в', 'на', 'за', 'c', 'к', 'до', 'для', 'что', 'кроме' 'того', 'также', 'по', 'он', 'она', 'него', 'ему',
                 'им', 'о', 'об', 'его', 'так', 'все', 'только', 'как', 'сейчас', 'мы', 'был', 'надо', 'когда',
                 'это', 'будет', 'было', 'рф', 'россия', 'из', 'от', 'россии', 'за', 'нет', 'если', 'чтобы', 'сказал',
                 'меня', 'их', 'уже', 'или', 'после', 'лет', 'были', 'который', 'где', 'при', 'вы', 'согласно',
                 'того', 'этого', 'всегда', 'однако', 'есть', 'очень', 'может', 'меня', 'мне', 'не', 'ее', 'раз',
                 'да', 'вот', 'но', 'этом', 'кроме', 'которая', 'была', 'чем', 'там', 'еще', 'тогда', 'они', 'бы',
                 'же', 'год', 'году', 'года', 'годом', 'годе', 'ранее', 'потом', 'даже', 'которые', 'то', 'пока', 'через',
                 'со', 'ну', 'ли', 'более', 'можно', 'всего', 'тем', 'себя', 'из', 'из-за', 'во', 'будут', 'поэтому',
                 'перед', 'том', 'теперь', 'этот', 'кто', 'быть', 'у', 'нас', 'понедельник', 'вторник', 'среда', 'четверг', 
                 'пятница', 'суббота', 'воскресенье', 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август',
                 'сентябрь', 'октябрь', 'ноябрь', 'декабрь', 'хотя', 'этого', 'эти', 'этой', 'этих', 'этим', 'ни', 'весь', 
                 'тот', 'свой', 'такой', 'какой', 'ещё', 'еще', 'один', 'два', 'человек', 'изз', 'изза', 'наш', 'наши',
                 'нашим','нашему', 'нашими', 'нами', 'нам', 'мой', 'моему', 'время', 'страна', 'день', 'слово', 'работа', 
                 'слово', 'другой', 'ТАСС', 'сообщил', 'отметил', 'дать', 'быть', 'тысяч', 'тысяча', 'заявил', 'ситуация',
                 'должный', 'гражданин', 'россиянин', 'мая', 'тоже', 'без', 'тыс'})
    stopwords = STOPWORDS
    
    wordcloud = WordCloud(max_font_size = 60, background_color = 'white', max_words = 250, width = 250, 
                          stopwords = stopwords, height = 150, scale = 10).generate(newsag) 

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.axis("off")
    plt.tight_layout(True)
    plt.title(cloud_title, fontdict={'fontsize': 18, 'fontweight': 'semibold'}, loc='center', pad=20)
    return wordcloud


# In[ ]:


t_cl = word_cloud(tass, 'ТАСС')
iz_cl = word_cloud(izvestia, 'Известия')
kom_cl = word_cloud(kommersant, 'Коммерсант')
len_cloud = word_cloud(lenta, 'Лента')
full_cloud = word_cloud(full, 'Общее облако')


# In[ ]:


# creating a system of checkbox widget
w1 = widgets.Checkbox(value=False, description ='ТАСС', disabled=False, indent=False)
w2 = widgets.Checkbox(value=False, description ='Известия', disabled=False, indent=False)
w3 = widgets.Checkbox(value=False, description ='Коммерсант', disabled=False, indent=False)
w4 = widgets.Checkbox(value=False, description ='Лента.ru', disabled=False, indent=False)
w5 = widgets.Checkbox(value=False, description ='Общее облако', disabled=False, indent=False)


# In[ ]:


def widgets_res():
    
    """Program takes a result of user widgets input and shows word cloud which was generated earlier"""
    
    list_of_check = [w1, w2, w3, w4, w5]
    selected = []
    for i in list_of_check:
        if i.value == True:
            selected.append(i)
    
    for el in selected:
        plt.subplots() # to have an opportunity to show several clouds
        if el.description == 'ТАСС':
            word_cloud(tass, el.description)
        if el.description == 'Известия':
            word_cloud(izvestia, el.description)
        if el.description == 'Коммерсант':
            word_cloud(kommersant, el.description)
        if el.description == 'Лента.ru':
            word_cloud(lenta, el.description)
        if el.description == 'Общее облако':
            word_cloud(full, el.description)


# In[ ]:


def friq_graph():
    
    """The program calculates the frequency of entered by the user word in the text 
    and total number of words. Then it calculates the ratio of frequency to the total 
    number of words and creates a graph and a table"""
    
    quans = [] # for frequancy of word from input 
    rel = [] # for ratio
    gen = [] # for total
    
    
    # all four loops are similar
    tass_split_text = tass.split(' ')
    quan_tass = 0
    tass_words = 0
    for w in tass_split_text:
        if w == str(word): 
            quan_tass = quan_tass + 1
        else:
            tass_words = tass_words + 1
    res1 = quan_tass / (tass_words + quan_tass) # 'plus' to consider all words
    quans.append(res1)
    rel.append(quan_tass)
    gen.append(tass_words+quan_tass)

    izvestia_split_text = izvestia.split(' ')
    quan_iz = 0
    iz_words = 0
    for w in izvestia_split_text:
        if w == str(word):
            quan_iz = quan_iz + 1
        else:
            iz_words = iz_words + 1
    res2 = quan_iz / (iz_words + quan_iz)
    quans.append(res2)
    rel.append(quan_iz)
    gen.append(iz_words+quan_iz)

    kommersant_split_text = kommersant.split(' ')
    quan_kom = 0
    kom_words = 0
    for w in kommersant_split_text:
        if w == str(word):
            quan_kom = quan_kom + 1
        else:
            kom_words = kom_words + 1
    res3 = quan_kom / (kom_words + quan_kom)
    quans.append(res3)
    rel.append(quan_kom)
    gen.append(kom_words+quan_kom)
    
    lenta_split_text = lenta.split(' ')
    quan_len = 0
    len_words = 0
    for w in lenta_split_text:
        if w == str(word):
            quan_len = quan_len + 1
        else:
            len_words = len_words + 1
    res4 = quan_len / (len_words + quan_len)
    quans.append(res4)
    rel.append(quan_len)
    gen.append(len_words+quan_len)

    lst = [['ТАСС', 'Известия', 'Коммерсант', 'Лента.ru'], quans]
    lst2 = [rel, gen]
    for_graph = pd.DataFrame(lst).transpose().sort_values(by = 1) # Data Frame for qraph
    for_graph.columns = ['СМИ', 'Частота употребления слова']
    table = pd.DataFrame(lst2).transpose() # for table
    table.columns = ['Абсолютная частота', 'Количество слов']
    table.index = ['ТАСС', 'Известия', 'Коммерсант', 'Лента.ru']
    graph = sns.barplot(x = for_graph['СМИ'], y = for_graph['Частота употребления слова'], palette = 'GnBu_d')
    
    return graph, table


# # Для пользователя

# ### Здесь вы можете увидеть наглядную повестку дня в виде облаков слов, сгенерированных на основе сегодняшних новостей и заголовков четырех главных российских сетевых СМИ. Выберете один вариант или несколько для сравнения.
# 
# #### Для этого запустите следующую ячейку

# In[ ]:


print('Выберете облака слов, которые вы хотите увидеть:')
display(w1, w2, w3, w4, w5)


# #### Запустите следующую ячейку, чтобы увидеть результат

# In[ ]:


widgets_res()


# ### Вы можете посмотреть частоту употребления интересующего вас слова в каждом СМИ. Для визуализации используется относительная величена (частота употребления к общему количеству слов). Перед графиком вы увидете таблицу с абсолютными величинами.
# 
# #### Запустите следующую ячейку и введите интересующее вас слово в появившемся окне

# In[ ]:


word = input('Введите слово заглавными буквами: ')


# #### Запутстите следующую ячейку для отображения результата

# In[ ]:


friq_graph()

