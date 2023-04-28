import database as db
import models
import sqlalchemy.orm
import schemas
import email_validator 
from fastapi import HTTPException , Depends , security
import passlib.hash
import jwt


JWT_SECRET_KEY ='FNDVJFNVKFDNVKDCNJDBJHGXDKSJNL'
oauth2schema = security.OAuth2PasswordBearer('/api/v1/login')


def create_db():
    return db.Base.metadata.create_all(bind=db.engine)



def get_db():
    databese = db.SessionLocal()
    try:
        yield databese
    finally:
        databese.close()
create_db()

async def GetUserByEmail(
    email:str, 
    db:sqlalchemy.orm.Session
):
    
    return db.query(models.UserModel).filter(models.UserModel.email == email).first()


async  def create_user(user:schemas.UserRequest, db:sqlalchemy.orm.Session):
    
    #check for validation email
    try:
        invalid_email = email_validator.validate_email(email=user.email)
        # email = isValid(email)
    except email_validator.EmailNotValidError:
        raise HTTPException(status_code=400,detail="PROVIDE valid email")
    
    #create hash password
    hashed_password = passlib.hash.bcrypt.hash(user.password)
    user_obj = models.UserModel(email=user.email,name = user.name,phone = user.phone,password_hash = hashed_password,)
    
    # save and commit user
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj    
    
    
async def create_token(user:models.UserModel):
    
    
    user_shema = schemas.UserResponse.from_orm(user)
    # convert object to dictinaory
    user_dict = user_shema.dict()
    del user_dict['created_at']
    
    token = jwt.encode(user_dict,JWT_SECRET_KEY)
    return dict(access_token=token,token_type='bearer')

    

async def login(
    email:str, 
    password:str,
    db:sqlalchemy.orm.Session
):
    
    db_user = await GetUserByEmail(email=email,db=db)
    
    #return flase no user email found
    if not db_user:
        return False
    
    #return flase if no user password found 
    if not db_user.password_verification(password=password):
        return False
    
    
    return db_user
    


async def current_user(
    db:sqlalchemy.orm.Session = Depends(get_db),
    token:str=Depends(oauth2schema)
):
    try:
        payload = jwt.decode(token,JWT_SECRET_KEY,algorithms=['HS256'])
        # Get user by id Id is already available in decode user payload
        db_user = db.query(models.UserModel).get(payload['id'])
    except:
        raise HTTPException(status_code=401,detail='wrong credentials')
    
    
    # if all okay return DTO/shcema version user
    return  schemas.UserResponse.from_orm(db_user)


async def create_post(
    user:schemas.UserResponse,
    post:schemas.PostRequest,
    db:sqlalchemy.orm.Session
):
    
    post = models.PostModel(**post.dict(),user_id = user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    # convwer the post model to dto/schema and return API LAYER
    return schemas.PostResponse.from_orm(post)
    
    

async def get_post_by_user(
    user:schemas.UserResponse,
    db:sqlalchemy.orm.Session
):
    
    posts = db.query(models.PostModel).filter_by(user_id=user.id)
    # convert each post model to post chema and make list of posts and return them
    return list(map(schemas.PostResponse.from_orm,posts))



async def get_post_all(
    db:sqlalchemy.orm.Session
):
    
    posts = db.query(models.PostModel)
    return list(map(schemas.PostResponse.from_orm,posts))



async def get_post_detail(
    post_id:int,
    db:sqlalchemy.orm.Session
):
    
    db_post = db.query(models.PostModel).filter(models.PostModel.id == post_id).first()
    
    if db_post is None:
        raise HTTPException(status_code=404,detail='Post not found')
    
    # return schemas.PostResponse.from_orm(db_post)
    return db_post    
    
    
    
async def get_user_detail(
    user_id:int,
    db:sqlalchemy.orm.Session
):
    
    db_user = db.query(models.UserModel).filter(models.UserModel.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404,detail='User not found')
    
    return schemas.UserResponse.from_orm(db_user)

    
async def delete_post(
    post:models.PostModel,
    db:sqlalchemy.orm.Session
):
    
    db.delete(post)
    db.commit()
    
    
async def update_post_detail(
    post_request:schemas.PostRequest,
    post:models.PostModel,
    db:sqlalchemy.orm.Session
):
    
    post.post_title = post_request.post_title
    post.post_description = post_request.post_description
    post.image  = post_request.image
    
    db.commit()
    db.refresh(post)
    
    
    return schemas.PostResponse.from_orm(post)
    
    
    
    