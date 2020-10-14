# toloker
Command line interface for Yandex Toloka.

## Install
    git clone git@github.com:cad0gan/toloker.git
    cd toloker
    git submodule update --init
    mkdir -p ~/.config/toloker/
    cp config_sample.yml ~/.config/toloker/config.yml

## Usage
    ./toloker -h
### Examples
Automatic assign your favorite tasks:
    
    ./toloker assigner
Show all tasks:

    ./toloker tasks -l
Show your skills:

    ./toloker skills -l
    
Show your transactions:

    ./toloker transactions -l
