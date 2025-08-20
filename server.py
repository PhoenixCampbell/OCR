def do_POST(s):
    response_code = 200
    response = ""
    var_len = int(s.headers.get('Content-Length'))
    content = s.rfile.read(var_len);
    payload = json.loads(content);

    if payload.get('train'):
        nn.train(payload['trainArray'])
        nn.save()
    elif payload.get('predict'):
        try:
            arr = payload['image']            # this is a length-400 list of floats
            response = {"type":"test", "result": int(nn.predict(arr))}
        except Exception as e:
            response_code = 500
            response = {"error": str(e)}
    else:
        response_code = 400
    
    s.send_response(response_code)
    s.send_header("Content-type", "application/json")
    s.send_header("access-Control-Allow-Origin", "*")
    s.end_headers()
    if response:
        s.wfile.write(json.dumps(response))
    return