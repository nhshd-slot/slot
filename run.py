import os

from slot import app

# Lists all routing rules registered on the Flask app
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port = port,
        debug=True
    )
