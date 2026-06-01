from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from os import popen
from pathlib import Path

def measure_temp():
    r = popen("vcgencmd measure_temp").read()
    r = r.split("=")[1].split("'")[0]
    return float(r)

def measure_freq():
    r = popen("vcgencmd measure_clock arm").read()
    r = r.split("=")[1]
    return int(r)

def get_throttle():
    r = popen("vcgencmd get_throttled").read()
    r = r.split("=")[1].strip()
    return int(r, 16)

app = FastAPI()

# serve templates and static frontend
base_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(base_dir / "templates"))
app.mount("/static", StaticFiles(directory=str(base_dir / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/cpu-temp")
def cpu_temp():
    return {"temperature": measure_temp()}


@app.get("/cpu-freq")
def cpu_freq():
    return {"frequency": measure_freq()}


@app.get("/throttle")
def throttle():
    return {"throttled": get_throttle()}