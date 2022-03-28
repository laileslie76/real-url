# docker build -t mytv:v1 .
# docker run --name tv -v /mnt/mmcblk2p4/real-url:/tv  --restart=always  --net=host -d  mytv:v1
FROM python:3.9.5
RUN pip install flask BeautifulSoup4 PyExecJS expiringdict requests && apt update && apt-get install -y nodejs
CMD ["python","/tv/server-flask.py"]
