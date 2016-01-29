# Guess the Karma server code

This very messy directory contains all the code to run your own version of www.guessthekarma.com (or hopefully it does). 

## Installation
I use conda as my package and environment manager. To create the environment and load all the python packages associated with this project, use this command: 

``` 
conda env create -f environment.yml
```

The next thing you need to do is create a file called config.py. This repo comes with a sample, so just do:
```
cp config_sample.py config.py
```

Once you are in there, the only thing you need to do is to change this line:
```
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/prediction_game'
```
Point that to wherever your database lives. I think it is necessary to run a postgres database but if it works with any other database (sqlite would be the simplest to work with), let me know. 
