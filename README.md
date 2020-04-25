# PeepoBot
A fork of GTXBot, our old Discord Bot aiming to bring the bot to a more general-use state.

Authors:
* oree (xxori)
* Codian (xxcodianxx)

## Self-Hosting
##### Install Dependencies
###### Packages
+ Python 3.6+
###### Libraries
+ ``discord.py``
+ ``aiosqlite``
+ ``youtube-dl``

1. Install ``python3`` package (different for each distro)

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
    
    *Run the following command to install the required dependencies.*
    ```
    # python3 -m pip install -r requirements.txt
    ```
    
    **If you do not have ``pip`` installed, get it like so:**
    
    ```
    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
    $ python3 get-pip.py
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

##### Configuration Guide
When configuring the bot, the most important file you want to look at is `config.json` as it contains the bot configuration.
By default, it will look like this:

```json
{
    "token": "create an application at https://discordapp.com/developers/",
    "logfiles": {
        "enabled": true,
        "overwrite": false
    },
    "authorized_dev_ids": [
        308034225137778698,
        304219290649886720
    ],
    "main_guild": -1,
    "show_splash_screen": true
}
```

**Configuration Fields**

*It is essential that you do not add or remove any curly brackets (`{` `}`) as that may corrupt the strucutre of the*
*JSON file. Below are some of the important fields you might wanna touch.*


* `token` - The bot token. Required for the bot to start up. Put the token in between the quotes: `"token"`
If you do not have one yet, create an application from [here](https://discordapp.com/developers/applications).

* `logfiles` - Logging configuration
    * `enabled` - Log information to files? Change to either `true` or `false` (lowercase)
    
    * `overwrite` - Instead of making a new log file for every run, just keep writing into the same one? 
    Use this if you want to avoid spam in the `logs` folder. Change to either `true` or `false`. 

* `authorized_dev_ids` - Self explanatory. Put the User ID's of anyone you want to be able to execute developer
commands here, separated by commas. Eg. `[1234, 3214]`

* `main_guild` - ID of the main guild the bot operates in. Set to `-1` to ignore.

* `show_splash_screen` - Should the splash screen be shown when starting the bot? Change to either `true` or `false`.

---
##### License Information
```
MIT License

Copyright (c) 2020 Martin Velikov & Patrick Thompson

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

### Happy Hosting! :)
