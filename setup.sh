pip install -r requirements.txt
su -c "psql -d postgres -c \"drop database if exists appdb\"" postgres
su -c "psql -d postgres -c \"create database appdb\"" postgres
su -c "psql -d postgres -c \"ALTER USER postgres WITH PASSWORD 'abc'\"" postgres