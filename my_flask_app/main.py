from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/raw")
def translate_links(link: str):
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