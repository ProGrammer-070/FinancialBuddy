from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import pandas as pd
from datetime import datetime
import io

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Supported currencies and symbols
CURRENCIES = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'INR': '₹',
    'JPY': '¥',
    'CAD': 'C$'
}

def get_currency():
    code = session.get('currency', 'USD')
    symbol = CURRENCIES.get(code, '$')
    return code, symbol

def format_currency(value):
    code, symbol = get_currency()
    try:
        value = float(value)
        return f"{symbol}{value:,.2f}"
    except Exception:
        return f"{symbol}{value}"

@app.context_processor
def inject_currency():
    code, symbol = get_currency()
    return dict(currency_code=code, currency_symbol=symbol, currencies=CURRENCIES, format_currency=format_currency)

@app.route('/set_currency', methods=['POST'])
def set_currency():
    code = request.form.get('currency', 'USD')
    if code in CURRENCIES:
        session['currency'] = code
    return redirect(request.referrer or url_for('home'))

class FinancialForm(FlaskForm):
    monthly_income = FloatField('Monthly Income', validators=[DataRequired()])
    housing_expense = FloatField('Housing Expense', validators=[DataRequired()])
    utilities_expense = FloatField('Utilities Expense', validators=[DataRequired()])
    groceries_expense = FloatField('Groceries Expense', validators=[DataRequired()])
    other_expenses = FloatField('Other Expenses', validators=[DataRequired()])
    short_term_goal = StringField('Short-term Savings Goal', validators=[DataRequired()])
    long_term_goal = StringField('Long-term Savings Goal', validators=[DataRequired()])
    expense_file = FileField('Upload Expense Summary (Optional)', validators=[Optional()])
    submit = SubmitField('Get Financial Advice')

@app.route('/')
def home():
    form = FinancialForm()
    return render_template('index.html', form=form)

@app.route('/reset_profile')
def reset_profile():
    session.pop('financial_data', None)
    return redirect(url_for('home'))

@app.route('/submit', methods=['POST'])
def submit():
    form = FinancialForm()
    if form.validate_on_submit():
        financial_data = {
            'monthly_income': form.monthly_income.data,
            'expenses': {
                'housing': form.housing_expense.data,
                'utilities': form.utilities_expense.data,
                'groceries': form.groceries_expense.data,
                'other': form.other_expenses.data
            },
            'goals': {
                'short_term': form.short_term_goal.data,
                'long_term': form.long_term_goal.data
            }
        }
        
        session['financial_data'] = financial_data

        risk_prompt = f"""Given this profile:
        Monthly Income: {financial_data['monthly_income']}
        Expenses: {financial_data['expenses']}
        Goals: {financial_data['goals']}
        Estimate the user's risk of debt or bankruptcy on a scale of 0-100 and explain why. Give practical steps to reduce risk.
        """
        risk_response = model.generate_content(risk_prompt)
        risk_data = risk_response.text

        prompt = f"""Based on the following financial information, provide personalized financial advice:
        Monthly Income: {financial_data['monthly_income']}
        Expenses:
        - Housing: {financial_data['expenses']['housing']}
        - Utilities: {financial_data['expenses']['utilities']}
        - Groceries: {financial_data['expenses']['groceries']}
        - Other: {financial_data['expenses']['other']}
        
        Goals:
        - Short-term: {financial_data['goals']['short_term']}
        - Long-term: {financial_data['goals']['long_term']}
        
        Please provide:
        1. Budget allocation recommendations (50/30/20 rule)
        2. 3 specific tips to improve financial habits
        3. Goal-specific suggestions
        """
        
        response = model.generate_content(prompt)
        advice = response.text

        total_expenses = sum(financial_data['expenses'].values())
        savings = financial_data['monthly_income'] - total_expenses
        savings_rate = (savings / financial_data['monthly_income'] * 100) if financial_data['monthly_income'] else 0
        expense_ratio = (total_expenses / financial_data['monthly_income'] * 100) if financial_data['monthly_income'] else 0

        return render_template('dashboard.html', 
                             financial_data=financial_data,
                             advice=advice,
                             risk_data=risk_data,
                             savings_rate=savings_rate,
                             expense_ratio=expense_ratio)
    
    return render_template('index.html', form=form)

@app.route('/dashboard')
def dashboard():
    financial_data = session.get('financial_data', {})
    total_expenses = sum(financial_data.get('expenses', {}).values()) if financial_data else 0
    monthly_income = financial_data.get('monthly_income', 0) if financial_data else 0
    savings = monthly_income - total_expenses
    savings_rate = (savings / monthly_income * 100) if monthly_income else 0
    expense_ratio = (total_expenses / monthly_income * 100) if monthly_income else 0

    risk_data = ""
    if financial_data:
        risk_prompt = f"""Given this profile:
        Monthly Income: {monthly_income}
        Expenses: {financial_data.get('expenses', {})}
        Goals: {financial_data.get('goals', {})}
        Estimate the user's risk of debt or bankruptcy on a scale of 0-100 and explain why. Give practical steps to reduce risk.
        """
        risk_response = model.generate_content(risk_prompt)
        risk_data = risk_response.text

    return render_template('dashboard.html',
                           financial_data=financial_data,
                           risk_data=risk_data,
                           savings_rate=savings_rate,
                           expense_ratio=expense_ratio)

@app.route('/download_report')
def download_report():
    financial_data = session.get('financial_data', {})
    if not financial_data:
        return redirect(url_for('dashboard'))

    output = io.StringIO()
    output.write("Field,Value\n")
    output.write(f"Monthly Income,{financial_data.get('monthly_income','')}\n")
    for k, v in financial_data.get('expenses', {}).items():
        output.write(f"{k.capitalize()} Expense,{v}\n")
    for k, v in financial_data.get('goals', {}).items():
        output.write(f"{k.replace('_',' ').capitalize()} Goal,{v}\n")
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='financial_report.csv')

@app.route('/prioritize', methods=['POST'])
def prioritize_purchases():
    purchases = request.json.get('purchases', [])
    
    prompt = f"""Evaluate these planned purchases and categorize them as Essential, Optional, or Delayable:
    {json.dumps(purchases, indent=2)}
    
    For each item, provide:
    1. Category (Essential/Optional/Delayable)
    2. Brief explanation
    """
    
    response = model.generate_content(prompt)
    prioritization = response.text
    
    return jsonify({'prioritization': prioritization})

@app.route('/explain_term', methods=['POST'])
def explain_term():
    term = request.json.get('term', '')
    
    prompt = f"""Explain the financial term '{term}' in simple, beginner-friendly language.
    Include a practical example if relevant."""
    
    response = model.generate_content(prompt)
    explanation = response.text
    
    return jsonify({'explanation': explanation})

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/chat_api', methods=['POST'])
def chat_api():
    user_message = request.json.get('message', '')
    prompt = f"User: {user_message}\nAI (as a helpful financial assistant):"
    response = model.generate_content(prompt)
    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True)