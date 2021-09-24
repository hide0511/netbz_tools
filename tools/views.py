from django.shortcuts import render
from django.views.generic import TemplateView

from django.http import HttpResponse
from bs4 import BeautifulSoup
from time import sleep
from string import ascii_lowercase
from string import digits
import requests
import urllib.parse
import random
import whois
import re
import MeCab
import collections
import seaborn as sns

import matplotlib
from wordcloud import WordCloud

#バックエンドを指定
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import japanize_matplotlib 

import io
import base64

from django.http import JsonResponse

# Create your views here.

class AdvItem:
    def __init__(self, title,summary,cite):
        self.title = title
        self.summary = summary
        self.cite = cite

class IndexView(TemplateView):
    template_name = 'index.html'

class AnimButton(TemplateView):
    template_name = "animbutton.html"

class ReplaceView(TemplateView):
    template_name = "replace.html"

class RealTimeCntView(TemplateView):
    template_name = "realtimecnt.html"

class WordCloudView(TemplateView):
    template_name = "wordcloud.html"

    def post(self, rq):

        if rq.is_ajax():        
            if rq.method == 'POST':  # POSTの処理
                text = rq.POST.get('input_data')  # POSTで渡された値
                text = text.replace('\n', '<br>')
                #text = text.replace('\r\n', '<br>')

                result = WordCloudView.getWordCloud(self,text)


                data = '<h2>調査結果</h2>'

                if len(result) > 0:
                    word_list = []
                    for res1 in result:
                        word_list.append(res1["surface"])

                    word_chain = ' '.join(word_list)

                    spwd=["br","もの","これ","ため","それ","ところ","よう","こと","そう","ます","ので","から","など","です","する","いる","ない","あり","なく","また"]

                    #W = WordCloud(width=840, height=680, background_color='white', colormap='bone', font_path='C:\Windows\Fonts\yumin.ttf').generate(word_chain)
                    W = WordCloud(width=1000, height=680, background_color='white', max_words=300, stopwords=spwd, colormap='viridis', font_path='.fonts/ipaexg.ttf').generate(word_chain)

                    #plt.figure(figsize=(10,4))
                    plt.rcParams["figure.figsize"] = (8, 6)
                    plt.imshow(W)
                    plt.axis('off')
                    #plt.show()

                    #fig = plt.subplots(figsize=(8, 20))
                    #fig = plt.figure(facecolor="skyblue", linewidth=300, edgecolor="green")
                    #plt.title('WordCloud')
                    #plt.subplots_adjust(top=0.98,bottom = 0.03,left = 0.2,right = 0.9,hspace = 0.1)

                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png')
                    image_png = buffer.getvalue()
                    graph = base64.b64encode(image_png)
                    graph = graph.decode('utf-8')
                    buffer.close()
                    data = '<h2>WordCloud</h2>'
                    data = data + f'<img src="data:image/png;base64, {graph} " alt="">'

                else:
                    data = data + '<p>取得できる単語がありませんでした。</p>'

            d = {
                'input_data':data
            }
            return JsonResponse(d)

        return render(rq, 'wordcloud.html')

    def getWordCloud(self,text):
        text = urllib.parse.quote(text)
        url = 'https://jlp.yahooapis.jp/MAService/V1/parse'
        data = "sentence=" + text
        appid = 'dj00aiZpPTltQWZwREpBVEdyZiZzPWNvbnN1bWVyc2VjcmV0Jng9ZDg-'
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'Yahoo AppID: {0}'.format(appid),
                        'Host': 'jlp.yahooapis.jp',
                        'Content-Length': str(len(data)),
                        }
                
        request = urllib.request.Request(url, data=data.encode('utf-8'),headers=headers)
        response = urllib.request.urlopen(request)

        kousei_text = response.read()

        print(kousei_text)

        xml_soup = BeautifulSoup(kousei_text, 'lxml')

        ret_list = []
        dc = {}
        index = 0

        for result in xml_soup.find_all("word"):
            dc = {}

            dc['surface'] = result.find('surface').getText()
            dc['pos'] = result.find('pos').getText()

            if dc['pos'] == '名詞' and dc['surface'].strip() != 'br':
                ret_list.append(dc)

            index =  index + 1

        return ret_list

