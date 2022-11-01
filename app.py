
from fastapi import FastAPI, HTTPException, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Text
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from status_code import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
import uvicorn
from random import  randint
from decouple import  config

app = FastAPI()
app.SECRET_KEY = config('SECRET_KEY_APP')

def randomNumb():
    id = randint(1_000, 999_999)
    return id
# connect to our Database and settings (credentials)
user_name = config('BD_USERNAME')
user_password = config('DB_PASSWORD')

connect_link = f"mongodb+srv://{user_name}:{user_password}@cluster0.8poqlow.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connect_link)


# instantiate db
db = client.blogapi

# to access the blog collections
blog = db.blogs

# models - schema
class Blog(BaseModel):
    blog_id: int
    title: str
    description: Text
    created: datetime = datetime.utcnow()

# update blog post
class UpdateBlog(Blog):
    title: str
    description: Text



# normal route
@app.get("/", status_code=200)
async def welcome():
    return {"message": "Welcome to a simple blog with FastAPI and MongoDB"}

# get all blog posts
@app.get("/posts")
async def all_post():
    all_blogs = blog.find().sort("created", -1)
    data = []
    for i in all_blogs:
        data.append({
        'id': i["blog_id"],
        'title': i['title'],
        'description': i['description'],
        'created': i['created']
        })
    return data
    
# get single blog post
@app.get("/post/{blog_id}")
async def single_post(blog_id: int):
    singleBlog = blog.find_one({'blog_id': blog_id})
    if not singleBlog: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No blog post with that id")
    return {
            "id": singleBlog['blog_id'],
            "title": singleBlog['title'],
            "description": singleBlog['description'],
            "created": singleBlog['created']
    }

# delete single blog post
@app.delete("/post/{blog_id}")
async def single_post(blog_id: int):
    singleBlog = blog.find_one({'blog_id': blog_id})
    if not singleBlog:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No blog post with that id")
    blog.find_one_and_delete({"blog_id": blog_id})
    return {"message":"Blog deleted"}


# update post
@app.put('/post/{blog_id}')
async def add_post(post: UpdateBlog, blog_id:int):
    singleBlog = blog.find_one({'blog_id': blog_id})
    if not singleBlog:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No blog post with that id")
    title = post.title
    description = post.description
    blog.update_one({'blog_id': blog_id}, {"$set": {
            "title": title,
            "description": description
        }}),
    return {'message': "Blog successfully updated"}


# patch a post
@app.patch('/post/{blog_id}')
async def add_post(post: UpdateBlog, blog_id:int):
    singleBlog = blog.find_one({'blog_id': blog_id})
    if not singleBlog:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No blog post with that id")
    
    if post.title == "string":
        title = singleBlog['title']
    else:
        title = post.title
    
    if post.description == "string":
        description = singleBlog['description']
    else:
        description = post.description
    blog.update_one({'blog_id': blog_id}, {"$set": {
            "title": title,
            "description": description
        }}),
    return {'message': "Blog successfully updated"}


# create blog post
@app.post('/post')
async def add_post(post: Blog):
    post.blog_id = randomNumb()
    blog.insert_one(post.dict())
    return {'message': "Blog successfully created"}

