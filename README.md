# 🌙 Eid Card Generator

A beautiful and modern web application that helps you create personalized Eid greeting cards with AI-generated messages, dynamic backgrounds, and elegant designs.

## ✨ Features

- 🤖 AI-powered message generation with customizable tones:
  - Formal
  - Emotional
  - Funny
  - Religious
- 🖼️ Dynamic background images from Pexels API
- 🎨 Beautiful card themes:
  - Classic
  - Modern
  - Elegant
- 🌟 Additional features:
  - Support for Urdu text (عید مبارک)
  - Optional Hadith inclusion
  - Customizable emoji count
  - Google Fonts integration
  - PDF export functionality
  - Responsive and modern UI

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/CodeVoyager007/eid-card-generator.git
   cd eid-card-generator
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix or MacOS:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```env
     OPENROUTER_API_KEY=your_openrouter_api_key
     PEXELS_API_KEY=your_pexels_api_key
     ```

## 🔑 API Keys

### OpenRouter API
1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Create a new API key
4. Copy the key to your `.env` file

### Pexels API
1. Visit [Pexels API](https://www.pexels.com/api/)
2. Create a developer account
3. Generate an API key
4. Copy the key to your `.env` file

## 🎮 Usage

1. Start the application:
   ```bash
   streamlit run main.py
   ```

2. Open your browser and navigate to the displayed URL (usually http://localhost:8501)

3. Create your card:
   - Enter recipient's name
   - Enter your name
   - Choose message tone
   - Adjust emoji count
   - Toggle Hadith inclusion
   - Select background category
   - Click "Generate Card"

4. Customize your card:
   - Refresh background if desired
   - Preview the card
   - Download as PDF

## 📁 Project Structure

```
eid-card/
├── main.py           # Main Streamlit application
├── agents.py         # AI message generation
├── tools.py          # Utility functions
├── utils/
│   ├── __init__.py  # Image handling
│   ├── font_utils.py # Font management
│   └── pdf_generator.py # PDF generation
├── fonts/            # Font files
├── requirements.txt  # Dependencies
└── README.md        # Documentation
```

## 🛠️ Technologies Used

- **Streamlit**: Web interface
- **OpenRouter/Mistral**: AI message generation
- **Pexels API**: Background images
- **FPDF2**: PDF generation
- **Google Fonts**: Typography
- **Python 3.8+**: Core language

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 👩‍💻 Author

**Ayesha Mughal**
- GitHub: [@CodeVoyager007](https://github.com/CodeVoyager007)

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/) for AI capabilities
- [Pexels](https://www.pexels.com/) for beautiful images
- [Streamlit](https://streamlit.io/) for the web framework


