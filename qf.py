# pip安装 fastapi 和 uvicorn
# 执行 "uvicorn main:app --host=0.0.0.0 --port=8000 --reload" 启动服务端

import json
import requests

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


app = FastAPI()

# 允许前端跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_access_token(ak, sk):
    auth_url = "https://aip.baidubce.com/oauth/2.0/token"
    resp = requests.get(auth_url, params={"grant_type": "client_credentials", "client_id": ak, 'client_secret': sk})
    return resp.json().get("access_token")

def get_stream_response(prompt):
    ak = "Wj9AlKe250p6F0zcYegIprMb"
    sk = "fi2mfzwBl7ktNXDWG3J0Olpj5ox128a6"
    source = "&sourceVer=0.0.1&source=app_center&appName=streamDemo"
    # 大模型接口URL
    base_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro"
    url = base_url + "?access_token=" + get_access_token(ak, sk) + source
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    payload = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, headers=headers, data=payload, stream=True)

def gen_stream(prompt):
    response = get_stream_response(prompt)
    for chunk in response.iter_lines():
        chunk = chunk.decode("utf8")
        if chunk[:5] == "data:":
            chunk = chunk[5:]
        yield chunk

@app.post("/eb_stream")    # 前端调用的path
async def eb_stream(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    return StreamingResponse(gen_stream(prompt))