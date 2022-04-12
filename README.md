# F1 Project Databases

Should be easy to run, nothing too crazy. The lower command also gives live reload

## Installation

`pip install flask` `pip install sqlalchemy`

## Run
`FLASK_APP=server.py FLASK_ENV=development flask run`


Also run an `export USER={Pranav's UNI}`  and `export PASSWORD={DB Password}`


## TODO
    - Sanatize inputs
    - Sanatize the signup process
    - Registering a credit card
    - Registering new bids
    - Race information

## Directory
`
├── README.md
├── SPEC.md
├── __pycache__
│   └── server.cpython-38.pyc
├── auth
│   ├── __pycache__
│   │   └── login.cpython-38.pyc
│   ├── login.py
│   └── payment.py
├── bets
│   ├── __pycache__
│   │   └── bets.cpython-38.pyc
│   └── bets.py
├── leaderboard
│   ├── __pycache__
│   │   └── leaderboard.cpython-38.pyc
│   └── leaderboard.py
├── server.py
├── templates
│   ├── anotherfile.html
│   ├── auth
│   │   ├── login.html
│   │   └── signup.html
│   ├── bets
│   │   ├── bets.html
│   │   └── placebet.html
│   ├── index.html
│   └── leaderboard
│       └── leaderboard.html
└── test.ipynb
`

11 directories, 19 files
