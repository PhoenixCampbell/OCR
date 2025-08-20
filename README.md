# OCR Canvas + Python NN (Local Demo)

Draw a digit in the browser, downscale it to **20×20** pixels, and send it to a tiny **NumPy** neural network for **training** and **prediction** over a simple HTTP API. Trained weights persist to `ocr_weights.json` so you can teach a few examples and test immediately.

## Features

-   🖊️ Canvas drawing with mouse/touch (200×200 → 20×20 downscale).
-   🔢 Minimal 2‑layer NN (400→64→10) implemented with NumPy.
-   💾 Weights auto‑save/load (`ocr_weights.json`).
-   ✅ Subtle green screen flash on successful **Train** (no popups).
-   🌐 Single endpoint: `POST /ocr` handles `train` and `predict`.

---

## Project Structure

```
.
├─ ocr.html                  # UI with canvas + controls
├─ ocr.js                    # Drawing, downscale, API calls, flash effect
├─ ocr.css                   # (optional) styles; includes green flash overlay
├─ server.py                 # Static file server + /ocr API + NumPy NN
├─ ocr_weights.json          # (generated) saved weights
├─ neural_network_design.py
├─ ocr.py
└─ requirements.txt          # numpy
```

## Prerequisites

-   Python **3.9+** (tested up to 3.13)
-   pip (and optionally `venv`)

---

## Quickstart (One‑Server Setup)

1. **Install dependencies**

```bash
# (recommended) create and activate a venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
# or: pip install numpy
```

2. **Run the app**

```bash
python server.py
```

You should see:

```
Serving OCR app on http://127.0.0.1:8000
```

3. **Open the UI**  
   Go to `http://127.0.0.1:8000/` (this maps `/` → `ocr.html`).

---

## How to Use

1. Draw a digit (0–9) on the canvas.
2. Enter the label (single digit) in the input field.
3. Click **Train** → the screen flashes **soft green** for ~1s on success.
4. Click **Test** to get a prediction for the current drawing.
5. Click **Reset** to clear the canvas.

> The front‑end downsamples to **20×20**, normalizes to `[0,1]` (black ≈ 1), and sends an array of **400** floats.

## Weights & Persistence

-   Saved to **`ocr_weights.json`** in the same folder as `server.py`.
-   Updated **only when you train**. Predict does not write the file.
-   Delete the file to reset training; restart the server to re‑init random weights.
-   To change the path, edit `WEIGHTS_PATH` near the top of `server.py`.

---

## Requirements

See `requirements.txt` (NumPy only).

---

## Acknowledgments

A lightweight teaching/demo project—browser canvas + minimal NumPy model—to illustrate end‑to‑end OCR without heavy frameworks.
