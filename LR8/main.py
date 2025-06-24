from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO

app = FastAPI()

@app.post("/size2json")
async def size2json(image: UploadFile = File(...)):
    if image.content_type != "image/png":
        return JSONResponse(
            content={"result": "invalid filetype"},
            media_type="application/json"
        )

    try:
        image_data = await image.read()
        img = Image.open(BytesIO(image_data))
        width, height = img.size
        return JSONResponse(
            content={"width": width, "height": height},
            media_type="application/json"
        )
    except Exception:
        return JSONResponse(
            content={"result": "invalid filetype"},
            media_type="application/json"
        )

@app.get("/login")
async def login():
    return JSONResponse(
        content={"author": "1147241"},
        media_type="application/json"
    )
