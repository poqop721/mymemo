from flask import Flask, session,render_template, jsonify, request, redirect
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from datetime import datetime
import random

app = Flask(__name__)
bcrypt = Bcrypt(app)
client = MongoClient('mongodb://testid:testpw@54.180.105.107', 27017)
db = client.mymemo 
dblog = client.login 
app.secret_key = str(random.randrange(1, 100000))

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('index.html')

## html의 showMemos() - 메모 가져오기
@app.route('/memo', methods=['GET'])
def listing():
    try :
        memos = list(db.mymemo.find({'id':session['id']}).sort('date',-1))
        for memo in memos:
            memo['_id'] = str(memo['_id']) #ObjectId로 받아온 ID값을 str로
        return jsonify({'result':'success', 'memo':memos,'logged':True,'id':session['id']})
    except :
        memos = list(db.mymemo.find({'id':''}).sort('date',-1))
        for memo in memos:
            memo['_id'] = str(memo['_id']) #ObjectId로 받아온 ID값을 str로
        return jsonify({'result':'success', 'memo':memos,'logged':False})

## html의 postMemos() - 메모 저장하기
@app.route('/memo', methods=['POST'])
def saving():
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d %H:%M:%S')
    title_recieve = request.form['title']
    text_recieve = request.form['text']
    color_recieve = request.form['color']
    id_recieve = request.form['id']
    db.mymemo.insert_one({'title':title_recieve,'text':text_recieve,'date':date_str,'changed':False,'color':color_recieve,'id':id_recieve})
    return jsonify({'result': 'success'})

## html의 deleteMemos() - 메모 삭제하기
@app.route('/deletememo', methods=['POST'])
def deleting():
    _id_recieve = request.form['_id']
    db.mymemo.delete_one({'_id':ObjectId(_id_recieve)}) #str로 변환된 Id를 다시 ObjectId로
    return jsonify({'result': 'success'})

## html의 saveUpdate() - 메모 수정하기
@app.route('/updatememo', methods=['POST'])
def updating():
    now = datetime.now()
    update_str = now.strftime('%Y-%m-%d %H:%M:%S')
    _id_recieve = request.form['_id']
    title_recieve = request.form['title']
    text_recieve = request.form['text']
    color_recieve = request.form['color']
    db.mymemo.update_one({'_id':ObjectId(_id_recieve)},{'$set':{'title':title_recieve,'text':text_recieve,'date':update_str,'changed':True,'color':color_recieve}})
    return jsonify({'result': 'success'})

@app.route('/signup', methods=['POST'])
def signup():
    id = request.form['id']
    checkId = list(dblog.login.find({'id':id}))
    print(checkId)
    if len(checkId) != 0 :
        return jsonify({'result': 'fail', 'msg':'이미 아이디가 존재합니다.'})
    pw = request.form['pw']

    pw_hash = bcrypt.generate_password_hash(pw)
      # 2. meta tag를 스크래핑하기
    dblog.login.insert_one({'id':id,'pw':pw_hash})
      # 3. mongoDB에 데이터 넣기
    return jsonify({'result': 'success', 'msg':'회원 가입에 성공했습니다!'})

@app.route('/login', methods=['POST'])
def login():
    id = request.form['id']
    pw = request.form['pw']
    checkUser = list(dblog.login.find({'id':id}))
    if len(checkUser) == 0:
        return jsonify({'result': 'fail', 'msg':'아이디가 존재하지 않습니다.'})
    elif not bcrypt.check_password_hash(checkUser[0]['pw'],pw):
        return jsonify({'result': 'fail', 'msg':'비밀번호가 틀렸습니다.'})
    else :
        session['id'] = id
        return jsonify({'result': 'success', 'id':id,'msg':'로그인 되었습니다!'})
    
@app.route('/logout')
def logOut():
   session.pop('id',None)
   return redirect('/')


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)