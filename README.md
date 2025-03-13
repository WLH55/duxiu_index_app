# 独秀指数计算器 (Duxiu Index Calculator)

这是一个用于计算个人财务"独秀指数"的Web应用，帮助您跟踪收入与生活成本之间的关系。

## 什么是独秀指数？

独秀指数是衡量个人财务健康的一个简单指标，计算公式为：

```
独秀指数 = 月工资 ÷ 生活成本
```

该指数反映了您的收入与生活成本之间的比例关系：
- 指数 ≥ 2: 优秀（财务状况非常健康）
- 1 ≤ 指数 < 2: 良好（财务状况稳定）
- 指数 < 1: 欠佳（财务压力较大）

## 功能特性

- 记录月度收入和生活成本
- 自动计算独秀指数
- 生成直观的趋势图表
- 下载趋势图功能
- 查看和管理历史数据

# 运行截图

![image-20250313145330319](README.assets/image-20250313145330319.png)



![image-20250313145401866](README.assets/image-20250313145401866.png)



![image-20250313145417320](README.assets/image-20250313145417320.png)

## 技术栈

- 后端: Python Flask
- 前端: HTML, CSS, JavaScript, Bootstrap 5
- 数据可视化: Matplotlib
- 数据存储: JSON文件

## 安装指南

### 前提条件

- Python 3.6+ 安装
- pip 包管理器

### 步骤

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/outstanding-index.git
cd outstanding-index
```

2. **创建并激活虚拟环境** (可选但推荐)

在Windows上:
```bash
python -m venv .venv
.venv\Scripts\activate
```

在macOS/Linux上:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r duxiu_index_app/requirements.txt
```

## 运行应用

1. **启动Flask应用**

```bash
cd duxiu_index_app
python app.py
```

2. **访问应用**

打开浏览器，访问:
```
http://127.0.0.1:5000
```

## 使用说明

1. 在表单中输入年月、月工资和生活成本
2. 点击"添加/更新"按钮保存数据
3. 查看自动生成的独秀指数趋势图
4. 可以点击"下载趋势图"按钮保存图表
5. 在历史数据表格中查看和管理已记录的数据

## 数据存储

所有数据保存在`duxiu_index_app/data.json`文件中，您可以备份此文件以保留您的历史记录。

## 许可证

MIT License

## 贡献

欢迎提交问题和改进建议！
