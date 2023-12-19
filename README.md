# Authenticator
The goal of this application is to authenticate users and manage their sessions.

## Application structure
```scss
not_bad_test/
├── app/
│   ├── main.py
│   ├── routers/
│   │   ├── sessions.py
│   │   └── users.py
│   ├── kernels/
│   │   ├── jwt_exceptions.py
│   │   └── sessions.py
│   └── database/
│       ├── crud.py
│       ├── database.py
│       ├── models.py
│       └── schemas.py
├── tests/
│   └── test_main.py
├── authenticator_db.sqlite
├── requirements.txt
├── Dockerfile.authenticator
└── README.md
```


## Technical specification

Créer une application d'authentification en utilisant le framework python FastAPI.
L'application doit exposer un REST API endpoint /sessions qui accepte des appels HTTP POST.
L'objet reçu dans le body de l'appel doit avoir cette forme: 
````json
{
    "user": {
        "email": "joe@foo.com"
    },
    "device": {
        "vendor_uuid": "un uuid lié au device obligatoire si le type est 'mobi'",
        "type" : "'mobi' ou 'othr'"
    }
}
````

Toute combinaison incorrecte ou vide pour le paramètre device, ou toute combinaison vide pour le paramètre user devra retourner une réponse HTTP 400.
De plus l'API endpoint /sessions doit accepter un paramètre nommé mode, passé en query param qui n'aura qu'une seule valeur possible : une adresse email, toute autre valeur, ou une absence de valeur devra retourner une réponse HTTP 400.

Après avoir correctement authentifié un utilisateur suite à l'appel HTTP POST reçu sur l'endpoint /sessions, un réponse HTTP qui doit avoir cette forme doit être retournée: 
````json
{
    "uuid" : "un unique identifier de session.py, qui devra être préfixé par les lettres 'ses-'",
    "created_at" : "date de création de la session.py",
    "token" : "un token de session.py",
    "is_new_user" : "un boolean indiquant si l'utilisateur est nouveau",
    "is_new_device" : "un boolean indiquant si le device est nouveau. La notion de 'nouveau' est définie si dessous)",
    "user": {
        "uuid" : "uuid du user, qui devra être préfixé par les lettres 'usr-'",
        "email": "l'email de l'utilisateur"
    },
    "device": {
        "uuid" : "uuid device, qui devra être préfixé par les lettres dev-",
        "type" : "mobi ou othr",
        "vendor_uuid" : "un uuid lié au device obligatoire si le type est 'mobi'"
    },
    "status": "pending"
}
````

Pour terminer l'authentification de l'utilisateur, l'application doit générer un code à 6 chiffres qu'elle sauvegardera dans une table, ce code devra être envoyé par e-mail à l'utilisateur, l'utilisateur aura 5 minutes au maximum pour rentrer ce code dans l'interface d'authentification.
Lorsque l'utilisateur cliquera sur le bouton valider, un appel HTTP PATCH sera fait sur l'api endpoint /sessions avec le body suivant : 
````json
{
    "otp_code":  "le code reçu"
}
````

Dans les headers de l'appel on doit trouver le token qui a été envoyé dans la réponse du premier appel HTTP POST sur l'API endpoint session, ce token permet de faire le lien entre le code otp_code et l'utilisateur qu'on authentifie.
La réponse à l'appel HTTP PATH reçu sur l'api endpoint /sessions sera de cette forme: 
````json
{
    "uuid" : "un unique identifier de session.py, qui devra être préfixé par les lettres 'ses-'",
    "created_at" : "date de création de la session.py",
    "token" : "un token de session.py",
    "is_new_user" : "un boolean indiquant si l'utilisateur est nouveau",
    "is_new_device" : "un boolean indiquant si le device est nouveau. La notion de 'nouveau' est définie si dessous)",
    "user": {
        "uuid" : "uuid du user, qui devra être préfixé par les lettres 'usr-'",
        "email": "l'email de l'utilisateur"
    },
    "device": {
        "uuid" : "uuid device, qui devra être préfixé par les lettres dev-",
        "type" : "mobi ou othr",
        "vendor_uuid" : "un uuid lié au device obligatoire si le type est 'mobi'"
    },
    "status" : "confirmed"
}
````
La réponse à l'appel HTTP PATCH ressemble à la réponse à l'appel HTTP POST, la différence est le paramètre status qui passe de pending à confirmed.

Si l'appel HTTP PATCH sur l'api endpoint /sessions est reçu après 5 minutes, une réponse HTTP 400 sera envoyé pour dire que l'authentification a échoué et qu'il faut recommencer.

Pour pouvoir gérer les appareils depuis lesquelles un utilisateurs se connecte nous utilisons le paramètre device.
Pour chaque demande d'authentification, si le type de device est 'mobi', le token aura une durée de vie infinie et la même session sera toujours renvoyée pour le même couple user/device.
Le code retourné dans la réponse HTTP sera 201 à la première demande de session puis 200 les futures demandes d'authentification.
Si le type de device est 'othr', le token aura une durée de vie de 2 heures. La même session sera renvoyée si une requête avec 'othr' a lieu dans la durée de vie.
Passé ce délai une nouvelle session est créée et celle d'avant doit passer à expired.

Le type de token qu'on utilisera sera JWT. 
Les tables de base de données qui vont contenir les informations de sessions doivent permettent de faire des statistiques sur les sessions.

## OpenAPI documentation (SWAGGER)
http://localhost:8000/docs


### Logs
Logs are available in the folder `not_bad_test/logs`  
If something doesn't work as expected you can consult the logs
