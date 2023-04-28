import datetime
import sqlalchemy
import sqlalchemy.orm as orm 
import passlib.hash as hash
import database as db



class UserModel(db.Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,index=True)
    email = sqlalchemy.Column(sqlalchemy.String,unique=True,index=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    lastname = sqlalchemy.Column(sqlalchemy.String)
    phone = sqlalchemy.Column(sqlalchemy.String)
    password_hash = sqlalchemy.Column(sqlalchemy.String)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default = datetime.datetime.utcnow())
    posts = orm.relationship("PostModel",back_populates="user")
    
    
    def password_verification(self, password:str):
        return hash.bcrypt.verify(password,self.password_hash)
    
    
    
class PostModel(db.Base):
    __tablename__ = 'posts'
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True,index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("users.id"))
    post_title = sqlalchemy.Column(sqlalchemy.String,index=True)
    post_description = sqlalchemy.Column(sqlalchemy.String,index=True)
    image = sqlalchemy.Column(sqlalchemy.String,index=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,index=True,default=datetime.datetime.utcnow())
    user = orm.relationship("UserModel",back_populates="posts")

    
    
    