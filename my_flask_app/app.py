from .__init__ import create_app

app = create_app()

@app.route("/link")
def link():
    pass