# RealWin API

### Local Setup:

```
python3 -m venv venv
source venv/bin/activate
poetry install

```

### Install New Package:

```
 poetry add package_name

```

### Delete Package:

```
 poetry remove package_name

```

### Run:

```
   uvicorn source.main:app --host 0.0.0.0 --reload

```

### Migration:

```
  alembic revision --autogenerate -m "description"
  alembic upgrade head

```

### Docs:

```
  OpenAPI: http://localhost:8000/docs

```


### App Architecture:

#### Main

```
  source > main.py => main file of the app which bootstraps all the services

```

#### Core

```
  source > core   > settings.py    ==> handles application settings across the app
  source > core   > routers.py     ==> handles all the routes in application
  source > core   > models.py      ==> handles base database model for database
  source > core   > schemas.py     ==> handles default schemas to be used for the application
  source > core   > exceptions.py  ==> handles application execptions across the app

```

#### App

This folder will be used for new module creation existing modules will be users and auth

below will be the required file structure of the each module

```
  source > app   > views.py     ==> will handle the module routing
  source > app   > models.py    ==> will be used to define the database structure like columns and types
  source > app   > schemas.py   ==> will be used to define schemas to be used for the module
  source > app   > services.py  ==> service layer of the module and will be used to handle database operations and logic

  other files can be added as need with in the module like helpers / utils

```
