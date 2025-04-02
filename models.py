from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

# 用户模型
class User(UserMixin):
    def __init__(self, id, username, email, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
        self.is_admin = is_admin
    
    # 设置密码
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 转换为字典
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'is_admin': self.is_admin
        }

# 用户数据存储类
class UserStore:
    def __init__(self, users_file):
        self.users_file = users_file
        self._init_users_file()
        
    # 初始化用户文件
    def _init_users_file(self):
        if not os.path.exists(os.path.dirname(self.users_file)):
            os.makedirs(os.path.dirname(self.users_file))
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    # 加载所有用户
    def load_users(self):
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                users = []
                for user_data in users_data:
                    user = User(
                        id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=user_data['password_hash'],
                        is_admin=user_data.get('is_admin', False)
                    )
                    if 'created_at' in user_data:
                        try:
                            user.created_at = datetime.fromisoformat(user_data['created_at'])
                        except (ValueError, TypeError):
                            user.created_at = datetime.now()
                    users.append(user)
                return users
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    # 保存所有用户
    def save_users(self, users):
        users_data = [user.to_dict() for user in users]
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    
    # 根据ID获取用户
    def get_user_by_id(self, user_id):
        users = self.load_users()
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    # 根据用户名获取用户
    def get_user_by_username(self, username):
        users = self.load_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    # 根据邮箱获取用户
    def get_user_by_email(self, email):
        users = self.load_users()
        for user in users:
            if user.email == email:
                return user
        return None
    
    # 添加用户
    def add_user(self, username, email, password):
        users = self.load_users()
        
        # 检查用户名和邮箱是否已存在
        if self.get_user_by_username(username):
            return False, "用户名已被使用"
        
        if self.get_user_by_email(email):
            return False, "邮箱已被注册"
        
        # 生成新用户ID
        user_id = str(len(users) + 1)
        
        # 创建新用户
        new_user = User(id=user_id, username=username, email=email, password_hash=None)
        new_user.set_password(password)
        
        # 添加到用户列表并保存
        users.append(new_user)
        self.save_users(users)
        
        return True, new_user
    
    # 更新用户
    def update_user(self, user):
        users = self.load_users()
        for i, existing_user in enumerate(users):
            if existing_user.id == user.id:
                users[i] = user
                self.save_users(users)
                return True
        return False
    
    # 设置用户为管理员
    def set_admin(self, user_id, is_admin=True):
        users = self.load_users()
        user = self.get_user_by_id(user_id)
        
        if user:
            user.is_admin = is_admin
            self.update_user(user)
            return True
        return False

# 独秀指数记录模型
class DuxiuRecord:
    def __init__(self, date, salary, living_cost, index, user_id=None):
        self.date = date
        self.salary = salary
        self.living_cost = living_cost
        self.index = index
        self.user_id = user_id
    
    # 转换为字典
    def to_dict(self):
        return {
            'date': self.date,
            'salary': self.salary,
            'living_cost': self.living_cost,
            'index': self.index,
            'user_id': self.user_id
        }

# 独秀指数数据存储类
class DuxiuStore:
    def __init__(self, data_file):
        self.data_file = data_file
        self._init_data_file()
    
    # 初始化数据文件
    def _init_data_file(self):
        if not os.path.exists(os.path.dirname(self.data_file)):
            os.makedirs(os.path.dirname(self.data_file))
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    # 加载所有记录
    def load_all_records(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                records_data = json.load(f)
                records = []
                for record_data in records_data:
                    records.append(DuxiuRecord(
                        date=record_data['date'],
                        salary=record_data['salary'],
                        living_cost=record_data['living_cost'],
                        index=record_data['index'],
                        user_id=record_data.get('user_id')
                    ))
                return records
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    # 加载用户的记录
    def load_user_records(self, user_id):
        all_records = self.load_all_records()
        return [record for record in all_records if record.user_id == user_id]
    
    # 保存所有记录
    def save_records(self, records):
        records_data = [record.to_dict() for record in records]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(records_data, f, ensure_ascii=False, indent=2)
    
    # 添加或更新记录
    def add_or_update_record(self, date, salary, living_cost, index, user_id):
        all_records = self.load_all_records()
        
        # 查找是否存在相同日期和用户ID的记录
        for i, record in enumerate(all_records):
            if record.date == date and record.user_id == user_id:
                # 更新现有记录
                all_records[i] = DuxiuRecord(date, salary, living_cost, index, user_id)
                self.save_records(all_records)
                return
        
        # 添加新记录
        all_records.append(DuxiuRecord(date, salary, living_cost, index, user_id))
        self.save_records(all_records)
    
    # 删除记录
    def delete_record(self, date, user_id):
        all_records = self.load_all_records()
        all_records = [record for record in all_records if not (record.date == date and record.user_id == user_id)]
        self.save_records(all_records)
