from sql.test import OPMysql
import random
import uuid

sqlOperate = OPMysql()

def random_str(num=0):
    uln = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    rs = random.sample(uln, num)  # 生成一个 指定位数的随机字符串
    a = uuid.uuid1()  # 根据 时间戳生成 uuid , 保证全球唯一
    b = ''.join(rs+str(a).split("-"))  # 生成将随机字符串 与 uuid拼接
    return b # 返回随机字符串

def unrelated():
    '''
    查询不存在的问题id
    '''
    sql = 'SELECT id, exercise_id from edu_course_exercise_qa qa where (SELECT count(1) \
        from edu_course_point_qa_ass ass where ass.course_exercise_qa_id = qa.id) = 0'
    try:
        unrelatedQas = sqlOperate.op_select(sql)
        return unrelatedQas
    except Exception as e:
        print(e)

def selectPoint(qa_id):
    '''
    关联表中查询point
    '''
    sql = 'SELECT course_id, point_id FROM edu_course_point_qa_ass WHERE course_exercise_qa_id = (SELECT id FROM edu_course_exercise_qa WHERE exercise_id = %r LIMIT 0, 1)'%(qa_id)
    try:
        result = sqlOperate.op_select(sql)
        return result
    except Exception as e:
        print(e)
        return[]

def concatSql(qa_id, point):
    '''
    生成语句sql
    '''
    table = 'edu_course_point_qa_ass'
    sqls = []
    for i in point:
        data = {
            'id': random_str(),
            'course_id': i['course_id'],
            'point_id': i['point_id'],
            'course_exercise_qa_id': qa_id
        }
        keys = ', '.join(data.keys())
        values = ', '.join('\'' + i + '\'' for i in data.values())
        sql = 'INSERT INTO {table} ({keys}) VALUES ({values})'.format(table=table, keys=keys, values=values)
        sqls.append(sql)
    return sqls

def main():
    while True:
        unrelatedQas = unrelated()
        print(unrelatedQas)
        if unrelatedQas:
            insertSqls = []
            for i in unrelatedQas:
                points = selectPoint(i['exercise_id'])
                insertSql = concatSql(i['id'], points)
                insertSqls += insertSql
            print(insertSqls)
            if not insertSqls:
                break
            sqlOperate.op_insert(insertSqls)
        else:
            break
    
if __name__ == "__main__":
    main()