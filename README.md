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
- https://kissgoddess.com/      :956k
- https://www.xiurenji.com/     :100k
- https://hotgirl.biz/          :557k
- https://www.v2ph.com/         :1200k
- https://www.nvshens.org/      :1000k
- https://www.hdleg.com/        :Buy images here
- https://www.24tupian.org/     :880k
- https://www.naixue.org/       :550k
- https://mrcong.com/           :381k
- https://bestgirlsexy.com/     :Not enough
- https://www.depvailon.com/    :Not enough
- http://www.wloob.com/         :85k
- https://www.24cos.com/        :Not enough
- http://asianboobsdaily.com/   :NOt enough
- https://www.youhuoxz.com/     :72k
- https://www.mn5.cc/           :190k

Pages for references
- https://www.kindgirls.com/
- https://www.instagram.com/s3xybabies/
- http://s3xies.com/
- loveygirl.cc                  :160k
- https://www.xsnvshen.com/     :830k
- http://www.zjdtt.com/         :Not enough

## Acknowledgements
- https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3