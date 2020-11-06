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
- https://kissgoddess.com/
- https://hotgirl.biz/
- https://www.nvshens.org/
- https://www.depvailon.com/
- http://www.wloob.com/

Pages for references
- https://www.kindgirls.com/
- https://www.instagram.com/s3xybabies/
- http://s3xies.com/
- loveygirl.cc
- https://www.xsnvshen.com/
- http://www.zjdtt.com/

## Acknowledgements
- https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3