class KouseiFView(TemplateView):
    template_name = "kousei-f.html"

    def post(self, rq):

        if rq.is_ajax():        
            if rq.method == 'POST':  # POSTの処理
                text = rq.POST.get('input_data')  # POSTで渡された値
                text = text.replace('\n', '<br>')
                #text = text.replace('\r\n', '<br>')

                result = KouseiFView.getKousei(self,text)

                _text = text

                data = '<h2>調査結果</h2>'

                if len(result) > 0:
                    data = data + '<table class="table table-striped"><thead><tr><th>番号</th><th>対象表記</th><th>詳細情報</th><th>言い換え候補文字列</th></tr></thead><tbody>'
                    for res1 in result:
                        data = data + f'<tr><td>{res1["index"]}</td><td>{res1["surface"]}</td><td>{res1["shitekiinfo"]}</td><td>{res1["shitekiword"]}</td></tr>'
                    data = data + '</tbody></table>'
                    data = data + "<h2>校正箇所</h2>"
                    adjust_pos = 0
                    for res1 in result:
                        insdata1 = '<span style="color:#ff0000; font-size:125%; font-weight:bold;">'
                        _text = _text[:int(res1['startpos'])+adjust_pos] + insdata1 + _text[int(res1['startpos'])+adjust_pos:]
                        adjust_pos = adjust_pos + len(insdata1)    

                        insdata2 = '</span>'
                        _text = _text[:int(res1['startpos'])+int(res1['length'])+adjust_pos] + insdata2 + _text[int(res1['startpos'])+int(res1['length'])+adjust_pos:]
                        adjust_pos = adjust_pos + len(insdata2)    

                        #_text = _text.replace('\n', '<br>')
                        #_text = _text.replace('\r\n', '<br>')

                    data = data + _text
                    
                else:
                    data = data + '<p>校正候補はありません。</p>'

            d = {
                'input_data':data
            }
            return JsonResponse(d)

        return render(rq, 'kousei-f.html')

    def getKousei(self,text):

        text = urllib.parse.quote(text)
    
        print(text)

        url = 'https://jlp.yahooapis.jp/KouseiService/V1/kousei'

        data = "sentence=" + text

        appid = 'dj00aiZpPTltQWZwREpBVEdyZiZzPWNvbnN1bWVyc2VjcmV0Jng9ZDg-'

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Yahoo AppID: {0}'.format(appid),
                'Host': 'jlp.yahooapis.jp',
                'Content-Length': str(len(data)),
                }
        
        request = urllib.request.Request(url, data=data.encode('utf-8'),headers=headers)
        response = urllib.request.urlopen(request)

        kousei_text = response.read()

        print(kousei_text)

        xml_soup = BeautifulSoup(kousei_text, 'lxml')
        
        ret_list = []
        index = 1

        for result in xml_soup.find_all("result"):
            dc = {}

            dc['index'] = index
            dc['startpos'] = result.find('startpos').getText()
            dc['length'] = result.find("length").getText()
            dc['surface'] = result.find("surface").getText()
            dc['shitekiinfo'] = result.find("shitekiinfo").getText()
            dc['shitekiword'] = result.find("shitekiword").getText()

            ret_list.append(dc)

            index =  index + 1

        return ret_list

