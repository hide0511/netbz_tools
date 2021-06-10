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

# Create your views here.

class IndexView(TemplateView):
    template_name = 'index.html'


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

                    if moji_cnt > 10000:
                        cnt_sum += 10000
                    elif moji_cnt < 1000:
                        cnt_sum += 1000
                    else:
                        cnt_sum += moji_cnt
                    
                    cnt_num += 1

                data = f'<p class="display-4">このキーワードで記事を書いた場合の推奨文字数は<span class="bg-info">{str(cnt_sum//cnt_num+300)}</span>です。</p>'

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

        url = 'https://www.google.com/search?q={}&sourceid=chrome&ie=UTF-8&num=15'

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
                    
                    for script in soup2(["script", "style"]):
                        script.decompose()
                    
                    text=soup2.get_text()
                    
                    lines= [line.strip() for line in text.splitlines()] 
                    
                    text = ''.join(line for line in lines if line)
                    
                    dc['count'] = len(text)

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
                    data = data + '<div class="bg-warning p-1 my-2"><a href="' + dc['link']+ '" target=”_blank”>' + dc['title'] + '</a></div>' 
                    
                    for d in dc['heading']:
                        if d.find('h1') == 0:
                            d = d.lstrip('h1:')
                            d = '<span class="kakomu">h1</span>' + d
                        elif d.find('h2') == 0:
                            d = d.lstrip('h2:')
                            d = '+ <span class="kakomu">h2</span>' + d
                        elif d.find('h3') == 0:
                            d = d.lstrip('h3:')
                            d = '+ + <span class="kakomu">h3</span>' + d
                        data = data + '<p>' + d + '</p>'

                #data = data.replace('h1','<span class="kakomu">h1</span>')
                #data = data.replace('h2','<span class="kakomu">h2</span>')
                #data = data.replace('h3','<span class="kakomu">h3</span>')

                return HttpResponse(data)

        return render(rq, 'heading.html')

    def getHeading(self,keyword):
        ret = []

        url = 'https://www.google.com/search?q={}&sourceid=chrome&ie=UTF-8&num=15'

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
                        heading_list.append(tag.name + ':' + tag.text.strip())
                            
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
                        data = data + '<li>' + res2  + '</li>'

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
        chrs = ["あ","い","う","え","お","か","き","く","け","こ","さ","し","す","せ","そ","た","ち","つ","て","と","な","に","ぬ","ね","の","は","ひ","ふ","へ","ほ","ま","み","む","め","も","や","ゆ","よ","ら","り","る","れ","ろ","わ","を","ん"]
        #chrs = ["あ","い","う"]
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
            sleep(random.uniform(0.05,0.5))

        return ret

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