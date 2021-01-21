from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.static_folder = 'static'
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbmijung


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/random/area')
def random_area():
    x_dic = db.random_info.find_one({}, {"_id": 0, 'center_x': 1})
    y_dic = db.random_info.find_one({}, {"_id": 0, 'center_y': 1})
    radius_dic = db.random_info.find_one({}, {"_id": 0, 'radius': 1})
    x = x_dic["center_x"]
    y = y_dic["center_y"]
    radius = radius_dic["radius"]
    url = 'https://dapi.kakao.com/v2/local/search/category.json?category_group_code=FD6&page=1&size=15&x={0}&y={1}+&radius={2}'.format(
        x, y, radius);
    headers = {
        "Authorization": "KakaoAK d7a2442f278d3d0e64f2da2bfe62b90a"
    }

    places = requests.get(url, headers=headers).json()
    documents = places['documents']
    for i in range(len(documents)):
        name = documents[i]['place_name']
        phone = documents[i]['phone']
        # data = requests.get(documents[i]['place_url'], headers={
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'})

        # soup = BeautifulSoup(data.text, 'html.parser')
        # image = soup.select_one("#mArticle > div.cont_essential > div:nth-child(1) > div.details_present > a > span.bg_present")

        # images = image['style']
        # print(image)
        # if not images:
        #    images = None
        
        # images=images.split('\'')[1]
        # print(image)
        # .replace(/^url(["']?/, ”).replace(/["']?)$/, ”)
        info = {'place_name': name, 'phone': phone, 'address': documents[i]['address_name'],
        'road_address': documents[i]['road_address_name'], 'place_url': documents[i]['place_url'],
        'category': documents[i]['category_name']}
        db.random_start_info.insert_one(info)


    return places


@app.route('/random/start', methods=['POST'])
def post_random_start():
    # index.html에서 데이터 받기
    location_receive = request.form['location_give']
    center_x_receive = request.form['center_x_give']
    center_y_receive = request.form['center_y_give']
    radius_receive = request.form['radius_give']
    n_receive = request.form['n_give']

    random_info = {'location': location_receive, 'center_x': center_x_receive, 'center_y': center_y_receive,
                   'radius': radius_receive, 'n': n_receive}

    # mongodb에 데이터 넣기
    db.random_info.insert_one(random_info)
    random_area()
    return jsonify({'result': 'success', 'msg': '200'})


@app.route('/start')
def start():
    return render_template('start.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
