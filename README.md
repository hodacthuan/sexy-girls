## Installation

### Install tools needed
```
git clone https://github.com/hodacthuan/linux-tools.git
linux-tools/cli-tools/awscli.sh
linux-tools/docker/index.sh
```
### Deploy MongoDB

```
git clone https://github.com/hodacthuan/devops-infrastructure.git
cd devops-infrastructure/mongodb

nano sexy-girls.env
./up.sh sexy-girls
```

### Deploy RedisDB

```
git clone https://github.com/hodacthuan/devops-infrastructure.git
cd devops-infrastructure/redisdb

nano sexy-girls.env
./up.sh sexy-girls
```

### Source code clone
```
ssh-keygen -o -t rsa -b 4096 -C "email@example.com"

```
Add SSH key
```bash
nano ~/.ssh/id_rsa
```
Apply SSH key
```bash
ssh-add ~/.ssh/id_rsa
sudo chmod 400 ~/.ssh/id_rsa
```
Clone source code
```
git clone git@github.com:hodacthuan/sexy-girls.git
cd sexy-girls
```
### Server Credentials
Add credential to file
```
nano devops/secrets.env

```
### Production - Start webserver

```
./deploy.sh build
./deploy.sh up prod
```

### Local - Start web server
```
./deploy.sh build
./deploy.sh up local
```

### Local - Scrape data
```
sudo apt install -y python3-pip
pip3 install -r ./server/requirements.txt

python3 server/manage.py scrape kissgoddess
python3 server/manage.py scrape hotgirlbiz

```
### Crontab Add and running
```
python3 server/manage.py crontab add
python3 server/manage.py crontab show
python3 server/manage.py crontab remove
```

## Roadmap
Pages can be scrape

| Website   |      View/Month               |     Notes    |
|---------- |---------------------------:   |:------       |
|https://kissgoddess.com/      |956k        | In progress
|https://hotgirl.biz/          |557k        | In progress
|https://www.xiurenji.com/     |100k
|https://www.v2ph.com/         |1200k
|https://www.nvshens.org/      |1000k
|https://www.hdleg.com/        |            |Buy images here
|https://xxxiao.com/           |477k        |Case study ramp up very fast since focus on 90% China
|https://www.24tupian.org/     |880k
|https://www.naixue.org/       |550k
|https://mrcong.com/           |381k
|http://www.wloob.com/         |85k
|https://www.youhuoxz.com/     |72k
|https://www.mn5.cc/           |190k
|https://www.kindgirls.com/    |5200k
|http://s3xies.com/
|http://loveygirl.cc           |160k
|https://www.xsnvshen.com/     |830k        |Error 1020 Access denied
|http://www.zjdtt.com/         |Not enough
|https://bestgirlsexy.com/     |Not enough
|https://www.depvailon.com/    |Not enough
|https://www.24cos.com/        |Not enough
|http://asianboobsdaily.com/   |Not enough

## Acknowledgements
- [Get Started With Django Part 1: Build a Portfolio App](https://realpython.com/get-started-with-django-1/)
- [Mongoengine Fields](https://docs.mongoengine.org/apireference.html#fields)
- [How To Scrape Web Pages with Beautiful Soup and Python 3](https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3)
- [Free Bootstrap Templates](https://startbootstrap.com/templates)
- [How to use Django with Apache and mod_wsgi](https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/modwsgi/)

Boto
- [Boto S3 Documents](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

- [List all S3 Object](https://alexwlchan.net/2017/07/listing-s3-keys/)