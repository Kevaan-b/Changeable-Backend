from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/raw")
def translate_links(link: str = Body(..., embed=True)):
    return [
    'https://gg.asuracomic.net/storage/media/182960/conversions/02-optimized.webp',
    'https://gg.asuracomic.net/storage/media/183029/conversions/03-optimized.webp',
    'https://gg.asuracomic.net/storage/media/183096/conversions/04-optimized.webp',
  ]

@app.post("/images")
def translate_images(images: list[UploadFile] = File(...)):
    return [
    'https://gg.asuracomic.net/storage/media/182960/conversions/02-optimized.webp',
    'https://gg.asuracomic.net/storage/media/183029/conversions/03-optimized.webp',
    'https://gg.asuracomic.net/storage/media/183096/conversions/04-optimized.webp',
  ]