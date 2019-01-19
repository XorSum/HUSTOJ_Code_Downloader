# HUSTOJ 代码下载爬虫

当你在hustoj上AC了几百道题目，有一天想把代码保存下来时，就试试这个爬虫吧

## 使用方法

### 1. 安装运行环境

安装python3

``` bash
sudo apt install python3 python3-dev python3-pip
```

安装爬虫相关的库

``` bash
pip3 install requests beautifulsoup4  lxml
```

### 2. 下载代码

``` bash
git clone https://github.com/XorSum/HUSTOJ_Code_Downloader.git --depth=1
cd HUSTOJ_Code_Downloader
```


### 3. 修改信息

编辑config.json文件，把账号、密码、OJ网址、代码保存路径等信息修改为你自己的


### 4. 运行

``` bash
python3 main.py
```