class KouseiView(TemplateView):
    template_name = "kousei.html"

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                text = param1

                text = text.replace('\n', '<br>')
                #text = text.replace('\r\n', '<br>')

                result = KouseiView.getKousei(self,text)

                _text = text

                data = ''

                if len(result) > 0:
                    data = '<table class="table table-striped"><thead><tr><th>番号</th><th>対象表記</th><th>詳細情報</th><th>言い換え候補文字列</th></tr></thead><tbody>'
                    for res1 in result:
                        data = data + f'<tr><td>{res1["index"]}</td><td>{res1["surface"]}</td><td>{res1["shitekiinfo"]}</td><td>{res1["shitekiword"]}</td></tr>'
                    data = data + '</tbody></table>'
                    data = data + "<h2>校正箇所</h2>"
                    adjust_pos = 0
                    for res1 in result:
                        insdata1 = '<span style="color:#ff0000; font-size:125%; font-weight:bold;">'
                        _text = _text[:int(res1['startpos'])+adjust_pos] + insdata1 + _text[int(res1['startpos'])+adjust_pos:]
                        adjust_pos = adjust_pos + len(insdata1)    

                        insdata2 = '</span>'
                        _text = _text[:int(res1['startpos'])+int(res1['length'])+adjust_pos] + insdata2 + _text[int(res1['startpos'])+int(res1['length'])+adjust_pos:]
                        adjust_pos = adjust_pos + len(insdata2)    

                        #_text = _text.replace('\n', '<br>')
                        #_text = _text.replace('\r\n', '<br>')

                    data = data + _text
                    
                else:
                    data = data + '<p>校正候補はありません。</p>'
                
                return HttpResponse(data)

        return render(rq, 'kousei.html')

    def getKousei(self,text):

        text = urllib.parse.quote(text)
    
        url = 'https://jlp.yahooapis.jp/KouseiService/V1/kousei'

        data = "sentence=" + text

        appid = 'dj00aiZpPTltQWZwREpBVEdyZiZzPWNvbnN1bWVyc2VjcmV0Jng9ZDg-'

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Yahoo AppID: {0}'.format(appid),
                'Host': 'jlp.yahooapis.jp',
                'Content-Length': str(len(data)),
                }
        
        request = urllib.request.Request(url, data=data.encode('utf-8'),headers=headers)
        response = urllib.request.urlopen(request)

        kousei_text = response.read()

        print(kousei_text)

        xml_soup = BeautifulSoup(kousei_text, 'lxml')
        
        ret_list = []
        index = 1

        for result in xml_soup.find_all("result"):
            dc = {}

            dc['index'] = index
            dc['startpos'] = result.find('startpos').getText()
            dc['length'] = result.find("length").getText()
            dc['surface'] = result.find("surface").getText()
            dc['shitekiinfo'] = result.find("shitekiinfo").getText()
            dc['shitekiword'] = result.find("shitekiword").getText()

            ret_list.append(dc)

            index =  index + 1

        return ret_list

class YahooKeywordView(TemplateView):
    template_name = "yahookeyword.html"

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                keyword = param1

                results = YahooKeywordView.getkeylist(self,keyword)

                data = ''

                data = data + '<h3>虫眼鏡キーワード</h3>'
                if len(results[0]) > 0:
                    for res1 in results[0]:
                        data = data + f'<li>{res1}</li>'
                else:
                    data = data + '<p>キーワードはありません。</p>'

                data = data + '<h3>広告</h3>'

                if len(results[1]) > 0:
                    for res2 in results[1]:
                        data = data + f'<li>{res2.title}</li>'
                else:
                    data = data + '<p>広告はありません。</p>'

                return HttpResponse(data)

        return render(rq, 'yahookeyword.html')

    def getkeylist(self,keyword):

        keyword_quote = urllib.parse.quote(keyword)
    
        url = 'https://search.yahoo.co.jp/search?p={}'.format(keyword_quote)
        
        data = None
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        request = urllib.request.Request(url, data, headers)
        response = urllib.request.urlopen(request)
        html = response.read()
        #time.sleep(1)
        
        #print(html)

        #html = requests.get(url)

        soup1 = BeautifulSoup(html,'html.parser')

        
        #with open('file.txt', 'w') as f:
        #    print(soup1.get_text(), file=f)
        

        items = soup1.find_all(class_="Unit__list")
        adv_items = soup1.find_all(class_="sw-Card Ad js-Ad")
        #adv_items = soup1.find_all(class_="sw-CardBase")
        
        keywordlist = []
        adv_list = []

        if len(items) >= 2:
        
            #print(items[1])
            item_lists = items[1].select('a') #下段の虫眼鏡キーワードから取得するため[1]を指定
                
            for item in item_lists:
                 keywordlist.append(item.text)

        print(len(adv_items))

        for adv_item in adv_items:
            print(adv_item.select('h3.sw-Card__titleMain')[0].text)
            a_title = adv_item.select('h3.sw-Card__titleMain')
            a_summary = adv_item.select('p.sw-Card__summary')
            a_cite = adv_item.select('cite')

            if len(a_title) > 0 and len(a_summary) > 0 and len(a_cite) > 0:
                adv_list.append(AdvItem(adv_item.select('h3.sw-Card__titleMain')[0].text,adv_item.select('p.sw-Card__summary')[0].text,adv_item.select('cite')[0].text))

        return keywordlist,adv_list

