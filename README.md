# Smart Financial Buddy

A personalized AI-powered finance coach web application that helps users make informed financial decisions. Built with Flask and powered by the Gemini API.

## Features

- 📊 Financial Profile Input
- 💡 AI-Powered Financial Advice
- 📈 Visual Progress Tracking
- 🎯 Goal Setting and Monitoring
- 💰 Purchase Prioritization
- 📚 Financial Terms Explanation

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-financial-buddy.git
cd smart-financial-buddy
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
```bash
python app.py
```
3. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Enter your financial information on the homepage
2. View personalized financial advice and visualizations on the dashboard
3. Use the purchase prioritization tool to evaluate planned purchases
4. Look up financial terms in the built-in glossary

## Technologies Used

- Flask: Web framework
- Gemini API: AI-powered financial advice
- Chart.js: Data visualization
- Bootstrap: UI components
- Animate.css: Animations
- Font Awesome: Icons

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Gemini API for providing the AI capabilities
- Bootstrap team for the UI framework
- Chart.js team for the visualization library 