"""
PDF generation utilities for EidiCard.
"""
from fpdf import FPDF
from pathlib import Path
import tempfile
from typing import Optional, Dict
import textwrap
import re
import os
import urllib.request

# Font management
FONTS_DIR = Path(__file__).parent.parent / 'fonts'
FONTS_DIR.mkdir(exist_ok=True)

def get_font_path(font_name: str) -> str:
    """Download and cache Google Fonts."""
    font_urls = {
        'roboto': {
            '': 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf',
            'B': 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf',
            'I': 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Italic.ttf'
        }
    }
    
    font_base = font_name.lower()
    if font_base not in font_urls:
        return ''
    
    # Create font directory if it doesn't exist
    font_dir = FONTS_DIR / font_base
    font_dir.mkdir(exist_ok=True)
    
    def download_font(style: str) -> str:
        font_path = font_dir / f"{font_base}{style}.ttf"
        if not font_path.exists():
            url = font_urls[font_base][style]
            try:
                urllib.request.urlretrieve(url, font_path)
            except Exception as e:
                print(f"Error downloading font: {e}")
                return ''
        return str(font_path)
    
    # Download all font styles
    for style in font_urls[font_base]:
        download_font(style)
    
    return str(font_dir / f"{font_base}.ttf")

def remove_emojis(text):
    """Remove emojis from text while preserving other Unicode characters."""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

class EidCard(FPDF):
    def __init__(self, theme: Dict[str, str]):
        super().__init__(format='A4')  # Use A4 format
        self.theme = theme
        # Set reasonable margins
        self.set_margins(left=20, top=20, right=20)
        self.set_auto_page_break(auto=True, margin=20)
        
        # Use Roboto font for better Unicode support
        font_path = get_font_path('roboto')
        if font_path:
            self.add_font('Roboto', '', font_path, uni=True)
            self.add_font('Roboto', 'B', str(FONTS_DIR / 'roboto' / 'robotoB.ttf'), uni=True)
            self.add_font('Roboto', 'I', str(FONTS_DIR / 'roboto' / 'robotoI.ttf'), uni=True)
            self.default_font = 'Roboto'
        else:
            # Fallback to built-in font if download fails
            self.add_font('Helvetica', '', uni=True)
            self.default_font = 'Helvetica'
    
    def header(self):
        # Add fancy header with Eid theme
        self.set_font(self.default_font, 'B', 24)
        self.set_text_color(
            int(self.theme.get('title_color', '#4a4a4a')[1:3], 16),
            int(self.theme.get('title_color', '#4a4a4a')[3:5], 16),
            int(self.theme.get('title_color', '#4a4a4a')[5:7], 16)
        )
        # Calculate width of text
        title = 'Eid Mubarak'
        title_w = self.get_string_width(title)
        # Center text horizontally
        self.set_x((210 - title_w) / 2)  # 210 is A4 width in mm
        self.cell(title_w, 20, title, 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Add footer
        self.set_y(-15)
        self.set_font(self.default_font, 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Created with EidiCard Generator', 0, 0, 'C')

def create_pdf(
    message: str,
    recipient: str,
    theme: Dict[str, str],
    output_path: Optional[str] = None
) -> str:
    """
    Create a PDF Eid card with the given message and styling.
    
    Args:
        message: The Eid greeting message
        recipient: Name of the recipient
        theme: Dictionary containing theme colors and styles
        output_path: Optional path to save the PDF
    
    Returns:
        Path to the generated PDF file
    """
    # Create PDF instance
    pdf = EidCard(theme)
    pdf.add_page()
    
    # Set colors from theme
    pdf.set_text_color(
        int(theme.get('text_color', '#000000')[1:3], 16),
        int(theme.get('text_color', '#000000')[3:5], 16),
        int(theme.get('text_color', '#000000')[5:7], 16)
    )
    
    # Remove emojis from text for PDF
    clean_message = remove_emojis(message)
    clean_recipient = remove_emojis(recipient)
    
    # Add recipient with proper width calculation
    pdf.set_font(pdf.default_font, 'B', 16)
    recipient_text = f'Dear {clean_recipient},'
    recipient_w = pdf.get_string_width(recipient_text)
    pdf.cell(recipient_w, 10, recipient_text, 0, 1, 'L')
    pdf.ln(10)
    
    # Add message with word wrapping
    pdf.set_font(pdf.default_font, '', 12)
    
    # Calculate available width for text (page width minus margins)
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    # Convert width from mm to characters (approximate)
    chars_per_line = int(effective_width / (pdf.get_string_width('x') * 1.1))
    
    # Word wrap the message
    lines = textwrap.wrap(clean_message, width=chars_per_line)
    for line in lines:
        pdf.multi_cell(effective_width, 8, line, 0, 'L')
        pdf.ln(2)  # Small gap between lines
    
    # Save the PDF
    if not output_path:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            output_path = tmp.name
    
    try:
        pdf.output(output_path)
    except Exception as e:
        # If PDF generation fails, create a simpler version without special characters
        pdf = EidCard(theme)
        pdf.add_page()
        pdf.set_font(pdf.default_font, 'B', 24)
        pdf.cell(0, 20, 'Eid Mubarak', 0, 1, 'C')
        pdf.ln(10)
        pdf.set_font(pdf.default_font, '', 12)
        pdf.multi_cell(0, 10, "May this Eid bring you joy and happiness.\nBest wishes to you and your family.")
        pdf.output(output_path)
    
    return output_path

def create_preview(
    message: str,
    recipient: str,
    theme: Dict[str, str]
) -> str:
    """
    Create an HTML preview of the Eid card.
    
    Args:
        message: The Eid greeting message
        recipient: Name of the recipient
        theme: Dictionary containing theme colors and styles
    
    Returns:
        HTML string for preview
    """
    # Replace newlines with <br> for HTML
    message_html = message.replace('\n', '<br>')
    
    html_template = f"""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <div style="
        max-width: 600px;
        margin: 20px auto;
        padding: 20px;
        border-radius: 10px;
        background-color: {theme.get('bg_color', '#ffffff')};
        color: {theme.get('text_color', '#000000')};
        font-family: 'Roboto', sans-serif;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="
            text-align: center;
            color: {theme.get('title_color', '#4a4a4a')};
            font-family: 'Roboto', sans-serif;
            font-weight: 700;
        ">
            Eid Mubarak
        </h1>
        <h2 style="
            margin-top: 20px;
            font-family: 'Roboto', sans-serif;
            font-weight: 700;
        ">Dear {recipient},</h2>
        <div style="
            white-space: pre-wrap;
            line-height: 1.6;
            margin-top: 20px;
            font-family: 'Roboto', sans-serif;
            font-weight: 400;
        ">
            {message_html}
        </div>
    </div>
    """
    return html_template 