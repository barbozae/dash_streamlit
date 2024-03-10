import pickle
from pathlib import Path
import streamlit_authenticator as stauth


names = ['Edson Barboza', 'Matheus Barboza', 'Daniela Bonopera']
usernames = ['barbozae', 'barbozam', 'bonoperad']
passwords = ['XXX', 'XXX', 'XXX']

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('wb') as file:
    pickle.dump(hashed_passwords, file)