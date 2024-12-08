
### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```
2. Create a secrets.toml file in the root directory and store your Open AI and Serper Keys

   ```
   $ mkdir -p .streamlit
   $ touch .streamlit/secrets.toml
   $ with open('.streamlit/secrets.toml', 'w') as f:
        f.write('my_openaikey = "xxxxx"\n')
        f.write('my_serperkey = "xxxxx"\n')
   ```
   
3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
