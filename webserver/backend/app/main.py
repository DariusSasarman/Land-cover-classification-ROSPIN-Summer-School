from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/", StaticFiles(directory="./app/static",html = True), name="static")


class SignUpRequest():
    name: str
    organization: str
    email: str
    password: str

@app.post("/api/land-cover/signup")
async def signup(info: SignUpRequest):
    # Here you would typically handle the signup logic, such as saving the user info to a database
    return {"message": "Signup successful", "user": info}

class LoginRequest():
    email: str
    password: str

@app.post("/api/land-cover/login")
async def login(info: LoginRequest):
    # Here you would typically handle the login logic, such as verifying the user's credentials
    return {"message": "Login successful", "user": info}


@app.post("/api/land-cover/demo/{}")
async def demo_request(area_id : str):
    # Here you would typically handle the demo request logic, such as processing the request and sending an email
    return {"message": "Demo request received", "request": info}

class JwtToken():
    token: str

@app.post("/api/land-cover/list")
async def list_requests(token: JwtToken):
    # Here you would typically retrieve the list of requests from a database or other storage
    return {"message": "List of requests", "requests": []}

class RequestInfo():
    area_of_interest: str
    additional_info: str

@app.post("/api/land-cover/createaoi")
async def create_aoi(info: RequestInfo):
    # Here you would typically handle the creation of an area of interest, such as saving the info to a database
    return {"message": "Area of interest created", "info": info}