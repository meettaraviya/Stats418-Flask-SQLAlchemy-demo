#!/bin/bash


#########################################################################################
#                                                                                       #
#   run.sh starts our flask server                                                      #
#                                                                                       #
#       run.sh --public  # Run on public IP (can be accessed by anyone with your IP)    #
#       run.sh           # Run on private IP (can only be accessed by your computer)    #
#                                                                                       #
#########################################################################################


# Define flask configuration using Shell environment
export FLASK_APP=crashinfo
export FLASK_ENV=development
export FLASK_SERVER_NAME=0.0.0.0
export FLASK_RUN_PORT=$(($UID + 50000))  # Set port based on UID so no conflicts

if [[ $1 == "--public" ]] ; then
    HOST=--host=0.0.0.0
fi

# Run flask app
python3 -m flask run $HOST
