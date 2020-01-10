import tensorflow as tf
#初始化一个Tensorflow的常量：Hello Google Tensorflow! 字符串，并命名为greeting作为一个计算模块
greeting = tf.constant('Hello Google Tensorflow!')
#启动一个会话
sess = tf.Session()
#使用会话执行greeting计算模块
result = sess.run(greeting)
print(result)
sess.close()