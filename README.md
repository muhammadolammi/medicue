# medicue
Medical symtoms checker


# Usage 
cd $WORKSPACE // go to your workspace directory 
git clone https://github.com/muhammadolammi/medicue  //clone the repo
cd medicue // go to the app directory
pip install -r requirements.txt //install dependency , run this and continue with the step while its working.
code .env // if you are using vscode this create a .env file(create .env file if you arent of vscode)
// add this record to the file
```
# the database url format . make sure to crreate database named medicue_db on mysql. the command "CREATE DATABASE medicue_db;"
DB_URL='mysql+pymysql://username:password@localhost/medicue_db'
# you can generate one with open ssl command "openssl rand -hex 32"
JWT_SECRET_KEY="your jwt signer" 
# get one or copy from https://aistudio.google.com/app/api-keys
GEMINI_API_KEY="your gemini api key"
```
python main.py // this should start your backend app , copy the url the second url usually starting with 193.168... and use in android app
