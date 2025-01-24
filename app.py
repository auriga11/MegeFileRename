from flask import Flask

# Flask setup
app = Flask(__name__)

# Health check endpoint
@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

# Run Flask app
if __name__ == "__main__":
    app.run()
