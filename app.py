from fastapi import FastAPI , Depends , HTTPException , security
import schemas
import services
from sqlalchemy import orm
from typing import List


app = FastAPI()


@app.post('/api/v1/users')
async def register_user(
    user:schemas.UserRequest,db:orm.Session = Depends(services.get_db)):

    db_user = await services.GetUserByEmail(email=user.email,db=db)
    
    if db_user:
        raise HTTPException(status_code=400,detail="Email already in use")
    
    
    db_user = await services.create_user(user = user , db=db)
    return await services.create_token(user=db_user)



@app.post('/api/v1/login')
async def login_user(
    from_data:security.OAuth2PasswordRequestForm = Depends(),
    db : orm.Session = Depends(services.get_db)
):
    db_user = await services.login(email=from_data.username,password=from_data.password,db=db)
    
    # invalid login then throw exception 
    if not db_user:
        raise HTTPException(status_code=401,detail='wrong login credentials')
    
    # create and return token
    return await services.create_token(db_user) 
    

    
@app.get('/api/v1/users/current',response_model=schemas.UserResponse)
async def current_user(
    user:schemas.UserResponse = Depends(services.current_user)
):
    
    return user
    
    
    
@app.post('/api/v1/posts',response_model=schemas.PostResponse)
async def create_post(
    post_request:schemas.PostRequest,
    user:schemas.UserRequest=Depends(services.current_user),
    db : orm.Session = Depends(services.get_db)
):
    
    return await services.create_post(user = user,db=db,post = post_request)



@app.get('/api/v1/posts/user',response_model=List[schemas.PostResponse])
async def get_post_byuser(
    user:schemas.UserRequest=Depends(services.current_user),
    db : orm.Session = Depends(services.get_db)
    
):

    return await services.get_post_by_user(user=user, db=db)

@app.get('/api/v1/posts/all',response_model=List[schemas.PostResponse])
async def get_post_all(
    db : orm.Session = Depends(services.get_db)
    
):

    return await services.get_post_all(db=db)

@app.get('/api/v1/posts/{post_id}',response_model=schemas.PostResponse)
async def get_post_detail(
    post_id:int,
    db:orm.Session = Depends(services.get_db)
):
    
    post = await services.get_post_detail(post_id = post_id,db = db)
    return post
    

@app.get('/api/v1/users/{user_id}',response_model=schemas.UserResponse)
async def get_user_detail(
    user_id:int,
    db:orm.Session = Depends(services.get_db)
):
    
    return await services.get_user_detail(user_id == user_id,db=db)

    
@app.delete('/api/v1/posts/{post_id}')
async def delete_post(
    post_id:int,
    db:orm.Session = Depends(services.get_db),
    user:schemas.UserRequest=Depends(services.current_user),
):

    post = await services.get_post_detail(post_id=post_id,db=db)
    
    await services.delete_post(post=post,db=db)
    return 'post deleted successfully'



@app.put('/api/v1/posts/{post_id}',response_model=schemas.PostResponse)
async def update_post(
    post_id:int,
    post_request:schemas.PostRequest,
    db:orm.Session = Depends(services.get_db),                             
):

    db_post = await services.get_post_detail(post_id=post_id,db=db)

    return await services.update_post_detail(post_request=post_request,post=db_post,db=db)
