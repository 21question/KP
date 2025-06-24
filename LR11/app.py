from fastapi import FastAPI, UploadFile, Form, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ... остальные маршруты ...


@app.get("/login")
async def login():
    return {"author": "1147241"}


@app.post("/decypher")
async def decypher(
    key: UploadFile = File(..., description="PEM приватный ключ"),  # Используем File()
    secret: str = Form(..., description="Зашифрованные данные в base64")
):
    try:
        # Чтение приватного ключа
        private_key_data = await key.read()
        private_key = serialization.load_pem_private_key(
            private_key_data,
            password=None,
            backend=default_backend()
        )

        # Дешифровка
        decrypted = private_key.decrypt(
            base64.b64decode(secret),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return {"decrypted": decrypted.decode()}

    except Exception as e:
        return {"error": str(e)}