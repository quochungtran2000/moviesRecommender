import flask
from flask import Flask, jsonify
import csv
import json
import pandas as pd
import math



app = Flask(__name__)
print('loading data')
df = pd.read_csv('movies_metadata.csv', low_memory=False)
print('loading data success')
@app.route("/")
def hello():
    result = df[['runtime','vote_count','tagline','title','overview','vote_average']].sort_values(by=['vote_count'], ascending=False)[:10].to_json(orient="table")
    print(df[['runtime','vote_count','tagline','title']].sort_values(by=['vote_count'], ascending=False)[:10])
    parsed = json.loads(result)
    data = json.dumps(parsed, indent=4)
    return data
@app.route('/recommender')
def recommen():
    key = "The true story of technical troubles that scuttle the Apollo 13 lunar mission in 1971, risking the lives of astronaut Jim Lovell and his crew, with the failed journey turning into a thrilling saga of heroism. Drifting more than 200,000 miles from Earth, the astronauts work furiously with the ground crew to avert tragedy. The Dark Knight of Gotham City confronts a dastardly duo: Two-Face and the Riddler. Formerly District Attorney Harvey Dent, Two-Face believes Batman caused the courtroom accident which left him disfigured on one side. And Edward Nygma, computer-genius and former employee of millionaire Bruce Wayne, is out to get the philanthropist; as The Riddler. Former circus acrobat Dick Grayson, his family killed by Two-Face, becomes Wayne's ward and Batman's new partner Robin. History comes gloriously to life in Disney's epic animated tale about love and adventure in the New World. Pocahontas is a Native American woman whose father has arranged for her to marry her village's best warrior. But a vision tells her change is coming, and soon she comes face to face with it in the form of Capt. John Smith."
    keywords = [word.lower() for word in key.split()] ; key.split()
    data = df[['runtime','vote_count','tagline','title','id','overview']].sort_values(by=['vote_count'], ascending=False)[:5000]
    N = len(data)
    tf = []
    idf = {}
    for word in keywords:
        idf[word] = 0
    for row in data.itertuples():
        tempword =dict.fromkeys(keywords, 0)
        temp = {}
        temp['id'] = row.id
        check = isinstance(row.overview, str)
        res = 0
        if check :
            res = len(row.overview.split())
        for word in tempword:
            wordCount = 0
            if check:
                wordCount = row.overview.lower().split().count(word)
            if wordCount >= 1:
                idf[word]+= 1
            temp[word] = 0
            if res != 0:
                temp[word] = wordCount/res
        tf.append(temp)
    print(pd.DataFrame(data=tf))
    print('loading...')
    for key in idf:
        if idf[key] > 0:
            idf[key] = math.log(N/idf[key])
        else:
            idf[key] = math.log(N/1)
    print(idf)        
    ifMultiIdf = []
    for tfLine in tf:
        temp = {}
        for key in tfLine:
            if key != 'id':
                temp[key] = tfLine[key] * idf[key]
            else:
                temp[key] = tfLine[key]
        ifMultiIdf.append(temp)
    for row in ifMultiIdf:
        total = 0
        for key in row:
            if(key != 'id'):
                total += row[key]
        row['total']=total
    ascDataFrameSimilarity = pd.DataFrame(data=ifMultiIdf).sort_values(by='total', ascending=False)
    print(pd.DataFrame(data=ifMultiIdf))
    Recommender =  data.merge(ascDataFrameSimilarity[['id','total']], on="id").sort_values(by='total', ascending=False)[:20]
    print(Recommender)
    parsed = json.loads(Recommender.to_json(orient="table"))
    data = json.dumps(parsed, indent=4)
    return data

app.run()


