import os
from utils import Function

# Xác định đường dẫn của thư mục hiện tại
current_directory = os.getcwd()
data_directory = os.path.abspath(os.path.join(current_directory, '..', 'data'))
file_path = os.path.join(data_directory, 'text')
if not os.path.exists(file_path):
    Function.creatFolder("test")
url="https://vnno-vn-6-tf-mp3-s1-zmp3.zmdcdn.me/a2c39ad80d98e4c6bd89/517702657457667291?authen=exp=1688695994~acl=/a2c39ad80d98e4c6bd89/*~hmac=ea761049a9ed648cf3b8ab65051d39d7&fs=MTY4ODUyMzE5NDg3NHx3ZWJWNnwwfDEdUngNTMdUngMTU5LjMw"
Function.download_mp3(url,"test","Mưa rơi tháng sau","asasdasd","today")


print('Đã lưu tệp tin vào thư mục namgiang/data.')
