sudo apt update
sudo apt install redis -y
pip3 install -r requirements.txt
sudo systemctl enable redis​
sudo service redis start
redis-server &
redis-cli ping
python3 setup.py install
