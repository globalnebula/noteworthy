import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from fpdf import FPDF
from io import BytesIO
import tempfile
import base64

def blend_text(background, text, position, font, color="black", alpha=0.8):
    temp_img = Image.new("RGBA", background.size, (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text(position, text, font=font, fill=(0, 0, 0, int(255 * alpha)))

    blended = Image.alpha_composite(background.convert("RGBA"), temp_img)
    return blended.convert("RGB")

def text_to_handwriting(text, ruled_image_path=None, line_spacing=60):
    font_path = "hand.otf"
    font = ImageFont.truetype(font_path, 30)
    lines = text.split("\n")
    img_width, img_height = 800, 1200

    if ruled_image_path:
        background = Image.open(ruled_image_path).resize((img_width, img_height))
    else:
        background = Image.new("RGB", (img_width, img_height), color="white")

    margin, padding = 89.5, 50
    current_y = margin

    for line in lines:
        words = line.split(" ")
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            bbox = ImageDraw.Draw(background).textbbox((0, 0), test_line, font=font)
            test_line_width = bbox[2] - bbox[0]
            if test_line_width < img_width - 2 * margin:
                current_line = test_line
            else:
                background = blend_text(background, current_line, (margin, current_y), font)
                current_line = word + " "
                current_y += line_spacing
        background = blend_text(background, current_line, (margin, current_y), font)
        current_y += line_spacing

    return background

def create_pdf(img):
    pdf = FPDF()
    pdf.add_page()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img_file:
        img.save(temp_img_file, format="PNG")
        temp_img_file.seek(0)
        pdf.image(temp_img_file.name, 0, 0, 210, 297)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf_file:
        pdf.output(temp_pdf_file.name)
        temp_pdf_file.seek(0)

        pdf_byte_arr = BytesIO()
        pdf_byte_arr.write(temp_pdf_file.read())
        pdf_byte_arr.seek(0)

    return pdf_byte_arr

def display_pdf(pdf_data):
    base64_pdf = base64.b64encode(pdf_data.getvalue()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def footer():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #131720;
            color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 14px;
        }
        </style>
        <div class="footer">
            <p>Made with 💖 by Kunal Achintya Reddy | <a style="color: #f1f1f1; text-decoration: none;", href="https://github.com/globalnebula/noteworthy" target="_blank">GitHub</a> | <a style="color: #f1f1f1; text-decoration: none;", href="https://linkedin.com/in/kunalachintyareddy" target="_blank">LinkedIn</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.title("Text to Handwriting")
st.subheader("For all my fellow Bums 😉")

user_text = st.text_area("Enter your text:")
ruled_lines_option = st.checkbox("Add ruled lines from image", value=False)
line_spacing = st.slider("Line Spacing", min_value=30, max_value=100, value=60)

if st.button("Generate Handwriting"):
    ruled_image_path = "ruled.png" if ruled_lines_option else None
    img = text_to_handwriting(user_text, ruled_image_path=ruled_image_path, line_spacing=line_spacing)
    pdf_data = create_pdf(img)

    display_pdf(pdf_data)
    st.download_button("Download PDF", data=pdf_data, file_name="handwritten_notes.pdf", mime="application/pdf")

footer()
