# Social Media Content Analyzer

## Overview

This is a Flask-based web application that extracts text from PDF documents and images, then provides AI-powered sentiment analysis, readability scoring, and engagement suggestions to optimize social media content. The application features a modern drag-and-drop interface for file uploads and comprehensive text analysis capabilities using multiple AI services.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework Architecture
- **Flask Application Structure**: Standard Flask app with modular service architecture
- **Service Layer Pattern**: Business logic separated into dedicated service classes (`FileHandler`, `TextExtractor`, `AIAnalyzer`)
- **Template-Based Frontend**: Server-side rendering with Jinja2 templates and Bootstrap 5 dark theme
- **Static Asset Management**: CSS and JavaScript files served through Flask's static file handling

### File Processing Pipeline
- **Multi-Format Support**: Handles PDF documents and images (PNG, JPG, JPEG)
- **PDF Text Extraction**: Uses PyMuPDF (fitz) library for robust PDF text extraction
- **OCR Capabilities**: Tesseract OCR integration with PIL for image text extraction
- **File Validation**: Comprehensive validation for file types, sizes (16MB limit), and content integrity
- **Secure File Handling**: Uses secure_filename and UUID-based file naming for security

### AI Analysis Engine
- **Sentiment Analysis**: HuggingFace transformers with fallback models (primary: cardiffnlp/twitter-roberta-base-sentiment-latest, fallback: distilbert-base-uncased-finetuned-sst-2-english)
- **Readability Metrics**: textstat library for calculating readability scores and text complexity
- **Engagement Suggestions**: OpenAI GPT integration for AI-powered content optimization recommendations
- **Error Resilience**: Graceful fallback mechanisms when AI services are unavailable

### Frontend Architecture
- **Progressive Enhancement**: JavaScript enhancement of server-rendered HTML
- **Drag-and-Drop Upload**: Modern file upload interface with visual feedback
- **Responsive Design**: Bootstrap 5 grid system with mobile-first approach
- **Real-time Feedback**: Interactive processing status and error handling
- **Dark Theme**: Consistent dark theme implementation across all components

### Configuration Management
- **Environment-Based Config**: Uses environment variables for sensitive configuration (OpenAI API key, session secrets)
- **Development vs Production**: Separate configuration handling with debug mode support
- **File Upload Limits**: Configurable file size limits and allowed extensions

## External Dependencies

### AI and Machine Learning Services
- **HuggingFace Transformers**: Sentiment analysis models with automatic model downloading
- **OpenAI API**: GPT-based engagement suggestions (optional, graceful degradation)
- **Tesseract OCR**: System-level OCR engine for image text extraction

### Python Libraries
- **Flask**: Core web framework with Werkzeug utilities
- **PyMuPDF (fitz)**: PDF text extraction and processing
- **pytesseract + Pillow (PIL)**: OCR and image processing
- **textstat**: Readability and text complexity analysis
- **transformers**: HuggingFace model integration

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme variant
- **Font Awesome**: Icon library for UI elements
- **Chart.js**: Data visualization library (prepared for future enhancements)
- **Vanilla JavaScript**: No additional frontend frameworks required

### Infrastructure
- **File System Storage**: Local file storage for uploaded documents (uploads directory)
- **Session Management**: Flask sessions with configurable secret keys
- **Logging**: Python logging framework for debugging and monitoring
- **WSGI Deployment**: ProxyFix middleware for production deployment compatibility