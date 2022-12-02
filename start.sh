if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/Azanpopz/kindi.git /kindi
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /kindi
fi
cd /kindi
pip3 install -U -r requirements.txt
echo "Starting kindi...."
python3 bot.py
