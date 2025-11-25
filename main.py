from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import os

from my_flask_app.processors.ocr.easyocr_processor import EasyOCRProcessor
from my_flask_app.processors.translation.gemini_translator import GeminiTranslator
from my_flask_app.processors.typesetting.easyocr_typesetter import EasyOCRTypesetter
from my_flask_app.scrapers.scraper_factory import ScraperFactory
from my_flask_app.services.translation_service import TranslationService


load_dotenv()

app = FastAPI()

app.mount('/pages', StaticFiles(directory='uploads'), name='pages')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

translator_service = TranslationService(ScraperFactory(), EasyOCRProcessor(), GeminiTranslator(), EasyOCRTypesetter())
site_url = os.getenv("SITE_URL", "http://localhost:8000")

@app.post("/raw")
async def translate_links(link: str = Body(..., embed=True), target_lang: str = Body("en")):
    """
    Accepts a chapter raw link, scrapes the link for pages, extracts the text, translates it,
    typesets it back onto the page and returns links to the new images.
    """
    scraper = translator_service.scraper_factory.get_scraper(link)

    if scraper:
      id = scraper.get_id(link) + "-" + target_lang
      folder = Path("uploads") / id
      if folder.exists() and folder.is_dir():
        return id

    links = [link]

    id = translator_service.process_links(links, target_lang)

    if not id:
      raise HTTPException(500, "Error translating")

    return id


@app.post("/upload")
async def translate_upload(images: list[UploadFile] = File(...), target_lang: str = Body("en")):
    """
    Accepts a list of files, extracts the files if it includes a zip file, extracts the text, translates it,
    typesets it back onto the page and returns links to the new images.
    """
    file_objects = [file for file in images]

    id = translator_service.process_upload(file_objects, target_lang)
    
    if not id:
      raise HTTPException(500, "Error translating")

    return id


@app.get("/chapter")
def get_chapter(id: str):
  folder = Path("uploads") / id

  if not folder.exists() or not folder.is_dir():
    raise HTTPException(404, "No pages found")

  images = sorted([file for file in folder.iterdir() if file.suffix.lower() == ".png"], key=lambda x: x.name)

  if not images:
    raise HTTPException(404, "No pages found")

  return [f"{site_url}/pages/{id}/{image.name}" for image in images]
