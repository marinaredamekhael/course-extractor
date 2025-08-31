# Course Extractor

A powerful web application that automatically extracts course information from educational websites. Built with Flask (Python) and modern web technologies, this tool helps educators, students, and researchers gather structured course data efficiently.

## 🌟 Features

### Core Functionality
- **AI-Powered Extraction**: Advanced algorithms automatically detect and extract course information
- **Multi-URL Support**: Process multiple educational websites simultaneously
- **Comprehensive Data Extraction**: Extract all available course details including:
  - Course Name
  - Institute Name
  - Location
  - Format (Online, On-campus, Hybrid, etc.)
  - Faculty/Instructors
  - Language of Instruction
  - Dates (Start/End)
  - Duration
  - Suitable For (target audience, prerequisites)
  - Fees/Cost
  - Availability/Enrollment Status

### User Experience
- **Modern Web Interface**: Responsive design that works on all devices
- **Real-time Processing**: Live feedback during extraction process
- **Smart Validation**: URL validation and error handling
- **Processing History**: Track and reprocess previous extractions
- **Export Options**: Download results as CSV or Excel files

### Technical Features
- **Privacy-First**: Only extracts publicly available information
- **Error Handling**: Graceful handling of invalid URLs and unsupported sites
- **Performance Optimized**: Efficient scraping with rate limiting
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd course-extractor
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

### 🚀 Deploy to Production (Make Public)

Want to make your Course Extractor publicly accessible? Follow our deployment guide:

