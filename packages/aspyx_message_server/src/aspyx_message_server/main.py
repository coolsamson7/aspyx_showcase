import logging

# setup logging

from aspyx.util import Logger

from aspyx_message_server import PushInterfaceModule

Logger.configure(default_level=logging.INFO, levels={
    "httpx": logging.ERROR,
    "aspyx.di": logging.INFO,
    "aspyx.event": logging.INFO,
    "aspyx.di.aop": logging.INFO,
    "aspyx.service": logging.ERROR
})

import uvicorn
from aspyx_service import RequestContext, FastAPIServer
from fastapi import FastAPI

#from starlette.middleware.cors import CORSMiddleware

# create the application

app = FastAPI()

#app.add_middleware(CORSMiddleware,
#                   allow_origins=[
#                       "http://localhost",
#                       "http://localhost:4200",
#                       "http://127.0.0.1",
#                       "http://127.0.0.1:4200",
#                       "*"
#                   ],
#                   allow_credentials=True,
#                   allow_methods=["POST", "GET", "PUT", "DELETE", "OPTIONS"],#
#                   allow_headers=["*"]#,
#                   expose_headers=["*"],#?
#                   )
#app.add_middleware(RequestContext)
#app.add_middleware(TokenContextMiddleware)

PushInterfaceModule.app = app

FastAPIServer.boot(PushInterfaceModule, host="127.0.0.1", port=8000, start_thread=False)

# run server

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)