"""
Main Streamlit application for the Eid Card Generator
"""
import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO
import random
import base64
from fpdf import FPDF
import tempfile
import time
from agents import generate_eid_message
from tools import style_card, get_available_themes
from utils import get_pexels_image, BACKGROUND_CATEGORIES
from utils.font_utils import download_google_fonts
import emoji

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Eid Card Generator",
    page_icon="🌙",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.card {
    max-width: 800px;
    margin: 0 auto 30px auto;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    position: relative;
    min-height: 500px;
}
.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.5));
    backdrop-filter: blur(3px);
    z-index: 1;
}
.card-inner {
    position: relative;
    z-index: 2;
    padding: 40px;
}
.card-title {
    font-size: 2.2em;
    margin-bottom: 30px;
    color: #1a1a1a;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.6);
}
.card-content {
    font-size: 1.3em;
    line-height: 1.8;
    color: #1a1a1a;
    white-space: pre-line;
    margin: 20px 0;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.6);
}
.card-signature {
    text-align: right;
    font-style: italic;
    margin-top: 40px;
    color: #1a1a1a;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.6);
}
.urdu-text {
    text-align: center;
    font-size: 1.8em;
    margin-top: 30px;
    color: #1a1a1a;
    text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.6);
}
.download-button {
    display: inline-flex;
    align-items: center;
    padding: 10px 20px;
    border-radius: 8px;
    color: white;
    background-color: #4CAF50;
    text-decoration: none;
    font-weight: 500;
    transition: transform 0.2s;
    cursor: pointer;
    margin: 10px 0;
}
.download-button:hover {
    transform: translateY(-2px);
}
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #4A0404;
    color: #000000;
    text-align: center;
    padding: 10px 0;
    font-size: 1em;
    z-index: 1000;
}
.footer a {
    color: #000000;
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s ease;
}
.footer a:hover {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cards' not in st.session_state:
    st.session_state.cards = []
if 'current_background' not in st.session_state:
    st.session_state.current_background = None
if 'background_category' not in st.session_state:
    st.session_state.background_category = "islamic patterns"

def create_pdf_card(card):
    """Create a PDF version of the card."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(20, 20, 20)
    
    # Add fonts
    pdf.add_font("Roboto", "", "fonts/roboto/roboto.ttf")
    pdf.add_font("Roboto", "B", "fonts/roboto/robotoB.ttf")
    pdf.add_font("Roboto", "I", "fonts/roboto/robotoI.ttf")
    
    # Download and add background image with retry logic
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            session = requests.Session()
            # Set longer timeouts and keep-alive
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
            response = session.get(
                card['background_url'],
                timeout=30,
                stream=True,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()
            
            # Download the image in chunks
            chunks = []
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
            
            image_data = b''.join(chunks)
            bg_image = Image.open(BytesIO(image_data))
            break  # Success, exit retry loop
            
        except (requests.exceptions.RequestException, IOError) as e:
            if attempt == max_retries - 1:  # Last attempt
                # If all retries failed, use a solid color background
                bg_image = Image.new('RGB', (2100, 2970), (255, 255, 255))
                st.warning(f"Could not load background image. Using solid background instead. Error: {str(e)}")
            else:
                time.sleep(retry_delay)
                continue
    
    # Create a white overlay on the background image
    overlay = Image.new('RGBA', bg_image.size, (255, 255, 255, 80))  # 80 = ~31% opacity
    if bg_image.mode != 'RGBA':
        bg_image = bg_image.convert('RGBA')
    bg_with_overlay = Image.alpha_composite(bg_image, overlay)
    bg_with_overlay = bg_with_overlay.convert('RGB')  # Convert to RGB for PDF
    
    # Save background temporarily
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_bg:
        bg_with_overlay.save(temp_bg.name, 'PNG')
        pdf.image(temp_bg.name, x=0, y=0, w=210, h=297)
    os.unlink(temp_bg.name)
    
    # Add content
    pdf.set_text_color(26, 26, 26)
    
    # Title
    pdf.set_font('Roboto', 'B', 24)
    pdf.cell(0, 40, f"Dear {card['recipient']},", new_x="LMARGIN", new_y="NEXT")
    
    # Message
    pdf.set_font('Roboto', '', 14)
    # Remove emojis and clean up the message
    message = card['message']
    message = message.replace("[No Hadith included per your request]", "")
    message = message.replace("Note: Do not include any signature, HTML tags, or styling code.", "")
    message = message.replace("Note: No signature, HTML tags, or styling code is included in this message.", "")
    message = '\n'.join(line.strip() for line in message.split('\n') if line.strip())
    message = ''.join(char for char in message if not is_emoji(char))
    pdf.multi_cell(0, 10, message)
    
    # Urdu text
    pdf.set_font('Roboto', 'B', 24)
    pdf.ln(20)
    pdf.cell(0, 20, "عید مبارک", align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Signature
    pdf.ln(20)
    pdf.set_font('Roboto', 'I', 14)
    pdf.cell(0, 10, "With warm wishes,", align='R', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, card['sender'], align='R', new_x="LMARGIN", new_y="NEXT")
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        pdf.output(temp_pdf.name)
        return temp_pdf.name

def is_emoji(char):
    """Check if a character is an emoji."""
    return char in emoji.EMOJI_DATA

def refresh_background():
    """Refresh the background image based on selected category."""
    st.session_state.current_background = get_pexels_image(st.session_state.background_category)

def create_card(recipient_name, sender_name, tone, include_hadith, include_emojis):
    """Create a new Eid card with the given parameters."""
    try:
        # Get a random font combination
        fonts = download_google_fonts()
        
        # Download and inject Google Fonts
        font_url = fonts["url"]
        st.markdown(f'<link href="{font_url}" rel="stylesheet">', unsafe_allow_html=True)
        
        # Use current background or get new one
        background_url = st.session_state.current_background
        if not background_url:
            background_url = get_pexels_image(st.session_state.background_category)
            if background_url:
                st.session_state.current_background = background_url
            else:
                st.warning("Could not load background image. Using default background.")
                background_url = "https://images.pexels.com/photos/1939485/pexels-photo-1939485.jpeg"
        
        # Generate message using OpenRouter API
        message = generate_eid_message(
            tone=tone,
            recipient=recipient_name,
            sender=sender_name,
            include_hadith=include_hadith,
            include_emojis=include_emojis
        )
        
        # Clean up the message
        message = message.replace("[No Hadith included, as per your requirements]", "")
        message = message.replace("Note: No signature, HTML tags, or styling code is included in this message.", "")
        message = "\n".join(line for line in message.split("\n") if line.strip())
        
        # Get card styling based on tone
        theme_map = {
            "formal": "Classic",
            "emotional": "Elegant",
            "funny": "Modern",
            "religious": "Classic"
        }
        style = style_card(theme_map.get(tone, "Classic"))
        
        # Create card data structure
        card = {
            'recipient': recipient_name,
            'sender': sender_name,
            'message': message,
            'background_url': background_url,
            'style': style,
            'fonts': fonts
        }
        
        # Add to session state
        st.session_state.cards.insert(0, card)  # Add new card at the beginning
        
        return True
    except Exception as e:
        st.error(f"Error creating card: {str(e)}")
        return False

# Title and description
st.title("🌙 Eid Card Generator")
st.markdown("Create beautiful Eid greeting cards with AI-generated messages and dynamic styling!")

# Two columns layout
col1, col2 = st.columns([2, 1])

with col1:
    # Card creation form
    with st.form("card_form"):
        col_recipient, col_sender = st.columns(2)
        with col_recipient:
            recipient_name = st.text_input("Recipient's Name", placeholder="Enter recipient's name")
        with col_sender:
            sender_name = st.text_input("Your Name", placeholder="Enter your name")
        
        col_tone, col_emoji = st.columns(2)
        with col_tone:
            tone = st.selectbox(
                "Message Tone",
                ["formal", "emotional", "funny", "religious"],
                help="Select the tone for your message"
            )
        
        with col_emoji:
            emoji_count = st.slider(
                "Number of Emojis",
                min_value=0,
                max_value=5,
                value=2,
                help="Select how many emojis to include"
            )
        
        include_emojis = emoji_count > 0
        include_hadith = st.checkbox("Include a Hadith", value=False)
        
        submit_button = st.form_submit_button("Generate Card")
        
        if submit_button and recipient_name and sender_name:
            with st.spinner("Creating your Eid card..."):
                success = create_card(
                    recipient_name,
                    sender_name,
                    tone,
                    include_hadith,
                    include_emojis
                )
                if success:
                    st.success("Card created successfully!")
        elif submit_button:
            if not recipient_name:
                st.error("Please enter the recipient's name")
            if not sender_name:
                st.error("Please enter your name")

with col2:
    # Background control section
    st.subheader("Background Settings")
    
    # Background category selection
    category = st.selectbox(
        "Choose Background Category",
        options=BACKGROUND_CATEGORIES,
        index=BACKGROUND_CATEGORIES.index(st.session_state.background_category),
        key="bg_category"
    )
    
    if category != st.session_state.background_category:
        st.session_state.background_category = category
        refresh_background()
    
    # Refresh button
    if st.button("🔄 Refresh Background"):
        refresh_background()
    
    # Preview current background
    if st.session_state.current_background:
        st.image(st.session_state.current_background, caption="Current Background", use_container_width=True)
    else:
        st.info("Click 'Refresh Background' to load a new background image")

# Display cards
if st.session_state.cards:
    st.markdown("### Your Eid Cards")
    
    for i, card in enumerate(st.session_state.cards):
        cols = st.columns([20, 1])
        
        with cols[0]:
            # Display card
            st.markdown(f"""
            <div class="card" style="background-image: url('{card['background_url']}'); background-size: cover; background-position: center;">
                <div class="card-inner">
                    <h2 class="card-title" style="font-family: {card['fonts']['title']};">Dear {card['recipient']},</h2>
                    <div class="card-content" style="font-family: {card['fonts']['body']};">{card['message']}</div>
                    <div class="urdu-text" style="font-family: {card['fonts']['title']};">عید مبارک</div>
                    <div class="card-signature" style="font-family: {card['fonts']['title']};">With warm wishes,<br>{card['sender']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate PDF for download
            pdf_path = create_pdf_card(card)
            
            # Download button
            with open(pdf_path, "rb") as file:
                btn = st.download_button(
                    label="📥 Download Card as PDF",
                    data=file,
                    file_name=f"eid_card_{i}.pdf",
                    mime="application/pdf"
                )
            
            # Clean up temporary PDF file
            os.remove(pdf_path)
        
        with cols[1]:
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.cards.pop(i)
                st.rerun()
else:
    st.info("Generate your first Eid card using the form above!")

# Add footer at the very end of the file
st.markdown("""
<div class="footer">
    Made with 💗 by <a href="https://github.com/CodeVoyager007" target="_blank">Ayesha Mughal</a>
</div>
""", unsafe_allow_html=True)
