# Prompt Evaluator

Automate the process of generating responses to prompts and log into a postgres database.  

- 👉 Enter one or more questions.  Each subsequent question leverages the conversation history so you can chain questions together.
- 👉 Select one or more models to run the questions through
- 👉 Specify a base_url to retrieve list of models (configured to use litellm and ollama as a openai proxy server and inference engine)
- 👉 Log results to an external postgres db 

<br />

## Features: 

- ✅ `Up-to-date Dependencies`
- ✅ Modern UI 
- ✅ 

<br />

## Start with `Docker`

> In case the starter was built with Docker support, here is the start up CMD:

```bash
$ docker-compose up --build
```

Once the above command is finished, the new app is started on `http://localhost:5085`

<br />

## Manual Build 

> Download/Clone the sources  

```bash
$ git clone https://github.com/<THIS_REPO>.git
$ cd <LOCAL_Directory>
```

<br />

> Install modules via `VENV`  

```bash
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

<br />

> `Set Up Database`

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

<br />

> `Generate your API` (optional) 

```bash
$ python manage.py generate-api -f
```

<br />

> `Start the App`

```bash
$ python manage.py runserver
```

At this point, the app runs at `http://127.0.0.1:8000/`. 

<br />

---
Starter built with [Django App Generator](https://app-generator.dev/django/), a free service provided by AppSeed.
