from fastapi import FastAPI

from library_management.routers import auth, users

app = FastAPI(title='Library System', version='0.1.0')
app.include_router(users.router)
app.include_router(auth.router)


@app.get('/')
def welcome():
    return {'message': 'Welcome to my Library Management!'}
