# Zylo

Zylo is a lightweight web framework made with love.

## Features

- Simple and intuitive routing
- Template rendering using Jinja2
- Session management with the sessions library
- Static file serving

## Installation

You can install Zylo using pip:


```bash
pip install zylo

```

## Usage

```python

# app.py

from zylo.core.branch import Zylo

app = Zylo()

@app.route('/')
def home(request):
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
 
```

## changelogs

- Beta version 2.0.8
- Latest update of beta
- Bug fixes with update --> 2.0.8
- Zylo Mailer got new features with update of 2.0.8
- Zylo JwT Now support HS256 HS384 HS512 & RS256 RS384 RS512
- Zylo Chiper introducing chip keys @latest 2.0.8
- Zylo Introduce CORS For web security
- Zylo Introduce Secure cookie builder @zinc cookies 
- Zylo BaseModal Added new features for a vast support.
- Zylo Instance now introducing @secure on Zylo web for more details check out the ## Zylo Instance.
- Zylo Introduce ZyloRestful For API building easily.
- changelogs 2.0.8 @latest
- Running on beta current version @2.0.8
- Relese date 21-8-2023 ( 23 Aug 2023 1:45:13:00:16 PM ( IST +5:30 ) )
- Push the errors and bugs to @zylo github 

## Usage Guide

Our team working hard and the usage guide will be avilable within 24hrs on http://zylo.vvfin.in or https://github.com/E491K8/ZyloProject/

## Batteries Support 

Installation of ZyloAdmin v1

```bash
pip install zyloadmin

```

## Create zylo project

```bash
zyloadmin startproject -i {projectName}
```

## Zylo Instance @secure

```python
# app.py

from zylo.core.branch import Zylo, Response

app = Zylo(__name__)

@app.route('/', methods=['GET', 'POST'], secure=True, pin="your_secret_pin")
def secureRoute(request):
    return Response("You have accessed the secure route! ")

### In this code we defined app as Zylo(__name__) instance then pass the secure = True and set the pin, by passing these deatils the Zylo will locked that particular route which you secure, if someone try to access the route the Zylo ask for a pin before accessing that route if pin is matched with your passed pin in that route the user will allow to get access of that route else it through a incorrect pin error until user pass the correct pin.

```
## Zylo Instance @BaseFeatures

```python
# app.py

from zylo.core.branch import Zylo, Response

app = Zylo(__name__)

@app.route('/', methods=['GET', 'POST'],  max_url_length=None, default=None, host=None, strict_slashes=None)
def base(request):
    return Response("Welcome")

```

## Mailer 2.0.8

```python 
# mailer.py

## Now you can setup the mailer through the Zylo-Admin batteries ($project) > settings.py file

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

## With using Mailer 2.0.8 you can now, use Bluk email sending and Send email Template with a timelimit and send a email with a paticular template.

```

## Documantaion v2.0.8

- Visit http://zylo.vvfin.in/docs/v2/
- For futher assistance get in touch with us support@vvfin.in