class LinkOpenerView(TemplateView):
    template_name = "linkopener.html"

class AllInTitleView(TemplateView):
    template_name = "allintitle.html"

class FrequentWordView(TemplateView):
    template_name = "frequent.html"

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                LIST_CNT = 100

                param1 = rq.GET.get("param1")  # GETパラメータ1
                keyword = param1

                words = FrequentWordView.getFrequentWord(self,keyword)

                data = ''

                c = collections.Counter(words)    

                sns.set(context="talk")
                sns.set(font='IPAexGothic')
                fig = plt.subplots(figsize=(8, 20))
                #fig = plt.figure(facecolor="skyblue", linewidth=300, edgecolor="green")
                plt.title(f'「{keyword}」の頻出キーワード')
                plt.subplots_adjust(top=0.98,bottom = 0.03,left = 0.2,right = 0.9,hspace = 0.1)
                
                sns.countplot(y=words,order=[i[0] for i in c.most_common(LIST_CNT)])

                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                image_png = buffer.getvalue()
                graph = base64.b64encode(image_png)
                graph = graph.decode('utf-8')
                buffer.close()
                data = '<h2>グラフ</h2>'
                data = data + f'<img src="data:image/png;base64, {graph} " alt="">'

                data =  data + '<h2>テーブル</h2>'                
                data = data + '<div id="resultText"><table class="table table-striped">'
                for letter, count in c.most_common(LIST_CNT):
                    data = data + f'<tr><td>{letter}</td><td>{count}</tr>'

                data = data + '</table></div>'

                #data = data.replace('h1','<span class="kakomu">h1</span>')
                #data = data.replace('h2','<span class="kakomu">h2</span>')
                #data = data.replace('h3','<span class="kakomu">h3</span>')

                return HttpResponse(data)

        return render(rq, 'frequent.html')

    def getFrequentWord(self,keyword):
        ret = []

        links = getGooleList(self,keyword)

        cnt = 0

        words=[]
        delete_list = ['し','こと','する','いる','ある','もの','なり','ため','さ','い','あり','よっ','よう','つい','いう','でき','なる']

        for link in links:
            if cnt >= 10 :
                break

            try:
                res = requests.get(link)
                sleep(0.01)

                if res.status_code == 200:

                    soup2 = BeautifulSoup(res.content,'html.parser')                   
                   
                    for script in soup2(["script", "style"]):
                        script.decompose()
                    
                    text=soup2.get_text()
                    

                    m = MeCab.Tagger ()
                    
                    node = m.parseToNode(text)
                
                    
                    while node:
                        try:
                            hinshi = node.feature.split(",")[0]
                            if hinshi in ["名詞","動詞","形容詞","形状詞","副詞"]:
                                if node.surface not in delete_list:
                                    if str(node.surface).isdigit() == False:
                                        words.append(node.surface)
                        except:
                            continue
                        finally:
                            node = node.next

                    cnt += 1
            except:
                continue


        return words

class WhoIsView(TemplateView):
    template_name = "whois.html"

    def get(self, rq):
        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                url = param1

                result = re.search('(?:https?://)?(?P<host>.*?)(?:[:#?/@]|$)', url)

                #辞書型で取得
                dc = whois.whois(result.group('host'))

                data = '<div><ul>'

                for key, value in dc.items():
                    data = data + f'<li>{key}:{value}</li>'
                data =  data + '</ul></div>'

                return HttpResponse(data)
        return render(rq, 'whois.html')

