from flask import Flask, request,redirect,render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random,string

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///urls.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
shorts=[]

data={}

@app.before_first_request
def create_tables():
    db.create_all()

class Url(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    web = db.Column(db.String(200),nullable=False)
    short = db.Column(db.String(16),nullable=False)
    date_created  = db.Column(db.DateTime,default=datetime.utcnow)

    def __init__(self,web,short):
        self.web =web
        self.short = short
    
    def __repr__(self)->str:
        return f"{self.sno} - {self.title}"

@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        web=request.form["web"]
        url = Url.query.filter_by(web=web).first()
        if url:
            return redirect(url_for("redirect_new_url",url=url.short))
        else:
            while(True):
               short = ''.join(random.choices(string.ascii_uppercase+string.ascii_lowercase+string.digits,k=16))
               if short not in shorts:
                    break
            shorts.append(short)
            obj = Url(web=web,short=short)
            db.session.add(obj)
            db.session.commit()
            data[short]=web
            allurl = Url.query.all()
            return redirect(url_for('redirect_new_url',url=short))
    
    return render_template("index.html")

@app.route('/history')
def history():
    return render_template("history.html",allurl=Url.query.all())

@app.route('/<short>')
def search(short):
    url=Url.query.filter_by(short=short).first()
    if url:
        return redirect(url.web)
    else:
        f'<h1>Url does not exist</h1>'


@app.route('/display/<url>')
def redirect_new_url(url):
    return render_template('shorten.html',short_url=url)

@app.route('/delete/<int:sno>')
def delete(sno):
    url = Url.query.filter_by(sno=sno).first()
    db.session.delete(url)
    db.session.commit()
    return redirect("/history")

if __name__ == '__main__':
    app.run(debug=True)