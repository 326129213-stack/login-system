from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 处理跨域请求
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 启用CORS，允许前端跨域请求
CORS(app, supports_credentials=True)

db = SQLAlchemy(app)


# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# 初始化数据库
with app.app_context():
    db.create_all()


# API: 检查登录状态
@app.route('/api/check_login', methods=['GET'])
def check_login():
    if 'username' in session:
        return jsonify({
            'status': 'success',
            'username': session['username'],
            'message': '已登录'
        })
    return jsonify({
        'status': 'error',
        'message': '未登录'
    })

# API: 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    try:
        # 获取JSON数据
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 验证数据
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': '用户名和密码不能为空'
            })

        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'status': 'error',
                'message': '用户名长度需在3-20字符之间'
            })

        if len(password) < 6:
            return jsonify({
                'status': 'error',
                'message': '密码至少需要6个字符'
            })

        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': '用户名已存在'
            })

        # 创建新用户
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': '注册成功'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'注册失败: {str(e)}'
        })


# API: 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': '用户名和密码不能为空'
            })

        # 查询用户
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # 设置session
            session['username'] = username
            return jsonify({
                'status': 'success',
                'username': username,
                'message': '登录成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '用户名或密码错误'
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'登录失败: {str(e)}'
        })


# API: 用户退出
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({
        'status': 'success',
        'message': '退出成功'
    })


# 提供静态文件（可选，前端也可以用其他服务器）
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    # 先创建数据库
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5001)