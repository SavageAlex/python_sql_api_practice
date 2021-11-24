#!/bin/bash

if [ ! -e "credentials.conf" ]; then
    echo -n "please enter credentials file password: "
    read password
    echo "extracting credentials..."
    unzip -qq -P "$password" .util/credentials.zip -d . && \
        echo " - [OK] credentials extracted" || \
        {
            echo " - [ERROR] invalid password!"
            exit 2
        }
fi

if [ ! -e "database.sqlite" ]; then
    echo "seeding database..."
    python3 .util/seed.py && \
        echo " - [OK] database.sqlite created" || \
        {
            echo " - [ERROR] failed to create database"
            exit 4
        }
fi
