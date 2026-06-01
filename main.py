from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import subprocess


def run_vcgencmd(args: list[str]) -> str:
    """Führt einen vcgencmd-Befehl aus und gibt den Output zurück."""
    try:
        result = subprocess.run(
            ["vcgencmd"] + args,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError(f"vcgencmd Fehler: {result.stderr.strip()}")
        return result.stdout.strip()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="vcgencmd nicht gefunden – läuft das auf einem Raspberry Pi?")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="vcgencmd Timeout")


def measure_temp() -> float:
    output = run_vcgencmd(["measure_temp"])
    # Output-Format: "temp=47.2'C"
    try:
        return float(output.split("=")[1].split("'")[0])
    except (IndexError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Konnte Temperatur nicht parsen: {output!r}")


def measure_freq() -> int:
    output = run_vcgencmd(["measure_clock", "arm"])
    # Output-Format: "frequency(48)=1400000000"
    try:
        return int(output.split("=")[1])
    except (IndexError, ValueError):
        raise HTTPException(status_code=500, detail=f"Konnte Frequenz nicht parsen: {output!r}")


def get_throttle() -> int:
    output = run_vcgencmd(["get_throttled"])
    # Output-Format: "throttled=0x50000"
    try:
        return int(output.split("=")[1], 16)
    except (IndexError, ValueError):
        raise HTTPException(status_code=500, detail=f"Konnte Throttle-Status nicht parsen: {output!r}")


app = FastAPI()

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