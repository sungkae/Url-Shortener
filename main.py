from flask import Flask, request, render_template, redirect
import sqlite3
import re
import pyperclip

BASE62 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
app = Flask(__name__)
def toBase10(str):
    count = len(str) - 1
    num = 0
    for i in str:
        index =BASE62.index(i)
        num += index*(62**count)
        count-=1

def toBase62(num):
    baselist = []
    base = len(BASE62)
    while num:
        num, remain = divmod(num, base)
        baselist.append(BASE62[remain])
    baselist.reverse()
    return ''.join(baselist)

def clicked(url):
    pyperclip.copy(url)


@app.route('/', methods = ['GET','POST'])
def hello_world():
    if request.method == 'POST':
        url = "127.0.0.1:5000/"
        origin_url =request.form['input-url']

        # 1. Database에 INSERT
        conn = sqlite3.connect('urls.db')
        cursor = conn.cursor()

        # Create table 이미 함
        # cursor.execute(''' ... ''')

        # http:// 가 없으면 href가 안되더라..
        if "http://" in origin_url or "https://" in origin_url:
            origin = origin_url
        else:
            origin ="http://" + origin_url

        symbol = (origin,)
        # Insert a row of data
        cursor.execute("SELECT id FROM urls WHERE origin = ('%s')"%(symbol))
        id = cursor.fetchone()
        # Check if exist
        if not id:
            cursor.execute("INSERT INTO urls (origin,modified,hits,salt) VALUES('%s','',0,0)"%(symbol))
            cursor.execute("SELECT id FROM urls WHERE origin = ('%s')"%(symbol))
            id = cursor.fetchone()

        # 2. BASE62로 변환
        shorten_url = toBase62(id[0])
        symbol = (shorten_url,)
        ids = (id[0],)
        # Insert shorten_url data
        sql = '''UPDATE urls SET modified = \'{0}\' WHERE id = \'{1}\''''.format(shorten_url, id[0])
        cursor.execute(sql)
        conn.commit()  # Save (commit) the changes
        conn.close()   # and Close
        # 3. 내 주소 + shorten_url [ex) 127.0.0.1/shorten_url] 리턴
        return render_template('index.html', short=url+shorten_url)

        # if
    return render_template('index.html')

@app.route('/<routeName>')
def originalizing(routeName):
    # 실패하면 돌아가는 곳
    url = "127.0.0.1:5000/"
    # 1. db에서 SELECT original_url WHERE shortened_url = routeName
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        id = cursor.execute("SELECT origin FROM urls WHERE modified = \'{}\'".format(routeName))
        orUrl = id.fetchone()
        # 2. 찾은 url 을 url에 넣기
        # link_target = orUrl
        link_target = url
        # None을 계속 찾는다... Why..? execute가 iterator라서?
        if orUrl is not None:
            link_target = orUrl[0]
    return redirect(link_target)

app.run("127.0.0.1", port=5000, threaded=True)