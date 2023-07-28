from ..utils import db

class UserModel(db.Model):
    __tablename__ = 'user_table'
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(8), unique=True, nullable=False)
    
    def __repr__(self):
        print(self.name)
        
    def save(self):
        db.session.add(self)
        db.session.commit()