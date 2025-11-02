from flask import Flask, render_template, request, send_file# type: ignore
import base64, io, os
from aes_module import derive_key, encrypt_neqr, decrypt_neqr, reconstruct_image
from quantum import load_image, pixels_to_neqr


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    image_data = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "encrypt":
            user_key = request.form["key"]
            key = derive_key(user_key)
            file = request.files["image"]
            image_path = os.path.join(UPLOAD_FOLDER, "input.png")
            file.save(image_path)

            pixels = load_image(image_path)
            neqr_data = pixels_to_neqr(pixels)
            ciphertext_path = os.path.join(OUTPUT_FOLDER, "encrypted.txt")
            encrypt_neqr(neqr_data, key, ciphertext_path)

            result = "Image encrypted successfully!"
            return send_file(ciphertext_path, as_attachment=True)

        elif action == "decrypt":
            user_key = request.form["key"]
            key = derive_key(user_key)
            file = request.files["ciphertext"]
            ciphertext_b64 = file.read().decode()
            pixels = decrypt_neqr(ciphertext_b64, key)
            img = reconstruct_image(pixels)
            img_path = os.path.join(OUTPUT_FOLDER, "decrypted.png")
            img.save(img_path)

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            image_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

            result = "Image decrypted successfully!"
            return render_template("index.html", result=result, image_data=image_data)

    return render_template("index.html", result=result, image_data=image_data)


if __name__ == "__main__":
    app.run(debug=True)
