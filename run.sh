# Define flask configuration using Shell environment
export FLASK_APP=crashinfo
export FLASK_ENV=development
export FLASK_SERVER_NAME=0.0.0.0
export FLASK_RUN_PORT=$(($UID + 50000))  # Set port based on UID so no conflicts

# Run flask app
python3 -m flask run
