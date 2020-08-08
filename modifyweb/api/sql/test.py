#!/usr/bin/env python
# coding=utf-8
import pymysql
from DBUtils.PooledDB import PooledDB

CONF = {
    "db":{
        # "host": "localhost",
        "host": "192.168.10.76",
        "user": "root",
        "port": 3306,
        "pass": "123456",
        "charset": "utf8",
        "database": "studying"
    }
}

class OPMysql(object):

    __pool = None

    def __init__(self):
        # 构造函数，创建数据库连接、游标
        self.connect = OPMysql.getmysqlconn()
        self.cur = self.connect.cursor(cursor=pymysql.cursors.DictCursor)


    # 数据库连接池连接
    @staticmethod
    def getmysqlconn():
        if OPMysql.__pool is None:

            # 参考 https://www.cnblogs.com/KKSoft/p/8040374.html
            __pool = PooledDB(creator=pymysql, \
                mincached=1, maxcached=20, \
                    host=CONF['db']['host'], user=CONF['db']['user'], \
                        passwd=CONF['db']['pass'], port=CONF['db']['port'], \
                                charset=CONF['db']['charset'], \
                                    db=CONF['db']['database'])
            print(__pool)
        return __pool.connection()

    # 插入\更新\删除sql
    def op_insert(self, sqls):
        # print('op_insert', sql)
        insert_nums = []
        for sql in sqls:   
            insert_num = self.cur.execute(sql)
            insert_nums.append(insert_num)
        # print('mysql sucess ', insert_num)
        self.connect.commit()
        return insert_nums

    # 查询
    def op_select(self, sql):
        # print('op_select', sql)
        self.cur.execute(sql)  # 执行sql
        select_res = self.cur.fetchall()  # 返回结果为字典
        # print('op_select', select_res)
        return select_res

    #析构时自动结束
    def __del__(self):
        self.connect.close()
        self.cur.close()

if __name__ == "__main__":
    o = OPMysql()
    
    