class ChrCountView(TemplateView):
    template_name = "chrcount.html"

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                keyword = param1

                result = ChrCountView.getChrCount(self,keyword)

                data = ''


                cnt_sum = 0
                cnt_num = 0
                for dc in result:
                    moji_cnt = int(dc['count'])

                    print(moji_cnt)

                    if moji_cnt > 8000:
                        cnt_sum += 8000
                    elif moji_cnt < 1000:
                        cnt_sum += 1000
                    else:
                        cnt_sum += moji_cnt
                    
                    cnt_num += 1

                data = f'<p class="display-4">このキーワードで記事を書いた場合の推奨文字数は<span class="bg-info">{str(cnt_sum//cnt_num+50)}</span>文字です。</p>'

                for dc in result:
                    data = data + '<div class="bg-warning p-1 my-2"><a href="' + dc['link']+ '" target=”_blank”>' + dc['title'] + '</a></div>'               
                    data = data + '<p>概算文字数： ' + str(int(dc['count']*0.9)) + '</p>'               

                #data = data.replace('h1','<span class="kakomu">h1</span>')
                #data = data.replace('h2','<span class="kakomu">h2</span>')
                #data = data.replace('h3','<span class="kakomu">h3</span>')

                return HttpResponse(data)

        return render(rq, 'chrcount.html')

    def getChrCount(self,keyword):
        ret = []

        links = getGooleList(self,keyword)

        cnt = 0
        for link in links:
            if cnt >= 10 :
                break

            dc = {}

            try:
                res = requests.get(link)
                sleep(0.01)


                if res.status_code == 200:

                    soup2 = BeautifulSoup(res.text,'html.parser')
                    
                    dc['title'] = soup2.title.string
                    dc['link'] = link
                    
                    for script in soup2(["script", "style"]):
                        script.decompose()
                    
                    text=soup2.get_text()
                    
                    lines= [line.strip() for line in text.splitlines()] 
                    
                    text = ''.join(line for line in lines if line)
                    
                    dc['count'] = len(text)*0.6

                    ret.append(dc)

                    cnt += 1 

            except:
                continue

                   
        return ret

class HeadingView(TemplateView):
    template_name = "suggest.html"

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                keyword = param1

                result = HeadingView.getHeading(self,keyword)

                data = ''

                for dc in result:
                    data = data + '<div class="resultSite">'
                    data = data + '<div class="bg-warning px-2 m-1"><p><span class="resultTitle">{}</span><br>'.format(dc['title']) 
                    data = data + 'URL:<a class="resultAtag mx-1 result_url" href="{}" target=”_blank”>{}</a></p></div>'.format(dc['link'],dc['link']) 
                    
                    for d in dc['heading']:
                        if d.find('h1') == 0:
                            d = d.lstrip('h1:')
                            d = '<span class="kakomu">h1</span>' + f'<span class="midashi">{d}</span>'
                        elif d.find('h2') == 0:
                            d = d.lstrip('h2:')
                            d = '+ <span class="kakomu">h2</span>' + f'<span class="midashi">{d}</span>'
                        elif d.find('h3') == 0:
                            d = d.lstrip('h3:')
                            d = '+ + <span class="kakomu">h3</span>' + f'<span class="midashi">{d}</span>'
                        data = data + '<p class="resultHeading">' + d + '</p>'
                    data = data + '</div>'
                #data = data.replace('h1','<span class="kakomu">h1</span>')
                #data = data.replace('h2','<span class="kakomu">h2</span>')
                #data = data.replace('h3','<span class="kakomu">h3</span>')

                return HttpResponse(data)

        return render(rq, 'heading.html')

    def getHeading(self,keyword):
        ret = []

        links = getGooleList(self,keyword)

        cnt = 0
        for link in links:
            if cnt >= 10 :
                break

            dc = {}

            try:
                res = requests.get(link)
                sleep(0.01)


                if res.status_code == 200:

                    soup2 = BeautifulSoup(res.content,'html.parser')
                    
                    dc['title'] = soup2.title.string
                    dc['link'] = link
                    
                    tags = soup2.find_all(['h1','h2','h3'])
                    
                    heading_list = []
                    
                    for tag in tags:
                        tagname = tag.text.strip()
                        tagname = tagname.replace(' ', '')
                        tagname = tagname.replace( '\n' , '' )
                        heading_list.append(tag.name + ':' + tagname)
                            
                    dc['heading'] = heading_list
                    ret.append(dc)

                    cnt += 1 

            except:
                continue

                   
        return ret