**Quick Deploy Options:**
- **[Heroku (Recommended)](https://devcenter.heroku.com/articles/getting-started-with-python)** - Free tier available
- **[Railway](https://railway.app)** - Simple deployment
- **[Render](https://render.com)** - Easy setup

**Step-by-step guide:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

**Automated deployment:** Use our deployment scripts:
- Windows: `deploy.bat`
- PowerShell: `deploy.ps1`

## 📖 Usage Guide

### Basic Usage

1. **Enter Website URL**
   - Navigate to the home page
   - Enter the URL of an educational institution's website
   - Click "Extract Courses"

2. **View Results**
   - Results are displayed in a structured table
   - Summary statistics show key metrics
   - Each course row contains all extracted information

3. **Export Data**
   - Use CSV export for spreadsheet applications
   - Use Excel export for detailed analysis
   - Files include timestamps for organization

### Advanced Features

#### Multiple URLs
- Click "Add Multiple URLs" to process several websites at once
- Each URL is processed independently
- Results are combined for comprehensive analysis

#### Processing History
- View previous extraction attempts
- Reprocess URLs with updated data
- Track success rates and course counts

#### Data Filtering
- Filter by institute, location, or format
- Sort results by any column
- Search within extracted data

### Best Practices

#### For Better Results
- Use the main course listing page of the educational institution
- Ensure the website is publicly accessible
- Try department-specific course pages for specialized programs
- Some websites may require multiple attempts for optimal extraction

#### URL Examples
- **University Courses**: `https://university.edu/courses`
- **Department Pages**: `https://university.edu/computer-science/courses`
- **Program Lists**: `https://college.edu/academic-programs`

## 🏗️ Architecture

### Backend (Flask)
- **CourseExtractor Class**: Core extraction logic
- **Web Scraping**: BeautifulSoup and Selenium integration
- **API Endpoints**: RESTful API for frontend communication
- **Data Processing**: Pandas for data manipulation and export

### Frontend (HTML/CSS/JavaScript)
- **Responsive Design**: Bootstrap 5 framework
- **Interactive UI**: Modern JavaScript with ES6+ features
- **Real-time Updates**: Asynchronous data processing
- **Local Storage**: Persistent user preferences and history

### Data Flow
1. User submits URL(s) via web interface
2. Backend processes URLs with web scraping
3. Extracted data is structured and validated
4. Results are returned to frontend
5. Data is displayed in table format
6. Export options generate downloadable files

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
FLASK_ENV=development
FLASK_DEBUG=True
CHROME_DRIVER_PATH=/path/to/chromedriver
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
```

### Customization Options
- **Scraping Patterns**: Modify regex patterns in `CourseExtractor` class
- **Export Formats**: Add new export formats in export functions
- **UI Themes**: Customize CSS variables in `static/css/style.css`
- **API Rate Limiting**: Adjust request limits and delays

## 📊 Data Structure

### Course Object
```json
{
  "course_name": "Introduction to Computer Science",
  "institute_name": "University of Technology",
  "location": "New York, NY",
  "format": "On-campus",
  "faculty": "Dr. John Smith",
  "language": "English",
  "dates": "2024-01-15 - 2024-05-15",
  "duration": "16 weeks",
  "suitable_for": "Undergraduate students",
  "fees": "$3,500",
  "availability": "Open for enrollment"
}
```

### API Response
```json
{
  "success": true,
  "results": [
    {
      "success": true,
      "url": "https://example.edu/courses",
      "courses_found": 25,
      "courses": [...]
    }
  ],
  "total_courses": 25
}
```

## 🛠️ Development

### Project Structure
```
course-extractor/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   └── index.html       # Main page template
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   │   └── style.css   # Main CSS file
│   └── js/             # JavaScript files
│       └── app.js      # Main application logic
├── README.md            # This file
└── .gitignore          # Git ignore rules
```

### Adding New Features

#### New Extraction Fields
1. Add field to `_extract_single_course_from_container` method
2. Update HTML table headers
3. Modify JavaScript display logic
4. Update export functions

#### New Export Formats
1. Create new route in Flask app
2. Implement export logic
3. Add frontend button
4. Update JavaScript export function

#### Custom Scraping Rules
1. Modify regex patterns in extraction methods
2. Add new CSS selectors for specific websites
3. Implement site-specific extraction logic
4. Test with target websites

### Testing
```bash
# Run basic tests
python -m pytest tests/

# Test specific functionality
python -m pytest tests/test_extraction.py

# Run with coverage
python -m pytest --cov=app tests/
```

## 🚨 Troubleshooting

### Common Issues

#### No Courses Found
- Check if the website is publicly accessible
- Verify the URL contains course information
- Try different pages within the same website
- Check browser console for JavaScript errors

#### Extraction Errors
- Ensure all dependencies are installed
- Check Chrome browser installation
- Verify internet connection
- Review Flask application logs

#### Performance Issues
- Reduce number of concurrent URLs
- Increase request timeout values
- Check website response times
- Monitor system resources

### Debug Mode
Enable debug mode for detailed error information:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Logging
Application logs are available in the console. For production, configure proper logging:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 📈 Performance Optimization

### Scraping Efficiency
- **Parallel Processing**: Process multiple URLs concurrently
- **Caching**: Cache previously scraped results
- **Rate Limiting**: Respect website robots.txt and rate limits
- **Connection Pooling**: Reuse HTTP connections

### Memory Management
- **Streaming**: Process large datasets in chunks
- **Cleanup**: Remove temporary files after export
- **Garbage Collection**: Optimize Python memory usage

### Database Integration
For production use, consider adding a database:

```python
# SQLite example
import sqlite3
conn = sqlite3.connect('courses.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        course_name TEXT,
        institute_name TEXT,
        extracted_at TIMESTAMP
    )
''')
```

## 🔒 Security Considerations

### Data Privacy
- Only extract publicly available information
- Respect website terms of service
- Implement rate limiting to avoid overwhelming servers
- Store sensitive data securely

### Input Validation
- Validate all user inputs
- Sanitize URLs before processing
- Implement CSRF protection
- Use parameterized queries

### Access Control
- Implement user authentication if needed
- Rate limit API endpoints
- Monitor for abuse patterns
- Log access attempts

## 🤝 Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Follow PEP 8 Python guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include type hints where appropriate

### Testing Requirements
- Maintain test coverage above 80%
- Test edge cases and error conditions
- Include integration tests for API endpoints
- Test with various website structures

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BeautifulSoup**: HTML parsing and navigation
- **Selenium**: Dynamic content extraction
- **Flask**: Web framework
- **Bootstrap**: UI components and responsive design
- **Font Awesome**: Icons and visual elements

## 🚀 Deployment

### Making Your App Public

This Course Extractor can be easily deployed to make it publicly accessible to anyone on the internet.

#### Quick Deploy Options

1. **Heroku (Recommended)**
   - Free tier available
   - Automatic deployment from GitHub
   - Easy scaling options

2. **Railway**
   - Simple deployment process
   - Good for small to medium apps
   - Automatic HTTPS

3. **Render**
   - Free tier available
   - Easy GitHub integration
   - Good documentation

#### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Platform**
   - Follow platform-specific instructions
   - Connect your GitHub repository
   - Deploy automatically

3. **Get Public URL**
   - Your app will have a public URL
   - Share with others to use your Course Extractor
   - Monitor usage and performance

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## 📞 Support

### Getting Help
- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check this README and inline code comments
- **Community**: Join discussions in project forums

### Contact Information
- **Project Maintainer**: [Your Name]
- **Email**: [your.email@example.com]
- **GitHub**: [github.com/yourusername]

---

**Note**: This tool is designed for educational and research purposes. Always respect website terms of service and implement appropriate rate limiting when scraping websites.
