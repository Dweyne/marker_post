import json
from flask import Flask, jsonify, request
from flask_cors import CORS
# import sys
# import pathlib
# ROOT = pathlib.Path.cwd()
# sys.path.append(str(ROOT/'api'/'sql'))
from sql.test import OPMysql
import time

sqlOperate = OPMysql()
app = Flask(__name__)
CORS(app)

def request_parse(req_data):
    '''
        解析请求数据并以json形式返回
    '''
    if req_data.method == 'POST':
        data = req_data.json
    elif req_data.method == 'GET':
        data = req_data.args
    return data

@app.route("/getExercise", methods=["GET"])
# def getExercise():
#     '''
#         获取题目
#     '''
#     type = request_parse(request).get("type")
#     data = {
#         'code': 0,
#         'data': {},
#         'errMessage': ''
#     }
#     # cursor = conn.cursor()
#     sql = 'SELECT id, question_type, content, source, easy_error \
#         FROM edu_course_exercise WHERE question_type = %s and checked != 1 ORDER BY rand() LIMIT 1;'%(type)
#     result = getDict(sql)
#     if result:
#         result = result[0]
#         if not 'code' in result:
#             data['data'] = result
#             # 根据题干id查找问题
#             courseId = result['id']
#             qaSql = 'SELECT id, type, question, cando, total_score, answer\
#                 FROM edu_course_exercise_qa WHERE course_exercise_id = %s'%(courseId)
#             qa = getDict(qaSql)
#             for i in qa:
#                 commentSql = 'SELECT id, comment FROM edu_course_exercise_comment\
#                     WHERE course_exercise_qa_id = %s'%(i['id'])
#                 comment = getDict(commentSql)[0]
#                 i['total_score'] = float(i['total_score'])
#                 i['cando'] = bool(i['cando'])
#                 i['comment_id'] = comment['id']
#                 i['comment'] = comment['comment']
#             data['data']['question'] = qa
#     return jsonify(data)
def getExercise():
    '''
        获取题目
    '''
    type = request_parse(request).get("type")
    data = {
        'code': 0,
        'data': {},
        'errMessage': ''
    }
    qa = {
        'id': '',
        'content': '',
        'source': '',
        'easy_error': '',
        "course_id": '',
        'question_type': '',
        'question':[]
    }
    sql = "SELECT * FROM (SELECT t1.id, t1.question_type, t1.course_id, t1.content, t1.source, t1.easy_error, t2.id AS question_id, \
        t2.question, t2.cando, t2.type, t2.total_score, t2.answer, t3.id AS comment_id, t3.`comment` \
        FROM (SELECT * FROM edu_course_exercise WHERE dw_checked = 1) AS t1 \
        INNER JOIN edu_course_exercise_qa AS t2 on t2.course_exercise_id = t1.id \
        INNER JOIN edu_course_exercise_comment AS t3 ON t3.course_exercise_qa_id = t2.id \
        WHERE t2.update_date < \'2020-07-29 10:59:09\' AND t2.total_score != 0) AS t WHERE t.id = (SELECT p.id from (SELECT t1.id \
        FROM (SELECT * FROM edu_course_exercise WHERE dw_checked = 1) AS t1 \
        INNER JOIN edu_course_exercise_qa AS t2 on t2.course_exercise_id = t1.id \
        WHERE t1.dw_checked = 1 AND t2.update_date < \'2020-07-29 10:59:09\' AND t2.total_score != 0 LIMIT 1) as p);"
    result = getDict(sql)
    if result:
        qa['id'] = result[0]['id']
        qa['content'] = result[0]['content']
        qa['question_type'] = result[0]['question_type']
        qa['source'] = result[0]['source']
        qa['course_id'] = result[0]['course_id']
        qa['easy_error'] = result[0]['easy_error']
        for i in result:
            que = {
                'id': i['question_id'],
                'question': i['question'],
                'type': i['type'],
                'answer': i['answer'],
                'comment': i['comment'],
                'comment_id': i['comment_id'],
                'total_score': str(i['total_score']),
                'cando': bool(i['cando'])
            }
            qa['question'].append(que)
    # else:
    #     que = {
    #             'id': '',
    #             'question': '',
    #             'answer': '',
    #             'comment': '',
    #             'comment_id': '',
    #             'total_score': '',
    #             'cando': False
    #         }
    #     qa['question'].append(que)
    data['data'] = qa
    return jsonify(data)

