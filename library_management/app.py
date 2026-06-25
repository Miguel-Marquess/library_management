from fastapi import FastAPI

from library_management.routers import users

app = FastAPI()
app.include_router(users.router)


@app.get('/')
def welcome():
    return {'message': 'Welcome to my Library Management!'}