class SuggestView(TemplateView):
    template_name = "suggest.html"

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                keyword = param1

                result = SuggestView.getkeylist(self,keyword)

                data = ''

                for res1 in result:
                    data = data + '<p class="bg-info">' + res1[0] + '</p>'
                    for res2 in res1[1]:
                        #link = f'https://www.google.co.jp/search?q=allintitle%3A{res2}&hl=ja&pws=0&complete=0'
                        #https://www.google.com/search?ie=utf-8&oe=utf-8&hl=ja&lr=lang_ja&q=allintitle%3AGrapecity
                        #data = data + f'<li>{res2}<a class="mx-1" href="{link}" target​="_blank">allintitle</a></li>'
                        data = data + f'<li>{res2}</li>'
 
                return HttpResponse(data)

            elif rq.method == 'POST':  # POSTの処理（使用してない処理）
                keyword = rq.POST.get("input_data")  # POSTで渡された値
                result = SuggestView.getkeylist(self,keyword)
                return HttpResponse(result)
        return render(rq, 'suggest.html')

    def getkeylist(self,keyword):

    # keyword_quote = urllib.parse.quote(keyword)
        #keyword_quote = 'ipad'


        url = 'https://www.google.co.jp/complete/search?hl=ja&output=toolbar&ie=utf-8&oe=utf-8&client=Chrome&q='

        chrs = []
        #chrs = ["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん"]
        chrs = ["あ","い","う"]
        #chrs.extend(ascii_lowercase)
        #chrs.extend(digits)

        ret = []
        for ch in chrs:
            try:
                r = requests.get(url + urllib.parse.quote_plus(keyword + ' ' + ch))
            except:
                continue

            if r.status_code == 200:
                buf = r.json()
                suggests = [keyword + ' ' + ch,[ph for ph in buf[1]]]
                ret.extend([suggests])
            sleep(random.uniform(0.01,0.2))

        return ret

def getGooleList(self,keyword):

    url = 'https://www.google.com/search?q={}&hl=ja&sourceid=chrome&ie=UTF-8&num=15'

    print(keyword)

    kw = keyword
    kw = urllib.parse.quote(kw)

    url = url.format(kw)

    data = None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
    request = urllib.request.Request(url, data, headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    sleep(0.3)

    soup1 = BeautifulSoup(html,'html.parser')

    _links = soup1.select('.yuRUbf > a')

    links = [link.get('href') for link in _links]

    return links

class SuggestView_old(TemplateView):
    template_name = "suggest.html"

    def post(self,rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                param2 = rq.GET.get("param2")  # GETパラメータ2
                param3 = rq.GET.get("param3")  # GETパラメータ3
                print("****************************************************")
                return HttpResponse(param1 + param2 + param3)
            elif rq.method == 'POST':  # POSTの処理
                keyword = rq.POST.get("input_data")  # POSTで渡された値
                result = SuggestView.getkeylist(self,keyword)
                print("****************************************************")
                return HttpResponse(result)

        print("****************************************************")

        keyword = rq.POST['keyword']

        result = SuggestView.getkeylist(self,keyword)

        context = {
            'keyword': keyword,
            'keylist': result,
        }
        
        return render(rq, 'suggest.html', context)

    def get(self, rq):

        if rq.is_ajax():        
            if rq.method == 'GET':  # GETの処理
                param1 = rq.GET.get("param1")  # GETパラメータ1
                param2 = rq.GET.get("param2")  # GETパラメータ2
                param3 = rq.GET.get("param3")  # GETパラメータ3

                keyword = param1

                result = SuggestView.getkeylist(self,keyword)
                print("****************************************************")
                return HttpResponse(result)

            elif rq.method == 'POST':  # POSTの処理
                keyword = rq.POST.get("input_data")  # POSTで渡された値
                result = SuggestView.getkeylist(self,keyword)
                print("****************************************************")
                return HttpResponse(result)

        return render(rq, 'suggest.html')

    def get_context_data(self,**kwargs):
        ctxt = super().get_context_data(**kwargs)

        keyword = self.request.GET.get('kw')

        if keyword != None:
            result = SuggestView.getkeylist(self,keyword)

            ctxt['keyword'] = keyword
            ctxt['keylist'] = result
  
        return ctxt

    def getkeylist(self,keyword):

       # keyword_quote = urllib.parse.quote(keyword)

        #keyword_quote = 'ipad'


        url = 'https://www.google.co.jp/complete/search?hl=ja&output=toolbar&ie=utf-8&oe=utf-8&client=firefox&q='

        chrs = []
        chrs = ['あ','い','う','え','お','か']
        #chrs.extend(ascii_lowercase)
        chrs.extend(digits)

        ret = []
        for ch in chrs:
            buf = requests.get(url + urllib.parse.quote_plus(keyword + ' ' + ch)).json()
            suggests = [keyword + ' ' + ch,[ph for ph in buf[1]]]
            ret.extend([suggests])
            sleep(0.05)

        return ret