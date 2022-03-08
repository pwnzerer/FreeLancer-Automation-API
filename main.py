import json
import math
import sys
import time
from cgi import test
from ctypes import cast
from email import message
from pathlib import Path
from pickle import LIST
from re import M
from typing import List, Optional
from urllib import request, response

import starlette.status as status
import uvicorn
from decouple import config
from fastapi import Body, Depends, FastAPI, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pydantic.fields import ModelField
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

import models
from database import SessionLocal, engine
from initialize import headers
from initialize_driver import *
from loginfunc import *
from models import negative_keywords, templatesinfo
from scrapper import *

# from ssl import _PasswordType

models.Base.metadata.create_all(bind=engine)


class exit_message(BaseModel):
    msg: str


class logindata(BaseModel):
    username: str
    password: str


class settingspage(BaseModel):
    template_ids: list
    job_ids: list
    time_for_bid: int
    country_list: list
    min_avg_rate: int
    min_avg_price: int
    total_bids: int


class add_template(BaseModel):
    template_name: str
    template_words: str
    keywords: str


class negative_keywordz(BaseModel):
    neg_key: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


user = config("USER_NAME", cast=str)
password = config("USER_PASWORD", cast=str)


app = FastAPI()
origins = [
    "http://localhost:4200",
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.get("/login", response_class=HTMLResponse)
# async def root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
@app.post("/shutdown")
async def stop_program(request: Request, message: exit_message):
    msg = message.msg
    sys.exit(f"{msg}")


@app.post("/login", response_model=logindata)
async def login_caller(request: Request, LoginData: logindata):
    user = LoginData.username
    password = LoginData.password
    print(user, password)
    driver = initialize_driver()
    login(driver, user, password)


# @app.get("/settings", response_class=HTMLResponse)
# async def settingspage(request: Request, db: Session = Depends(get_db)):
#     alltempdata = db.query(templatesinfo).all()
#     return templates.TemplateResponse("scrapper_parameters.html", {"request": request, "alltempdata": alltempdata})


@app.post("/settings")
async def settings_page(settings_page_data: settingspage):
    list_of_template_ids = settings_page_data.template_ids
    jobidlist = settings_page_data.job_ids
    timeforbid = settings_page_data.time_for_bid
    total_bids = settings_page_data.total_bids
    country_list = settings_page_data.country_list
    min_avg_hourly_rate = settings_page_data.min_avg_rate
    min_avg_price = settings_page_data.min_avg_price
    paramz = make_params(jobidlist, country_list, min_avg_hourly_rate, min_avg_price)
    all_jobs = get_all_jobs(FREELANCE_BASE_URL, headers, paramz)
    time_to_bid(all_jobs, timeforbid, list_of_template_ids, total_bids)
    return {"status": True, "message": "Automation started"}


# @app.get("/addtemplate", response_class=HTMLResponse)
# # this param remember db: Session = Depends(get_db)
# async def add_templates(request: Request, db: Session = Depends(get_db)):
#     # template_data = templatesinfo("asdadsa", "asdadasda", "asdasd")
#     # db.add(template_data)
#     # db.commit()
#     alltempdata = db.query(templatesinfo).all()
#     return templates.TemplateResponse("maketemplate.html", {"request": request, "alltempdata": alltempdata})


@app.post("/addtemplate")
async def addtemplates(
    addingtemplate: add_template,
    db: Session = Depends(get_db),
):
    templatename = addingtemplate.template_name
    templatetext = addingtemplate.template_words
    keywords = addingtemplate.keywords
    template_data = templatesinfo(templatename, templatetext, keywords)
    db.add(template_data)
    db.commit()
    return {"status": True, "message": "template added"}


@app.get("/getnegativekeywords/")
async def negativeee_keywords(db: Session = Depends(get_db)):
    allkeydata = db.query(negative_keywords).all()
    return allkeydata


@app.post("/addnegativekeywords")
async def negativekeywords(negkeyclass: negative_keywordz, db: Session = Depends(get_db)):
    neg_key = negkeyclass.neg_key
    keyworddata = negative_keywords(neg_key)
    db.add(keyworddata)
    db.commit()
    return {"status": True, "message": "keyword added"}


@app.get("/getalltemplaedata")
async def alldatatemplate(db: Session = Depends(get_db)):
    alltempdata = db.query(templatesinfo).all()
    return alltempdata


# @app.get("/testing", response_class=HTMLResponse)
# async def testtest(request: Request, db: Session = Depends(get_db)):
#     alltestingdata = db.query(templatesinfo).all()
#     return templates.TemplateResponse("test.html", {"request": request, "alltestingdata": alltestingdata})


# @app.post("/testing/{data}")
# async def testtest1(data, request: Request, db: Session = Depends(get_db)):
#     responce = json.loads(data)
#     listofids = responce["favorite"]
#     print("our data is", params)
#     alltestingdata = db.query(templatesinfo).all()
#     # print(json.loads(jsdata))
#     return templates.TemplateResponse("test.html", {"request": request, "alltestingdata": alltestingdata})


# @app.get("/")
# async def get_form_data(
#     ml_keywords: List[str] = Query(ml_keywords),
#     is_ml: bool = Query(
#         False,
#         choices=(True, False),
#         description="is ML tempalte service is required - by default False",
#     ),
#     wb_keywords: List[str] = Query(web_keywords),
#     is_wb: bool = Query(
#         False,
#         choices=(True, False),
#         description="is Web tempalte service is required - by default False",
#     ),
#     mb_keywords: List[str] = Query(mob_keywords),
#     is_mb: bool = Query(
#         False,
#         choices=(True, False),
#         description="is Mobile tempalte service is required - by default False",
#     ),
#     wp_keywords: List[str] = Query(wordpress_keywords),
#     is_wp: bool = Query(
#         False,
#         choices=(True, False),
#         description="is Word Press tempalte service is required - by default False",
#     ),
# ):
#     payload = {
#         "ml": {
#             "is_ml": is_ml,
#             "ml_keywords": ml_keywords,
#         },
#         "wb": {
#             "is_wb": is_wb,
#             "wb_keywords": wb_keywords,
#         },
#         "mb": {
#             "is_mb": is_mb,
#             "mb_keywords": mb_keywords,
#         },
#         "wp": {
#             "is_wp": is_wp,
#             "wp_keywords": wp_keywords,
#         },
#     }
#     print(payload)

#     main(payload)

#     return {"message": "all good", "payload": json.dumps(payload)}
