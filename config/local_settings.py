#DEBUG为False时后台无样式
DEBUG = True
DOMAIN = ''
ALLOWED_HOSTS = ['*']
BANK_REPO = 'D:\\Documents\\PyCharmFiles\\examination\\backup\\'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

#数据库MySQL配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'exam',
        'USER': 'root',
        'PASSWORD': '123456'
    }
}
# Redis配置
REDIS = {
    'default': {
        'HOST': '127.0.0.1',
        'PORT': 6379,
        'PASSWORD': '',
        'db': 0,
    }
}
# send e-mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'triumphares@163.com'
EMAIL_HOST_PASSWORD = 'bxbd6698'
# Email address that error messages come from.
# Default email address to use for various automated correspondence from
# the site managers.
SERVER_EMAIL = DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# People who get code error notifications.
# In the format [('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com')]
ADMINS = [(),]
# Not-necessarily-technical managers of the site. They get broken link
# notifications and other various emails.
MANAGERS = ADMINS

