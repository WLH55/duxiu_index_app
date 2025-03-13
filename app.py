from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'duxiu-index-secret'

# 数据存储路径
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

# 初始化数据文件
def init_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

# 加载数据
def load_data():
    init_data_file()
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# 保存数据
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 生成图表
def generate_chart(data):
    if not data:
        return None
    
    # 准备数据
    sorted_data = sorted(data, key=lambda x: x['date'])
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_record', methods=['POST'])
def add_record():
    data = load_data()
    
    # 获取表单数据
    salary = float(request.form.get('salary', 0))
    living_cost = float(request.form.get('living_cost', 0))
    date = request.form.get('date', datetime.now().strftime('%Y-%m'))
    
    # 计算独秀指数
    if living_cost > 0:
        duxiu_index = round(salary / living_cost, 2)
    else:
        duxiu_index = 0
    
    # 创建记录
    record = {
        'date': date,
        'salary': salary,
        'living_cost': living_cost,
        'index': duxiu_index
    }
    
    # 检查是否已存在同一个月的记录
    for i, item in enumerate(data):
        if item['date'] == date:
            data[i] = record
            break
    else:
        data.append(record)
    
    # 按日期排序
    data.sort(key=lambda x: x['date'])
    
    # 保存数据
    save_data(data)
    
    # 生成图表
    chart_data = generate_chart(data)
    
    return jsonify({
        'success': True, 
        'data': data,
        'chart': chart_data
    })

@app.route('/get_data')
def get_data():
    data = load_data()
    chart_data = generate_chart(data)
    
    return jsonify({
        'success': True, 
        'data': data,
        'chart': chart_data
    })

@app.route('/delete_record', methods=['POST'])
def delete_record():
    date = request.form.get('date')
    data = load_data()
    
    # 删除指定日期的记录
    data = [item for item in data if item['date'] != date]
    
    # 保存数据
    save_data(data)
    
    # 生成图表
    chart_data = generate_chart(data)
    
    return jsonify({
        'success': True, 
        'data': data,
        'chart': chart_data
    })

if __name__ == '__main__':
    app.run(debug=True)
