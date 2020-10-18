# toloker
The command line interface for Yandex Toloka.

## Install
    git clone git@github.com:cad0gan/toloker.git
    cd toloker
    git submodule update --init
    pip install -r pytoloka/requirements.txt
    pip install -r requirements.txt
    mkdir -p ~/.config/toloker/
    cp config_sample.yml ~/.config/toloker/config.yml
    
If you are using macOS and you want to get notifications, install **terminal-notifier**.
https://github.com/julienXX/terminal-notifier 

## Usage
    ./toloker -h
### Assigner
Automatic assign your favorite tasks:
    
    ./toloker assigner
**Hotkeys**:
* **q**: quit
* **s**: stop/start
### Other
Show all tasks:

    ./toloker tasks -l
    
-------------------------------------

Show worker information:

    ./toloker worker

Show your skills:

    ./toloker skills -l

Show first 3 skills

    ./toloker skills -l -n 3
    
Show your transactions:

    ./toloker transactions -l

Show last 5 transactions:

    ./toloker transactions -l -n 5

Show analytics:

    ./toloker history -a
