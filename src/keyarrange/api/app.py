"""FastAPI backend — wraps Pipeline and serves MIDI + piano roll."""
import asyncio
import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from keyarrange.pipeline import Pipeline
from keyarrange.render.piano_roll import render_piano_roll

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

app = FastAPI(title="KeyArrange")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("/tmp/keyarrange/uploads")
OUTPUT_DIR = Path("/tmp/keyarrange/outputs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Serve frontend
from pathlib import Path
WEB_DIR = Path(__file__).parent.parent.parent.parent / "web"  # src/keyarrange/api/app.py → repo root
app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")


@app.get("/", response_class=HTMLResponse)
async def root():
    return (WEB_DIR / "index.html").read_text()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".mp3", ".wav")):
        raise HTTPException(status_code=400, detail="Only MP3 and WAV files are supported.")

    job_id = Path(file.filename).stem[:40].replace(" ", "_") + "_" + uuid.uuid4().hex[:6]
    upload_path = UPLOAD_DIR / f"{job_id}{Path(file.filename).suffix}"
    upload_path.write_bytes(await file.read())

    logger.info(f"Job {job_id}: starting pipeline")

    try:
        loop = asyncio.get_event_loop()
        midi_path, piano_roll_path, pdf_path = await loop.run_in_executor(None, _run_pipeline, str(upload_path), job_id)
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

    return {
        "job_id": job_id,
        "midi_url": f"/download/midi/{job_id}",
        "piano_roll_url": f"/download/piano_roll/{job_id}" if piano_roll_path else None,
        "pdf_url": f"/download/pdf/{job_id}" if pdf_path else None,
    }


def _run_pipeline(upload_path: str, job_id: str) -> tuple[str, str | None, str | None]:
    """Synchronous pipeline call — run in executor to avoid blocking event loop."""
    output_dir = str(OUTPUT_DIR / job_id)
    pipeline = Pipeline(upload_path, output_dir)
    return pipeline.run()


@app.get("/download/{file_type}/{job_id}")
async def download(file_type: str, job_id: str):
    if file_type == "midi":
        # Pipeline writes to OUTPUT_DIR/job_id/<song_name>/arranged/arranged.mid
        # Glob for it since song_name is embedded in path
        matches = list((OUTPUT_DIR / job_id).rglob("arranged.mid"))
        if not matches:
            raise HTTPException(status_code=404, detail="MIDI file not found.")
        return FileResponse(str(matches[0]), media_type="audio/midi", filename="keyarrange.mid")

    elif file_type == "piano_roll":
        matches = list((OUTPUT_DIR / job_id).rglob("piano_roll.png"))
        if not matches:
            raise HTTPException(status_code=404, detail="Piano roll not found.")
        return FileResponse(str(matches[0]), media_type="image/png")

    elif file_type == "pdf":
        matches = list((OUTPUT_DIR / job_id).rglob("arranged.pdf"))
        if not matches:
            raise HTTPException(status_code=404, detail="PDF not found.")
        return FileResponse(str(matches[0]), media_type="application/pdf", filename="keyarrange.pdf")

    else:
        raise HTTPException(status_code=400, detail="file_type must be 'midi' or 'piano_roll'.")
