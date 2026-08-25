from flask import jsonify, render_template

from app.main import main


@main.get("/")
def index():
    return render_template("main/index.html")


@main.get("/health")
def health():
    return jsonify(status="ok")
