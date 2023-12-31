import requests
from http.cookies import SimpleCookie
import traceback

from flask import Flask, request, Response, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"  # 返回格式为JSON  UTF-8


session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'X-Requested-With,Content-Type',
    'Access-Control-Allow-Methods': 'PUT,POST,GET,DELETE,OPTIONS',
    "Content-Type": "multipart/form-data"
})
sfsessionid = ""


def init_sfsessionid():
    global sfsessionid, session
    data = {
        "login": "admin@bytetrade.io",
        "password": "abcd123456",
        "next": "/",
        "remember_me": "on"
    }
    response = session.post("http://127.0.0.1:8000",    # /accounts/login/?next=/",
                            headers=session.headers, data=data)
    print("\nSession Headers after Init: ", session.headers, "\n")

    # 将原始服务器的响应返回给客户端
    headers = dict(response.headers)
    print(headers)
    set_cookie = headers.get("Set-Cookie", "")
    cookie = SimpleCookie()
    cookie.load(set_cookie)
    for key, value in cookie.items():
        if key == "sfsessionid":
            sfsessionid = value.value
    print("sfsessionid=", sfsessionid)
    return


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.before_request
def proxy():
    global sfsessionid, session
    method = request.method
    url = request.url

    if method == "GET":
        req_headers = dict(request.headers)
        if not sfsessionid:
            init_sfsessionid()

        if "/assets/bundles" in url:
            newurl = url.replace("http://127.0.0.1:5000", "http://127.0.0.1:3000")
        else:
            newurl = url.replace("http://127.0.0.1:5000", "http://127.0.0.1:8000")

        cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)
        print("======cookie_dict:", cookie_dict)
        session.cookies.update(cookie_dict if cookie_dict else {"sfsessionid": sfsessionid})
        response = session.get(newurl, headers=request.headers) # , cookies={"sfsessionid": sfsessionid},)

        print(f"\nSession Headers after GET {newurl}: ", session.headers, session.cookies, session.auth, session.proxies, "\n")

        # 将原始服务器的响应返回给客户端
        headers = dict(response.headers)
        return Response(response.content, headers=headers, status=response.status_code)

    if method == "POST":
        print("sfsessionid=", sfsessionid)
        data = None
        try:
            req_headers = dict(request.headers)
            if not sfsessionid:
                init_sfsessionid()

            data = request.get_data().decode('utf-8')
            print(data)
            print(request.data)

            if "/assets/bundles" in url:
                newurl = url.replace("http://127.0.0.1:5000", "http://127.0.0.1:3000")
            else:
                newurl = url.replace("http://127.0.0.1:5000", "http://127.0.0.1:8000")
            cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)
            print("======cookie_dict:", cookie_dict)
            session.cookies.update(cookie_dict if cookie_dict else {"sfsessionid": sfsessionid})
            response = session.post(newurl, headers=request.headers,
                                    data=request.data) #, cookies={"sfsessionid": sfsessionid})

            print(f"\nSession Headers after POST {newurl}: ", session.headers, session.cookies, session.auth, session.proxies, "\n")

            # # 将原始服务器的响应返回给客户端
            headers = dict(response.headers)
            print(headers)

            set_cookie = headers.get("Set-Cookie", "")
            if set_cookie:
                cookie = SimpleCookie()
                cookie.load(set_cookie)
                for key, value in cookie.items():
                    if key == "sfsessionid":
                        sfsessionid = value.value
                        # session.cookies.update({"sfsessionid": sfsessionid})
                        break
                print("sfsessionid=", sfsessionid)
            print(response)
            print(response.is_redirect, response.url, response.request, response.next)
            print(response.history)
            status = response.status_code
            if response.history:
                print("重定向！！！！！！")
                for r in response.history:
                    print(r.is_redirect, r.url, r.request, r.next)
                status = 302
            if status == 302:
                headers.update(
                    {
                        "Location": response.url.replace("127.0.0.1:8000", "127.0.0.1:5000"),
                        "Set-Cookie": f"sfsessionid={sfsessionid}"
                    }
                )
            return Response(response.content, status=status, headers=headers)
        except Exception:
            traceback.print_exc()
            return data


if __name__ == '__main__':
    init_sfsessionid()
    app.run()
