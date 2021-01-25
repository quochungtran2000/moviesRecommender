import flask
from flask import Flask, jsonify, request
import flask_cors
from flask_cors import CORS,cross_origin
import csv
import json
import pandas as pd
import math



app = Flask(__name__)
CORS(app)
print('loading data')
df = pd.read_csv('movies_metadata.csv', low_memory=False)
print('loading data success')

@app.route("/")
def hello():
    result = df[['runtime','vote_count','tagline','title','overview','vote_average', 'id']].sort_values(by=['vote_count'], ascending=False)[:12].to_json(orient="table")
    # print(df[['runtime','vote_count','tagline','title']].sort_values(by=['vote_count'], ascending=False)[:12])
    parsed = json.loads(result)
    data = json.dumps(parsed, indent=4)
    return data


@app.route('/recommender', methods=['POST'])
def recommen():
    # lấy overview
    key = request.get_json()["key"]
    keywords = [word.lower() for word in key.split()] ; key.split()
    data = df[['runtime','vote_count','tagline','title','vote_average','id','overview']].sort_values(by=['vote_count'], ascending=False)
    #đếm tổng số dòng
    N = len(data)
    tf = []
    idf = {}
    # khởi tạo giá trị cho từng key của idf = 0
    for word in keywords:
        idf[word] = 0
    #itertuples chuyển từ data frame sang tuples
    for row in data.itertuples():
        # tạo ra 1 object có key là word và giá trị là 0
        keys =dict.fromkeys(keywords, 0)
        # tfLine là 1 dòng của tf
        tfLine = {}
        tfLine['id'] = row.id
        # tạo biến check để kiểm tra có chữ trong overview hay không
        check = isinstance(row.overview, str)
        # tạo biến tính tổng số từ trong 1 row
        totalWord = 0
        if check :
            totalWord = len(row.overview.split())
        for key in keys:
            # tạo biến tính tổng số lần được lặp lại của một chữ
            wordCount = 0
            if check:
                # hàm count(key) để tính tổng số lần lặp lại của biến key
                wordCount = row.overview.lower().split().count(key)
            if wordCount >= 1:
                # nếu wordCount >=1 thì biến key trong idf tăng lên 1, giá trị của idf[key] tương ứng với số văn bản có chứa key
                idf[key]+= 1
            tfLine[key] = 0
            # nếu văn bản có chứ key => 
            if totalWord != 0:
                tfLine[key] = wordCount/totalWord  
        tf.append(tfLine)
    # print(pd.DataFrame(data=tf))
    # print('loading...')
    for key in idf:
        if idf[key] > 0:
            idf[key] = math.log(N/idf[key])
        else:
            idf[key] = math.log(N/1)
    # print(idf)   
    # tfMultiIdf là tf * idf     
    ifMultiIdf = []
    for tfLine in tf:
        temp = {}
        # vì 1 dòng của tf có chưa key tương ứng với id phim nên trường hợp khác id là giá trị của tf * idf
        for key in tfLine:
            if key != 'id':
                temp[key] = tfLine[key] * idf[key]
            else:
                temp[key] = tfLine[key]
        ifMultiIdf.append(temp)
    for row in ifMultiIdf:
        #tính tổng số điểm của 1 row trong tf-idf
        total = 0
        for key in row:
            if(key != 'id'):
                total += row[key]
        row['total']=total
    # sắp xếp danh giảm dần theo tổng số điểm
    ascDataFrameSimilarity = pd.DataFrame(data=ifMultiIdf).sort_values(by='total', ascending=False)
    # print('TF * IDF')
    # print(pd.DataFrame(data=ifMultiIdf))
    # merge data danh sách giảm dần theo số điểm để lấy ra các trường còn lại và lấy 20 phim có số điểm cao nhất
    Recommender =  data.merge(ascDataFrameSimilarity[['id','total']], on="id").sort_values(by='total', ascending=False)[:20]
    # print('Recommender Film')
    # print(Recommender)
    parsed = json.loads(Recommender.to_json(orient="table"))
    data = json.dumps(parsed, indent=4)
    return data

app.run()


