## Installation

### Install tools needed
```
git clone https://github.com/hodacthuan/linux-tools.git
linux-tools/docker/index.sh
```
### Up database MongoDB

```
git clone https://github.com/hodacthuan/devops-infrastructure.git
cd devops-infrastructure/mongodb
nano sexy-girls.env
./up.sh sexy-girls
```

### Up to production

### Local - Scrape data
```
sudo apt install -y python3-pip
pip3 install -r ./server/requirements.txt
python3 server/manage.py scrape
```
### Local - Start web server
```
./deploy.sh up local
```
### Crontab Add and running
```
python3 server/manage.py crontab add
python3 server/manage.py crontab show
python3 server/manage.py crontab remove
```

## Roadmap
Pages can be scrape

| Website   |      View/Month      |  Notes |
|---------- |-------------: |:------|
|https://kissgoddess.com/     |  956k       | In progress
|https://www.xiurenji.com/     |100k
|https://hotgirl.biz/          |557k
|https://www.v2ph.com/         |1200k
|https://www.nvshens.org/      |1000k
|https://www.hdleg.com/        |            |Buy images here
|https://www.24tupian.org/     |880k
|https://www.naixue.org/       |550k
|https://mrcong.com/           |381k
|https://bestgirlsexy.com/     |Not enough
|https://www.depvailon.com/    |Not enough
|http://www.wloob.com/         |85k
|https://www.24cos.com/        |Not enough
|http://asianboobsdaily.com/   |NOt enough
|https://www.youhuoxz.com/     |72k
|https://www.mn5.cc/           |190k
|https://www.kindgirls.com/    |5200k
|http://s3xies.com/
|http://loveygirl.cc           |160k
|https://www.xsnvshen.com/     |830k        |Error 1020 Access denied
|http://www.zjdtt.com/         |Not enough

## Acknowledgements
- [Get Started With Django Part 1: Build a Portfolio App](https://realpython.com/get-started-with-django-1/)
- [Mongoengine Fields](https://docs.mongoengine.org/apireference.html#fields)
- [How To Scrape Web Pages with Beautiful Soup and Python 3](https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3)