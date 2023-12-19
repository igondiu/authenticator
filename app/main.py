import importlib
import logging
from os import getcwd, chdir, listdir
from os.path import join, isfile, splitext
from pathlib import Path
import uvicorn

from fastapi import FastAPI, APIRouter
from decouple import config

from app.database import database


def configure_logging(log_dir, app_name, debug):
    fhandler = logging.FileHandler(filename=f'{join(log_dir, app_name)}.log', mode='a')
    logging.basicConfig(
        format="%(asctime)s [%(threadName)-10s] - %(levelname)s - "
               "%(module)s.%(funcName)s(%(lineno)d): %(message)s",
        level=logging.DEBUG if debug else logging.INFO
    )
    logging.getLogger().addHandler(fhandler)
    logging.debug("Logger successfully configured")


def auto_include_routers(app):
    path = "app/routers"
    previous_directory = getcwd()
    base_dir = Path(__file__).resolve().parent.parent

    chdir(base_dir)
    files = [
        splitext(f)[0]
        for f in listdir(path)
        if isfile(join(path, f)) and f.lower().endswith(".py")
    ]
    path = path.replace("/", ".")
    path = path.replace("\\", ".")
    for file in files:
        module = importlib.import_module(path + "." + file)
        for item in dir(module):
            router = getattr(module, item)
            if isinstance(router, APIRouter):
                app.include_router(router)

    chdir(previous_directory)


def create_app():
    application = FastAPI()

    configure_logging(config("LOG_DIR"), config("APP_NAME"), config("DEBUG", default=False))

    database.Base.metadata.create_all(bind=database.engine)
    try:
        auto_include_routers(application)
    except Exception as e:
        logging.critical(f"Something failed while register routes: \n{e}")
        exit(1)

    return application


if __name__ == "__main__":
    uvicorn.run(create_app(), port=8000, host="localhost")
