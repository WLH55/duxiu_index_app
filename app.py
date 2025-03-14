from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from models import User, UserStore, DuxiuRecord, DuxiuStore

app = Flask(__name__)
app.config['SECRET_KEY'] = 'duxiu-index-secret'

# 初始化LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'warning'

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
DATA_FILE = os.path.join(DATA_DIR, 'records.json')

# 初始化用户存储和数据存储
user_store = UserStore(USERS_FILE)
duxiu_store = DuxiuStore(DATA_FILE)

@login_manager.user_loader
def load_user(user_id):
    return user_store.get_user_by_id(user_id)

# 主页
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        success, result = user_store.add_user(username, email, password)
        
        if success:
            flash('注册成功，现在您可以登录了！', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'注册失败: {result}', 'danger')
    
    return render_template('register.html', form=form)

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = user_store.get_user_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            flash('登录成功！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('登录失败，请检查用户名和密码', 'danger')
    
    return render_template('login.html', form=form)

# 用户注销
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功注销', 'success')
    return redirect(url_for('login'))

# 生成图表
def generate_chart(data):
    if not data or len(data) == 0:
        return None
    
    # 准备数据
    # 确保日期格式统一且可以正确排序
    for item in data:
        if not isinstance(item['date'], str):
            item['date'] = str(item['date'])
    
    # 按日期排序数据
    sorted_data = sorted(data, key=lambda x: x['date'])
    
    # 提取日期和指数值
    dates = [item['date'] for item in sorted_data]
    indices = [item['index'] for item in sorted_data]
    
    # 创建图表
    plt.figure(figsize=(10, 6))
    plt.plot(dates, indices, marker='o', linestyle='-', color='#4CAF50', linewidth=2.5)
    
    # 设置标题和标签
    plt.title('独秀指数变化趋势', fontsize=16, fontweight='bold')
    plt.xlabel('日期', fontsize=12, fontweight='bold')
    plt.ylabel('独秀指数', fontsize=12, fontweight='bold')
    
    # 设置网格和背景
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gca().set_facecolor('#f8f9fa')
    
    # 设置x轴标签旋转
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=10)
    
    # 添加数据标签
    for i, (date, index) in enumerate(zip(dates, indices)):
        plt.annotate(f'{index}', 
                    (date, index), 
                    textcoords="offset points",
                    xytext=(0,10), 
                    ha='center',
                    fontsize=9,
                    fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    
    # 调整布局
    plt.tight_layout()
    
    # 将图表转换为base64编码的图片
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

@app.route('/add_record', methods=['POST'])
@login_required
def add_record():
    # 获取表单数据
    salary = float(request.form.get('salary', 0))
    living_cost = float(request.form.get('living_cost', 0))
    date = request.form.get('date', datetime.now().strftime('%Y-%m'))
    
    # 计算独秀指数
    if living_cost > 0:
        duxiu_index = round(salary / living_cost, 2)
    else:
        duxiu_index = 0
    
    # 添加记录到用户的数据中
    duxiu_store.add_or_update_record(date, salary, living_cost, duxiu_index, current_user.id)
    
    # 加载用户记录
    user_records = duxiu_store.load_user_records(current_user.id)
    records_data = [record.to_dict() for record in user_records]
    
    # 生成图表
    chart_data = generate_chart(records_data)
    
    return jsonify({
        'success': True, 
        'data': records_data,
        'chart': chart_data
    })

@app.route('/get_data')
@login_required
def get_data():
    # 加载用户记录
    user_records = duxiu_store.load_user_records(current_user.id)
    records_data = [record.to_dict() for record in user_records]
    
    # 生成图表
    chart_data = generate_chart(records_data)
    
    return jsonify({
        'success': True, 
        'data': records_data,
        'chart': chart_data
    })

@app.route('/delete_record', methods=['POST'])
@login_required
def delete_record():
    date = request.form.get('date')
    
    # 删除用户特定记录
    duxiu_store.delete_record(date, current_user.id)
    
    # 加载用户记录
    user_records = duxiu_store.load_user_records(current_user.id)
    records_data = [record.to_dict() for record in user_records]
    
    # 生成图表
    chart_data = generate_chart(records_data)
    
    return jsonify({
        'success': True, 
        'data': records_data,
        'chart': chart_data
    })

if __name__ == '__main__':
    app.run(debug=True)
