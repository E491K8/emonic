# Emonic

Emonic is a lightweight web framework made with love.

[![Emonic.jpg](https://i.postimg.cc/xCmNTN4y/Emonic.jpg)](https://postimg.cc/TLR3t1Gp)

## Features

- Simple and intuitive routing
- Template rendering using Jinja2
- Session management with the sessions library
- Static file serving

## Installation

You can install Emonic using pip:


```bash
pip install emonic

```

## Usage

```python

# app.py

from emonic.core.branch import Emonic

app = Emonic()

@app.route('/')
def home(request):
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
 
```

## changelogs

- Latest version 1.0.0
- Emonic Mailer of 1.0.0
- Emonic JwT support HS256 HS384 HS512 & RS256 RS384 RS512
- Emonic Chiper introducing chip keys @latest 1.0.0
- Emonic CORS For web security
- Emonic Secure cookie builder @zinc cookies 
- Emonic BaseModal features for a vast support.
- Emonic Instance support @secure on Emonic web for more details check out the ## Emonic Instance.
- Emonic Introduce EmonicRestful For API building easily.
- changelogs 1.0.0 @latest
- Relese date 22-8-2023 ( 22 Aug 2023 1:45:13:00:16 PM ( IST +5:30 ) )
- Push the errors and bugs to @emonic github 

## Usage Guide

Our team working hard and the usage guide will be avilable within 24hrs on http://emonic.vvfin.in or https://github.com/embrake/emonic/

## Batteries Support 

Installation of EmonicAdmin v1

```bash
pip install emonic-admin

```

## Create emonic project

```bash
emonic-admin startproject -i {projectName}
```

## Emonic Instance @secure

```python
# app.py

from emonic.core.branch import Emonic

app = Emonic(__name__)

@app.route('/', methods=['GET', 'POST'], secure=True, pin="your_secret_pin")
def secureRoute(request):
    return "You have accessed the secure route! "

### In this code we defined app as Emonic(__name__) instance then pass the secure = True and set the pin, by passing these deatils the Emonic will locked that particular route which you secure, if someone try to access the route the Emonic ask for a pin before accessing that route if pin is matched with your passed pin in that route the user will allow to get access of that route else it through a incorrect pin error until user pass the correct pin.

```
## Emonic Instance @BaseFeatures

```python
# app.py

from emonic.core.branch import Emonic

app = Emonic(__name__)

@app.route('/', methods=['GET', 'POST'],  max_url_length=None, default=None, host=None, strict_slashes=None)
def base(request):
    return "Welcome"

```

## Mailer 1.0.0

```python 
# mailer.py

## Now you can setup the mailer through the Emonic-Admin batteries ($project) > settings.py file

MAILER = [
    {
        "SMTP": "", ## SMTP for e.g, smtp.gmail.com
        "PORT": , ## PORT SSL 447 TLS 587
        "USERNAME": "", # Your Account Username or email
        "PASSWORD": "", # Your Account Password
        "SSL": , # Choose the SSL Security either True or False
        "DEFAULT_SENDER": "" # Default send Account or email
    }
]

## With using Mailer 1.0.0 you can now, use Bluk email sending and Send email Template with a timelimit and send a email with a paticular template.

```

## Documantaion v2.0.8

- Visit http://emonic.vvfin.in/docs/v1/
- For futher assistance get in touch with us support@vvfin.in