@app.route("/updateExercise", methods=["POST"])
def setExercise():
    '''
        设置题目已被检查
    '''
    data = {
        'code': 0,
        'data': [],
        'errMessage': ''
    }
    exercise = request_parse(request).get('exercise')
    exerciseId = exercise['id']
    # print(exercise)
    question = exercise['question']
    exeForm = {
        'id': exerciseId,
        'question_type': exercise['question_type'],
        'course_id': exercise['course_id'],
        'content': exercise['content'],
        'easy_error': exercise['easy_error'],
        'source': exercise['source'],
        'dw_checked': 1
    }
    exeForm['is_pk'] = 1 if int(exercise['question_type']) == 1 else 0
    exes = [exeForm]
    qas = []
    comments = []
    for i in question:
        qaForm = {
            'id': i['id'],
            'course_exercise_id': exerciseId,
            'type': i['type'],
            'question': i['question'],
            'cando': 1 if i['cando'] else 0,
            'answer': i['answer'],
            'total_score': i['total_score']
        }
        commentForm = {
            'id': i['comment_id'],
            'path': ',' + str(i['comment_id']),
            'course_exercise_qa_id': i['id'],
            'comment': i['comment']
        }
        qas.append(qaForm)
        comments.append(commentForm)
    try:
        sqls = getSql(exes, 'edu_course_exercise') + getSql(qas, 'edu_course_exercise_qa') + getSql(comments, 'edu_course_exercise_comment')
        try:
            path = './api/checked_' + time.strftime('%Y-%m-%d',time.localtime(time.time())) + '.sql'
            with open(path, 'a', encoding='utf-8') as file:
                for i in sqls:
                    file.write(i)
                    file.write(';\n')
        except Exception as e:
            print(e)
            pass
        results = sqlOperate.op_insert(sqls)
        print(results)
        if results:
            data['data'] = 'ok'
    except Exception as e:
        print(e)
        data['code'] = -1
        data['errMessage'] = str(e)
        pass
    return jsonify(data)

def getSql(formDict, table):
    '''
        封装查询语句方法
    '''
    sqls = []
    for i in formDict:
        id = i['id']
        delSql = 'DELETE FROM {table} WHERE id=\'{id}\''.format(table=table, id=id)
        sqls.append(delSql)
        dataValues = list(map(lambda x: f'\'{str(x)}\'', i.values()))
        values = ', '.join(dataValues)
        keys = ', '.join(i.keys())
        sql = "INSERT INTO {table} ({keys}) VALUES ({values})".format(table=table, keys=keys, values=values)
        sqls.append(sql)
    return sqls


def getDict(sql):
    '''
        查询数据库
    '''
    try:
        # cursor.execute(sql)
        # response = cursor.fetchall()
        # results = []
        # if response:
        #     for r in response:
        #         result = {}
        #         for i,key in enumerate(cursor.description):
        #             result[key[0]] = r[i]
        #         results.append(result)
        # print(sql)
        results = sqlOperate.op_select(sql)
        # print(results)
        return results
    except Exception as e:
        # conn.rollback()
        print(e)
        return {
            'code': -1,
            'errMessage': str(e),
            'data': {}
        }

def sqlOprateFun(self, data, table):
    '''
    @description: sql操作
    @param {type}
    @return：
    '''
    # 转为字符串
    dataValues = list(map(lambda x: str(x), data.values()))
    keys = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    sql = 'UPDATE {table} ({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
    try:
        result = sqlOperate.op_insert(sql)
        return result
    except Exception as E:
        times=time.strftime('%Y-%m-%d %H:%I:%S',time.localtime(time.time()))
        with open('./api/error.log', 'a', encoding='utf-8') as file:
            file.write(repr(data['id']) + ' ' + repr(table) + repr(E) + ':' + repr(times))
            file.write('\n')
        return str(E)
    

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
