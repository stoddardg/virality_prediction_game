# Guess the Karma 

This very messy directory contains all the code to run your own version of www.guessthekarma.com (or hopefully it does). 

## Installation

First, grab this repo with 
```
git clone https://github.com/stoddardg/virality_prediction_game.git
```

Now you should have the code, so time to actually install things. 

First step is to create a virtual environment and install all the necessary packages. I use conda as my package and environment manager. To create the environment and load all the python packages associated with this project, use this command: 

``` 
conda env create -f environment.yml
```
Hopefully that works. Then do
```
source activate guess_the_karma_env
``` 
to activate the environment. 


The next thing you need to do is create a file called config.py. This repo comes with a sample, so just do:
```
cp config_sample.py config.py
```

Once you are in there, the only thing you need to do is to change this line:
```
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/prediction_game'
```
Point that to wherever your database lives. I think it is necessary to run a postgres database but if it works with any other database (sqlite would be the simplest to work with), let me know. 

The next step is to populate the database with some data. To do this 
```
python populate_db.py
```

If that works, you can now run the server with 
```
python run.py
```
After running that, you should see a bunch of lines, and one of them should look like this: 
```
* Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

Just point your browser to that url and you should be good to go!




If things don't work, there are two immediate things to make sure. First, make sure your the virtual environment is activated. Second, make sure that your instance of postgres is running. If both of those things are working and its still not going, then ¯\_(ツ)_/¯
