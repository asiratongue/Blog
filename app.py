
import json, os, copy, shutil
from flask import Flask, request, Response, render_template, jsonify, url_for, redirect

article_dir = os.path.join(os.getcwd(), 'articles')
if not os.path.exists(article_dir):
   os.makedirs(article_dir)

article_title_list = []
article_nested_dict = {}
USERNAME = 'admin'
PASSWORD = 'password'
filepath_list = []

app = Flask(__name__)

def ArticleUpdate():
   global article_nested_dict 
   global article_title_list
   article_title_list = []
   filepath_list.clear()
   x = 0

   for folder, subfolders, files in os.walk(article_dir):
       if files != []:
           filepath = os.path.join(folder, files[0])
           x += 1
           filepath_list.append(filepath)

           with open(filepath, 'r') as jsonfile:
               article_json = json.load(jsonfile)
               article_nested_dict[x] = article_json
               article_title_list.append(article_json['title'])

ArticleUpdate()

def check_auth(username, password):
   return username == USERNAME and password == PASSWORD

def authenticate():
   return Response('Could not verify! Please provide valid credentials.',401, {'WWW-Authenticate' : 'Basic realm = "Login Required"'})

@app.route('/article/<int:id>', methods = ['GET', 'POST'])
def article_page(id):
   return render_template('article.html', article_nested_dict = article_nested_dict, id = id)

@app.route('/', methods=['GET', 'POST'])
def home():
   if request.method == 'GET':
       ArticleUpdate()
   return render_template('home.html', article_nested_dict=article_nested_dict, article_title_list=article_title_list)

@app.route('/dashboard')
def dashboard():
   auth = request.authorization
   if not auth or not check_auth(auth.username, auth.password):
       return authenticate()
   if request.method == 'GET':
       ArticleUpdate()
   return render_template('dashboard.html', article_nested_dict = article_nested_dict, article_title_list = article_title_list)

@app.route('/delete/<int:id>', methods = ['GET','POST'])
def delete_page(id):
   with open(filepath_list[id - 1], 'r') as jsonread:
       article_json = json.load(jsonread)

   if request.method == 'POST':
       ArticleDelPath = '/Article' + ' ' + str(id)
       shutil.rmtree(article_dir + ArticleDelPath)
       return redirect(url_for('dashboard'))

   return render_template('delete.html', article_nested_dict=article_nested_dict, article_json=article_json, id=id)

@app.route('/add', methods = ['POST', 'GET'])
def add_page():
   new_article = {}

   if request.method == 'POST':
       TitleEdit = request.form.get('Article_Title')
       PublishingDateEdit = request.form.get('Publishing_Date')
       ContentEdit = request.form.get('Content')

       new_article['title'] = TitleEdit
       new_article['Date'] = PublishingDateEdit
       new_article['Content'] = ContentEdit
       new_article['id'] = len(article_nested_dict) + 1
       jsonConv = json.dumps(new_article) 
       NewArticleName = '/article' + str(len(article_nested_dict)+1) + '.json'
       new_article_folder = '/Article' + ' ' + str(len(article_nested_dict)+1)
       new_directory = article_dir + new_article_folder

       os.makedirs(new_directory, exist_ok=True)
       with open(new_directory + NewArticleName, 'w') as file:
           file.write(jsonConv)
       return redirect(url_for('dashboard'))
   
   return render_template('add.html')

@app.route('/edit_page/<int:id>', methods = ['POST', 'GET'])
def edit_page(id):
   with open (filepath_list[id - 1], 'r') as jsonread:
       article_json = json.load(jsonread)

   if request.method == 'POST':
       TitleEdit = request.form.get('Article_Title')
       PublishingDateEdit = request.form.get('Publishing_Date')
       ContentEdit = request.form.get('Content')

       UpdatedArticle = copy.deepcopy(article_nested_dict[id])  
       UpdatedArticle['title'] = TitleEdit
       UpdatedArticle['Date'] = PublishingDateEdit
       UpdatedArticle['Content'] = ContentEdit

       ArticleStr = 'article' + str(UpdatedArticle['id'])+ '.json'

       jsonConv = json.dumps(UpdatedArticle)

       for folder, subfolders, files in os.walk(article_dir):
           if files != []:
               if files[0] == ArticleStr:
                   filepath = os.path.join(folder, ArticleStr)
                   with open (filepath, 'w') as jsonfile:
                       jsonfile.write(jsonConv)

       article_json = UpdatedArticle
       return redirect(url_for('dashboard'))

   return render_template('edit.html', article_json = article_json, article_nested_dict = article_nested_dict, id = id)

@app.route('/load-more')
def load_more():
   page = int(request.args.get('page', 1))
   start_idx = (page - 1) * 10
   end_idx = start_idx + 10
   articles = list(article_nested_dict.values())[start_idx:end_idx]
   return jsonify({'articles': articles})

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
