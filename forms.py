from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message="请输入用户名"),
        Length(min=3, max=20, message="用户名长度必须在3-20个字符之间")
    ])
    
    email = StringField('邮箱', validators=[
        DataRequired(message="请输入邮箱"),
        Email(message="请输入有效的邮箱地址")
    ])
    
    password = PasswordField('密码', validators=[
        DataRequired(message="请输入密码"),
        Length(min=6, message="密码长度必须至少为6个字符")
    ])
    
    confirm_password = PasswordField('确认密码', validators=[
        DataRequired(message="请确认密码"),
        EqualTo('password', message="两次输入的密码必须一致")
    ])
    
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        # 检查用户名是否只包含字母、数字、下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('用户名只能包含字母、数字和下划线')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(message="请输入用户名")
    ])
    
    password = PasswordField('密码', validators=[
        DataRequired(message="请输入密码")
    ])
    
    submit = SubmitField('登录')
