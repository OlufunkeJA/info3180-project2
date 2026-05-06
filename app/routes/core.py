from app.routes.common import api_bp, current_app, jsonify, request


@api_bp.route("/")
def index():
    return jsonify(message="This is the beginning of our API")


@api_bp.route("/<file_name>.txt")
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + ".txt"
    return current_app.send_static_file(file_dot_text)


@api_bp.after_app_request
def add_header(response):
    """Apply cache and compatibility headers."""
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"

    if request.method == "GET":
        response.headers["Cache-Control"] = "public, max-age=0"
    else:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"

    return response


@api_bp.app_errorhandler(404)
def page_not_found(error):
    """Custom 404 response."""
    return jsonify(error="Resource not found."), 404
