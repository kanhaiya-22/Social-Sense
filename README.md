# Social Media Content Analyzer

A Flask-based web application that extracts text from PDF documents and images, then provides AI-powered sentiment analysis, readability scores, and engagement suggestions to help optimize social media content.

## Features

### 📁 File Processing
- **PDF Text Extraction**: Extract text from PDF documents using PyMuPDF
- **OCR Image Processing**: Extract text from images (PNG, JPG, JPEG) using Tesseract OCR
- **Drag & Drop Upload**: Modern file upload interface with drag-and-drop support
- **File Validation**: Comprehensive validation for file types, sizes, and content

### 🤖 AI-Powered Analysis
- **Sentiment Analysis**: Detect emotional tone using HuggingFace transformers
- **Readability Scoring**: Calculate readability metrics using textstat
- **Engagement Suggestions**: Get AI-powered recommendations using OpenAI GPT-5
- **Real-time Processing**: Live feedback during analysis

### 🎨 Modern Web Interface
- **Responsive Design**: Bootstrap-based dark theme optimized for all devices
- **Interactive Dashboard**: Clean, intuitive interface with visual feedback
- **Results Visualization**: Comprehensive display of analysis results
- **Error Handling**: Graceful error handling with helpful user messages

## Technology Stack

### Backend
- **Flask**: Python web framework
- **PyMuPDF**: PDF text extraction
- **pytesseract + Pillow**: OCR image processing
- **transformers**: HuggingFace sentiment analysis
- **textstat**: Readability metrics
- **OpenAI**: AI-powered engagement suggestions

### Frontend
- **Bootstrap 5**: UI framework with dark theme
- **Vanilla JavaScript**: Interactive file upload
- **Font Awesome**: Icons
- **Chart.js**: Data visualization (ready for future enhancements)

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR installed on system
- OpenAI API key (optional, for engagement suggestions)

### Environment Variables
Create a `.env` file or set these environment variables:

```bash
SESSION_SECRET=your-session-secret-key
OPENAI_API_KEY=your-openai-api-key  # Optional
