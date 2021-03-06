
#If you are putting this live, you definitely want to set DEBUG = False, or else hackers will steal your data! (protect your data)!
DEBUG = True



USE_RELOADER = False
# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example


# Set this to your database path
SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/prediction_game'


WTF_CSRF_ENABLED = True

# This might not be used anymore... I should really check into that. 
SECRET_KEY = 'PASSWORD FOR WTF FORMS'


DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2



# Enable protection agains *Cross-site Request Forgery (CSRF)*
# CSRF_ENABLED     = True

# # Use a secure, unique and absolutely secret key for
# # signing the data. 
# CSRF_SESSION_KEY = "secret"

# # Secret key for signing cookies
# SECRET_KEY = "secret"