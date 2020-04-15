# PeepoBot
A fork of GTXBot, our old bot developed by me and Codian, modified for different use

## Self-Hosting
##### Install Dependencies
###### Packages
+ Python 3.6+
###### Libraries
+ ``discord.py``
+ ``aiosqlite``
+ ``youtube-dl``

1. Install ``python`` package different for each distro)

    Arch/Manjaro
    ```
    # pacman -S python3
    ```
    Ubuntu/Debian/Mint
    ```
    # apt install python3
    ```
    RHEL/Centos/Fedora
    ```
    # yum install python3
    ```

2. Install dependencies with ``pip``
    
    If you do not have ``pip`` installed, install it:
    
    ```
    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
    $ python3 get-pip.py
    ```
    
    If you have ``pip`` or have just installed it:
    
    ```
    # python3 -m pip install -r requirements.txt
    ```
---

 ##### Running PeepoBot
 
Simply run the ``bot.py`` file with ``python3`` to begin the startup process.
```
$ python3 bot.py
```
The bot will not start the first time, but it will generate some important files and dirs:
1. ``config.json`` - This file is the *bot config* which tells the bot important startup information such as the bot token and logging info.

2. ``common.db`` - This is the bot's sqlite3 database file where user and guild data is stored.

3. ``logs/`` - This folder will store logfiles. You can configure how logging behaves in the ``config.json`` file. 

After you're done configuring the bot, start it like before, and if you did everything correctly, it should start up!
```
$ python3 bot.py
```
---
##### License Information
```
MIT License

Copyright (c) 2019 Martin Velikov & Patrick Thompson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
