from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, traceback, os
import numpy as np

WEIGHTS_PATH = "ocr_weights.json"

def one_hot(y, k=10):
    v = np.zeros((k,), dtype=np.float32); v[int(y)] = 1.0; return v

class OCRNeuralNetwork:
    def __init__(self, sizes=(400, 64, 10), lr=0.05, load_if_exists=True):
        self.n_in, self.n_h, self.n_out = sizes
        rng = np.random.default_rng(42)
        self.W1 = rng.normal(0, 0.1, (self.n_h, self.n_in)).astype(np.float32)
        self.b1 = np.zeros((self.n_h,), dtype=np.float32)
        self.W2 = rng.normal(0, 0.1, (self.n_out, self.n_h)).astype(np.float32)
        self.b2 = np.zeros((self.n_out,), dtype=np.float32)
        self.lr = float(lr)
        if load_if_exists: self.load()

    def _forward(self, x):
        z1 = self.W1 @ x + self.b1
        h1 = np.maximum(z1, 0.0)
        z2 = self.W2 @ h1 + self.b2
        z2 -= z2.max()
        exp = np.exp(z2); yhat = exp / (exp.sum() + 1e-8)
        return h1, yhat

    def predict(self, x):
        x = np.asarray(x, dtype=np.float32).reshape(-1)
        if x.size != self.n_in: raise ValueError(f"Expected 400 inputs, got {x.size}")
        _, yhat = self._forward(x)
        return int(np.argmax(yhat))

    def train(self, trainArray, epochs=1, batch_size=16):
        data = []
        for item in trainArray:
            x = np.asarray(item["y0"], dtype=np.float32).reshape(-1)
            if x.size != self.n_in: continue
            y = int(item["label"])
            data.append((x, one_hot(y, self.n_out)))
        if not data: return
        for _ in range(epochs):
            rng = np.random.default_rng(); rng.shuffle(data)
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                dW1 = np.zeros_like(self.W1); db1 = np.zeros_like(self.b1)
                dW2 = np.zeros_like(self.W2); db2 = np.zeros_like(self.b2)
                for x, y in batch:
                    h1, yhat = self._forward(x)
                    dz2 = (yhat - y)
                    dW2 += np.outer(dz2, h1); db2 += dz2
                    dh1 = self.W2.T @ dz2
                    dz1 = dh1 * (h1 > 0)
                    dW1 += np.outer(dz1, x); db1 += dz1
                m = len(batch)
                self.W2 -= self.lr * (dW2 / m); self.b2 -= self.lr * (db2 / m)
                self.W1 -= self.lr * (dW1 / m); self.b1 -= self.lr * (db1 / m)

    def save(self, path=WEIGHTS_PATH):
        with open(path, "w") as f:
            json.dump({"W1": self.W1.tolist(), "b1": self.b1.tolist(),
                       "W2": self.W2.tolist(), "b2": self.b2.tolist()}, f)

    def load(self, path=WEIGHTS_PATH):
        if not os.path.exists(path): return
        with open(path, "r") as f:
            obj = json.load(f)
        self.W1 = np.array(obj["W1"], dtype=np.float32)
        self.b1 = np.array(obj["b1"], dtype=np.float32)
        self.W2 = np.array(obj["W2"], dtype=np.float32)
        self.b2 = np.array(obj["b2"], dtype=np.float32)

nn = OCRNeuralNetwork(sizes=(400, 64, 10), lr=0.05, load_if_exists=True)

class Handler(SimpleHTTPRequestHandler):
    # Serve / as /ocr.html
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/ocr.html"
        return super().do_GET()

    # CORS for all responses
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path != "/ocr":
            self.send_error(404, "Not Found")
            return
        code = 200
        resp = {}
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
            if payload.get("train"):
                nn.train(payload["trainArray"])
                nn.save()
                resp = {"ok": True, "type": "train"}
            elif payload.get("predict"):
                pred = int(nn.predict(payload["image"]))
                resp = {"ok": True, "type": "test", "result": pred}
            else:
                code = 400; resp = {"ok": False, "error": "Bad request"}
        except Exception as e:
            code = 500
            resp = {"ok": False, "error": str(e), "trace": traceback.format_exc()}

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp).encode("utf-8"))

def main():
    addr = ("127.0.0.1", 8000)
    print(f"Serving OCR app on http://{addr[0]}:{addr[1]}")
    # Run from the folder that contains ocr.html/ocr.js
    HTTPServer(addr, Handler).serve_forever()

if __name__ == "__main__":
    main()
