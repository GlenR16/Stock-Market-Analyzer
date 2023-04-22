set +x


# Store the current working directory
echo -e "\e[32mGetting current location...\e[0m"
root=$(pwd)

# Create python virtual environment if it doesn't exist
if [ ! -d "$root/venv" ]; then
    echo -e "\e[32mCreating virtual environment...\e[0m"
    python3 -m venv $root/venv
fi

# Activate virtual environment
echo -e "\e[32mActivating virtual environment...\e[0m"
source $root/venv/bin/activate

# Install python dependencies
echo -e "\e[32mInstalling python dependencies...\e[0m"
pip install -r $root/requirements.txt

# Setup directory structure for docker compose
echo -e "\e[32mSetting up directory structure for docker compose...\e[0m"

mkdir -p $root/docker
mkdir -p $root/docker/postgres
mkdir -p $root/docker/postgres/logs
mkdir -p $root/docker/postgres/data

# Start docker containers
echo -e "\e[32mStarting docker containers...\e[0m"

set -x
sudo docker compose --env-file .production.env up 