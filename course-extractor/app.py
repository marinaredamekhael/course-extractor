from flask import Flask, request, jsonify, send_file, render_template, send_from_directory, make_response
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
import csv
from openpyxl import Workbook
from datetime import datetime
import os
import time
import logging
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

# Configure Flask
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseExtractor:
    def __init__(self):
        self.session = requests.Session()
        
        # Enhanced headers to appear more like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # List of user agents to rotate through
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        # Safety limit for following course links from a listing page
        self.max_course_pages = int(os.getenv('MAX_COURSE_PAGES', '100'))
    
    def _rotate_user_agent(self):
        """Rotate to a different user agent"""
        import random
        new_agent = random.choice(self.user_agents)
        self.session.headers.update({'User-Agent': new_agent})
        return new_agent
    
    def _add_random_delay(self):
        """Add a random delay to appear more human-like"""
        import random
        import time
        delay = random.uniform(1, 3)  # Random delay between 1-3 seconds
        time.sleep(delay)
        
    def extract_course_info(self, url):
        """Extract course information from a given URL"""
        try:
            logger.info(f"Extracting course info from: {url}")
            
            # Try Stanford with a different approach - use a more common user agent
            if 'stanford' in url.lower():
                self.session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })
                logger.info("Using Stanford-specific headers")
            
            # Temporarily disable delays and user agent rotation for debugging
            # self._rotate_user_agent()
            # self._add_random_delay()
            
            # Try with requests first
            response = self.session.get(url, timeout=15)  # Increased timeout
            
            # Log response details for debugging
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response content length: {len(response.content)}")
            
            # Check if we got blocked
            if response.status_code == 403:
                logger.warning(f"Got 403 Forbidden for {url}, trying with different approach")
                # Try with a different user agent
                self._rotate_user_agent()
                self._add_random_delay()
                response = self.session.get(url, timeout=15)
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            courses = self._extract_courses_from_page(soup, url)
            
            # If no courses found, try to find course listing pages
            if not courses:
                course_links = self._find_course_links(soup, url)
                courses = []
                for link in course_links[:self.max_course_pages]:  # Use configurable limit
                    try:
                        course_info = self._extract_single_course(link, url)
                        if course_info:
                            courses.append(course_info)
                        # Add delay between requests
                        # self._add_random_delay()
                    except Exception as e:
                        logger.warning(f"Failed to extract from {link}: {e}")
                        continue
            
            return {
                'success': True,
                'url': url,
                'courses_found': len(courses),
                'courses': courses
            }
            
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return {
                'success': False,
                'url': url,
                'error': f"Failed to fetch URL: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return {
                'success': False,
                'url': url,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def _extract_courses_from_page(self, soup, base_url):
        """Extract multiple courses from a page"""
        courses = []
        
        # First, try to extract from table-based course listings (like Stanford Continuing Studies)
        table_courses = self._extract_courses_from_table(soup, base_url)
        if table_courses:
            courses.extend(table_courses)
        
        # Look for course containers in divs/articles
        course_containers = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'course|class|program', re.I))
        
        if not course_containers:
            # Try alternative selectors
            course_containers = soup.find_all(['div', 'article'], id=re.compile(r'course|class|program', re.I))
        
        for container in course_containers:
            course_info = self._extract_single_course_from_container(container, base_url)
            if course_info:
                try:
                    page_root = soup
                    course_info = self._apply_fallbacks(course_info, page_root)
                except Exception:
                    pass
                courses.append(course_info)
        
        return courses
    
    def _extract_courses_from_table(self, soup, base_url):
        """Extract courses from table-based course listings"""
        courses = []
        
        # Look for tables that might contain course information
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        # For debugging: print the first 1000 chars of page content
        page_content = soup.get_text()[:1000]
        logger.info(f"Page content preview: {page_content}")
        
        # Also look for other table-like structures
        div_tables = soup.find_all('div', class_=re.compile(r'table|grid|list', re.I))
        logger.info(f"Found {len(div_tables)} div-based table structures")
        
        # Look for any divs that might contain course listings (Stanford specific)
        if 'stanford' in base_url.lower():
            # Look for divs containing course-like content
            course_divs = soup.find_all('div', string=re.compile(r'ARCH|ARTH|CW|TECH|WELL|FICT|SCI', re.I))
            logger.info(f"Found {len(course_divs)} Stanford course divs")
            
            # Also look for any div with course-related text
            course_containers = soup.find_all('div', string=re.compile(r'course|class|program', re.I))
            logger.info(f"Found {len(course_containers)} course containers")
        
        for i, table in enumerate(tables):
            # Check if this table looks like a course catalog
            table_text = table.get_text().lower()
            logger.info(f"Table {i}: Text preview: {table_text[:200]}...")
            logger.info(f"Table {i}: HTML structure: {str(table)[:500]}...")
            
            # More flexible table detection for Stanford Continuing Studies
            is_course_table = (
                any(keyword in table_text for keyword in ['course', 'code', 'title', 'format', 'status', 'quarter']) or
                any(keyword in table_text for keyword in ['arch', 'arth', 'cw', 'tech', 'well', 'fict', 'sci']) or  # Stanford course codes
                'fa' in table_text or 'wi' in table_text or 'sp' in table_text or 'su' in table_text or  # Quarter abbreviations
                any(keyword in table_text for keyword in ['online', 'on-campus', 'off-campus']) or  # Format indicators
                any(keyword in table_text for keyword in ['open', 'closed', 'wait list']) or  # Status indicators
                len(table_text) > 100  # Large tables are more likely to be course catalogs
            )
            
            logger.info(f"Table {i} course detection result: {is_course_table}")
            
            if is_course_table:
                logger.info(f"Table {i} identified as course catalog")
                rows = table.find_all('tr')
                logger.info(f"Table {i} has {len(rows)} rows")
                
                for row_idx, row in enumerate(rows[1:], 1):  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    logger.info(f"Row {row_idx} has {len(cells)} cells")
                    if len(cells) >= 3:  # Need at least course code, title, and some other info
                        course_info = self._extract_course_from_table_row(cells, base_url, table_text)
                        if course_info:
                            logger.info(f"Successfully extracted course from row {row_idx}: {course_info['course_name']}")
                            # Apply page-level metadata to this course
                            course_info = self._apply_page_metadata(course_info, soup, base_url)
                            courses.append(course_info)
                        else:
                            logger.info(f"No course info extracted from row {row_idx}")
            else:
                logger.info(f"Table {i} not identified as course catalog")
        
        # Also try to extract from div-based table structures
        for i, div_table in enumerate(div_tables):
            div_text = div_table.get_text().lower()
            logger.info(f"Div table {i}: Text preview: {div_text[:200]}...")
            
            # Check if this div contains course information
            if any(keyword in div_text for keyword in ['course', 'code', 'title', 'format', 'status', 'quarter']):
                logger.info(f"Div table {i} identified as course catalog")
                # Try to extract courses from this div structure
                div_courses = self._extract_courses_from_div_structure(div_table, base_url)
                if div_courses:
                    courses.extend(div_courses)
        
        logger.info(f"Total courses extracted from tables: {len(courses)}")
        return courses
    
    def _extract_courses_from_div_structure(self, div_element, base_url):
        """Extract courses from div-based table structures"""
        courses = []
        
        try:
            # Look for course items in div structures
            course_items = div_element.find_all(['div', 'article'], class_=re.compile(r'course|item|row', re.I))
            logger.info(f"Found {len(course_items)} course items in div structure")
            
            for item in course_items:
                course_info = self._extract_course_from_div_item(item, base_url)
                if course_info:
                    courses.append(course_info)
                    
        except Exception as e:
            logger.warning(f"Error extracting from div structure: {e}")
        
        return courses
    
    def _extract_course_from_div_item(self, div_item, base_url):
        """Extract course information from a div-based course item"""
        try:
            course_info = {
                'course_name': 'Not Available',
                'institute_name': 'Not Available',
                'location': 'Not Available',
                'format': 'Not Available',
                'faculty': 'Not Available',
                'language': 'Not Available',
                'dates': 'Not Available',
                'duration': 'Not Available',
                'suitable_for': 'Not Available',
                'fees': 'Not Available',
                'availability': 'Not Available'
            }
            
            # Extract course name from various possible selectors
            name_selectors = ['h1', 'h2', 'h3', 'h4', '.course-title', '.course-name', '.title', '.name']
            for selector in name_selectors:
                name_elem = div_item.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    course_info['course_name'] = name_elem.get_text(strip=True)
                    break
            
            # Extract other information from the div item
            item_text = div_item.get_text()
            
            # Look for format information
            if 'online' in item_text.lower():
                course_info['format'] = 'Online'
            elif 'on-campus' in item_text.lower():
                course_info['format'] = 'On-campus'
            elif 'off-campus' in item_text.lower():
                course_info['format'] = 'Off-campus'
            
            # Look for status information
            if 'open' in item_text.lower():
                course_info['availability'] = 'Open'
            elif 'closed' in item_text.lower():
                course_info['availability'] = 'Closed'
            elif 'wait list' in item_text.lower():
                course_info['availability'] = 'Wait List'
            
            # Only return if we have at least a course name
            if course_info['course_name'] != 'Not Available':
                return course_info
                
        except Exception as e:
            logger.warning(f"Error extracting course from div item: {e}")
        
        return None
    
    def _extract_course_from_table_row(self, cells, base_url, table_context):
        """Extract course information from a table row"""
        try:
            course_info = {
                'course_name': 'Not Available',
                'institute_name': 'Not Available',
                'location': 'Not Available',
                'format': 'Not Available',
                'faculty': 'Not Available',
                'language': 'Not Available',
                'dates': 'Not Available',
                'duration': 'Not Available',
                'suitable_for': 'Not Available',
                'fees': 'Not Available',
                'availability': 'Not Available'
            }
            
            # Detect table type based on context and cell content
            is_stanford_format = (
                'stanford' in table_context.lower() or 
                'quarter' in table_context.lower() or
                any(re.match(r'^[A-Z]{2,5}\s*\d+', cell.get_text(strip=True)) for cell in cells[:2] if len(cells) > 1) or  # Course codes like ARCH 03
                any(cell.get_text(strip=True) in ['FA', 'WI', 'SP', 'SU'] for cell in cells if len(cells) > 2) or  # Quarter abbreviations
                any('online' in cell.get_text(strip=True).lower() or 'on-campus' in cell.get_text(strip=True).lower() for cell in cells if len(cells) > 3)
            )
            
            # Additional check: if first cell is just a number, it's likely LBS format (row numbers)
            if len(cells) > 0 and cells[0].get_text(strip=True).isdigit():
                is_stanford_format = False
            
            if is_stanford_format:
                # Stanford Continuing Studies format: Code | Course Title | Qtr | Days | Format | Status
                logger.debug("Using Stanford format extraction")
                course_info = self._extract_stanford_format(cells, course_info)
            else:
                # LBS Centre Kerala format: # | Course name | Duration | Course Fee | Close date | Details | Option
                logger.debug("Using LBS format extraction")
                course_info = self._extract_lbs_format(cells, course_info)
            
            # Only return if we have at least a course name
            if course_info['course_name'] != 'Not Available':
                return course_info
                
        except Exception as e:
            logger.warning(f"Error extracting course from table row: {e}")
        
        return None
    
    def _extract_stanford_format(self, cells, course_info):
        """Extract course information from Stanford Continuing Studies table format"""
        try:
            # Stanford format: Code | Course Title | Qtr | Days | Format | Status
            logger.debug(f"Stanford format: Processing {len(cells)} cells")
            
            if len(cells) >= 4:  # Need at least 4 columns for meaningful extraction
                # Extract course code from first column
                course_code = ""
                course_title = ""
                
                if len(cells) > 0:
                    # First cell might contain both code and title, or just code
                    first_cell_text = cells[0].get_text(strip=True)
                    logger.debug(f"First cell: '{first_cell_text}'")
                    
                    # Check if first cell looks like a course code
                    if re.match(r'^[A-Z]{2,5}\s*\d+', first_cell_text):
                        course_code = first_cell_text
                        
                        # Extract course title from second column
                        if len(cells) > 1:
                            course_title = cells[1].get_text(strip=True)
                            logger.debug(f"Second cell (title): '{course_title}'")
                    else:
                        # First cell might contain the title
                        course_title = first_cell_text
                
                # Set the course name
                if course_code and course_title:
                    course_info['course_name'] = f"{course_code} - {course_title}"
                elif course_title:
                    course_info['course_name'] = course_title
                elif course_code:
                    course_info['course_name'] = course_code
                
                # Extract quarter from appropriate column (usually 3rd for Stanford)
                if len(cells) > 2:
                    quarter = cells[2].get_text(strip=True)
                    logger.debug(f"Quarter cell: '{quarter}'")
                    if quarter and quarter not in ['Qtr', ''] and re.match(r'^(FA|WI|SP|SU)$', quarter):
                        course_info['dates'] = quarter
                
                # Extract days from appropriate column (usually 4th for Stanford)
                if len(cells) > 3:
                    days = cells[3].get_text(strip=True)
                    logger.debug(f"Days cell: '{days}'")
                    if days and days not in ['Days', '']:
                        if course_info['dates'] != 'Not Available':
                            course_info['dates'] += f" ({days})"
                        else:
                            course_info['dates'] = days
                
                # Extract format from appropriate column (usually 5th for Stanford)
                if len(cells) > 4:
                    format_text = cells[4].get_text(strip=True)
                    logger.debug(f"Format cell: '{format_text}'")
                    if format_text and format_text not in ['Format', '']:
                        course_info['format'] = format_text
                
                # Extract status from last column (usually 6th for Stanford)
                if len(cells) > 5:
                    status = cells[5].get_text(strip=True)
                    logger.debug(f"Status cell: '{status}'")
                    if status and status not in ['Status', '']:
                        course_info['availability'] = status
                        
                logger.debug(f"Extracted Stanford course: {course_info['course_name']}")
                        
        except Exception as e:
            logger.warning(f"Error extracting Stanford format: {e}")
        
        return course_info
    
    def _extract_lbs_format(self, cells, course_info):
        """Extract course information from LBS Centre Kerala table format"""
        try:
            # LBS Centre format: # | Course name | Duration | Course Fee | Close date | Details | Option
            if len(cells) >= 5:
                # Extract course name from second column (index 1)
                course_name = cells[1].get_text(strip=True)
                if course_name and course_name not in ['Course name', '']:
                    course_info['course_name'] = course_name
                
                # Extract duration from third column (index 2)
                if len(cells) > 2:
                    duration = cells[2].get_text(strip=True)
                    if duration and duration not in ['Duration', '']:
                        course_info['duration'] = duration
                
                # Extract fees from fourth column (index 3)
                if len(cells) > 3:
                    fees = cells[3].get_text(strip=True)
                    if fees and fees not in ['Course Fee', '']:
                        course_info['fees'] = fees
                
                # Extract close date from fifth column (index 4)
                if len(cells) > 4:
                    close_date = cells[4].get_text(strip=True)
                    if close_date and close_date not in ['Close date', '']:
                        course_info['dates'] = close_date
                
                # Extract format from the last column (usually contains "Apply Online")
                if len(cells) > 5:
                    format_text = cells[-1].get_text(strip=True)
                    if format_text and 'Apply Online' in format_text:
                        course_info['format'] = 'Online Application Available'
                        
        except Exception as e:
            logger.warning(f"Error extracting LBS format: {e}")
        
        return course_info
    
    def _extract_single_course_from_container(self, container, base_url):
        """Extract information from a single course container"""
        try:
            course_info = {
                'course_name': 'Not Available',
                'institute_name': 'Not Available',
                'location': 'Not Available',
                'format': 'Not Available',
                'faculty': 'Not Available',
                'language': 'Not Available',
                'dates': 'Not Available',
                'duration': 'Not Available',
                'suitable_for': 'Not Available',
                'fees': 'Not Available',
                'availability': 'Not Available'
            }
            
            # Extract course name
            name_selectors = ['h1', 'h2', 'h3', '.course-title', '.course-name', '.title']
            for selector in name_selectors:
                name_elem = container.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    course_info['course_name'] = name_elem.get_text(strip=True)
                    break
            
            # Extract institute name (try to get from page title or breadcrumbs)
            institute_selectors = ['.institute', '.university', '.college', '.school', '.breadcrumb']
            for selector in institute_selectors:
                institute_elem = container.select_one(selector)
                if institute_elem and institute_elem.get_text(strip=True):
                    course_info['institute_name'] = institute_elem.get_text(strip=True)
                    break
            
            # Fallback: try to extract from page content patterns
            if course_info['institute_name'] == 'Not Available':
                # Look for common university patterns in the text
                institute_patterns = [
                    r'(Stanford\s+University)',
                    r'(INSEAD)',
                    r'(HEC\s+Paris)',
                    r'(IMD\s+Business\s+School)',
                    r'(LBS\s+Centre)',
                    r'([A-Z][a-z]+\s+University)',
                    r'([A-Z][a-z]+\s+College)',
                    r'([A-Z][a-z]+\s+School)',
                    r'(INSEAD\s+Business\s+School)',
                    r'(INSEAD\s+Executive\s+Education)',
                    r'(HEC\s+Paris\s+Business\s+School)',
                    r'(IMD\s+Business\s+School)',
                    r'(LBS\s+Centre,\s*Kerala)',
                    r'(LBS\s+Centre\s+for\s+Science\s+&\s+Technology)',
                    r'(LBS\s+Centre\s+for\s+Science\s+and\s+Technology)'
                ]
                
                for pattern in institute_patterns:
                    match = re.search(pattern, container_text, re.I)
                    if match:
                        course_info['institute_name'] = match.group(1).strip()
                        break
            
            # Extract location
            location_patterns = [
                r'Location[:\s]+([^,\n]+)',
                r'Address[:\s]+([^,\n]+)',
                r'([A-Z][a-z]+,\s*[A-Z]{2})',
                r'([A-Z][a-z]+,\s*[A-Z][a-z]+)'
            ]
            
            container_text = container.get_text()
            for pattern in location_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['location'] = match.group(1).strip()
                    break
            
            # Fallback: try to extract from common university locations
            if course_info['location'] == 'Not Available':
                location_fallbacks = [
                    r'(Stanford,\s*CA)',
                    r'(Stanford,\s*California)',
                    r'(Fontainebleau,\s*France)',
                    r'(Singapore)',
                    r'(Abu\s+Dhabi)',
                    r'(Lausanne,\s*Switzerland)',
                    r'(Kerala,\s*India)',
                    r'(Paris,\s*France)',
                    r'(INSEAD\s+Fontainebleau)',
                    r'(INSEAD\s+Singapore)',
                    r'(INSEAD\s+Abu\s+Dhabi)',
                    r'(HEC\s+Paris,\s*France)',
                    r'(IMD\s+Lausanne)',
                    r'(LBS\s+Centre,\s*Kerala)',
                    r'(Thiruvananthapuram,\s*Kerala)',
                    r'(Kerala,\s*India)',
                    r'(India)'
                ]
                
                for pattern in location_fallbacks:
                    match = re.search(pattern, container_text, re.I)
                    if match:
                        course_info['location'] = match.group(1).strip()
                        break
            
            # Extract format
            format_patterns = [
                r'(Online|On-campus|Hybrid|Distance|Remote)',
                r'(Full-time|Part-time)',
                r'(In-person|Virtual|Blended)'
            ]
            
            for pattern in format_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['format'] = match.group(1)
                    break
            
            # Extract faculty/instructors
            faculty_selectors = ['.faculty', '.instructor', '.teacher', '.professor']
            for selector in faculty_selectors:
                faculty_elem = container.select_one(selector)
                if faculty_elem and faculty_elem.get_text(strip=True):
                    course_info['faculty'] = faculty_elem.get_text(strip=True)
                    break
            
            # Extract language
            language_patterns = [
                r'Language[:\s]+([^,\n]+)',
                r'Taught in[:\s]+([^,\n]+)',
                r'([A-Z][a-z]+)\s+language'
            ]
            
            for pattern in language_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['language'] = match.group(1).strip()
                    break
            
            # Fallback for language: try html lang attribute
            if course_info['language'] == 'Not Available':
                html_lang = container.find('html')
                if html_lang and html_lang.get('lang'):
                    course_info['language'] = html_lang['lang'].split('-')[0].strip().capitalize()
            
            # Additional fallback: most university courses are in English
            if course_info['language'] == 'Not Available':
                # Check if page content suggests English language
                english_indicators = ['english', 'en', 'en-us', 'en-gb']
                if any(indicator in container_text.lower() for indicator in english_indicators):
                    course_info['language'] = 'English'
                else:
                    # Default to English for most university websites
                    course_info['language'] = 'English'
            
            # Extract dates
            date_patterns = [
                r'Start[:\s]+([^,\n]+)',
                r'End[:\s]+([^,\n]+)',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\w+\s+\d{1,2},?\s+\d{4})'
            ]
            
            dates = []
            for pattern in date_patterns:
                matches = re.findall(pattern, container_text, re.I)
                dates.extend(matches)
            
            if dates:
                course_info['dates'] = ' - '.join(dates[:2])  # Start and end dates
            
            # Extract duration
            duration_patterns = [
                r'Duration[:\s]+([^,\n]+)',
                r'(\d+\s+(weeks?|months?|years?|days?))',
                r'(\d+-\d+\s+(weeks?|months?|years?))'
            ]
            
            for pattern in duration_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['duration'] = match.group(1).strip()
                    break
            
            # Extract suitable for/prerequisites
            suitable_patterns = [
                r'Suitable for[:\s]+([^,\n]+)',
                r'Prerequisites[:\s]+([^,\n]+)',
                r'Target audience[:\s]+([^,\n]+)',
                r'Requirements[:\s]+([^,\n]+)'
            ]
            
            for pattern in suitable_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['suitable_for'] = match.group(1).strip()
                    break
            
            # Extract fees
            fee_patterns = [
                r'Fee[:\s]+([^,\n]+)',
                r'Cost[:\s]+([^,\n]+)',
                r'Price[:\s]+([^,\n]+)',
                r'(\$[\d,]+)',
                r'(\d+[\d,]*\s*(USD|EUR|GBP|CAD))'
            ]
            
            for pattern in fee_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['fees'] = match.group(1).strip()
                    break
            
            # Extract availability
            availability_patterns = [
                r'Enrollment[:\s]+([^,\n]+)',
                r'Status[:\s]+([^,\n]+)',
                r'Availability[:\s]+([^,\n]+)',
                r'(Open|Closed|Full|Available|Limited)'
            ]
            
            for pattern in availability_patterns:
                match = re.search(pattern, container_text, re.I)
                if match:
                    course_info['availability'] = match.group(1).strip()
                    break
            
            # Only return if we have at least a course name
            if course_info['course_name'] != 'Not Available':
                return course_info
            
        except Exception as e:
            logger.warning(f"Error extracting course from container: {e}")
        
        return None
    
    def _find_course_links(self, soup, base_url):
        """Find links that might lead to course pages"""
        course_links = []
        base_netloc = urlparse(base_url).netloc
        
        # Enhanced course keywords for executive education sites
        course_keywords = [
            'course', 'courses', 'class', 'program', 'programs', 'curriculum', 'syllabus', 
            'training', 'workshop', 'executive', 'education', 'mba', 'mim', 'emba',
            'certificate', 'diploma', 'degree', 'module', 'session', 'seminar'
        ]
        
        # Look for links with course-related text or href
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            link_text = link.get_text(strip=True).lower()
            
            # Check if link text OR href contains course keywords
            href_lower = href.lower()
            if any(keyword in link_text for keyword in course_keywords) or any(keyword in href_lower for keyword in course_keywords):
                full_url = urljoin(base_url, href)
                # Keep only same-domain links to avoid external noise
                if urlparse(full_url).netloc == base_netloc:
                    course_links.append(full_url)
        
        # Also look for navigation menus that might contain course links
        nav_selectors = ['nav', '.navigation', '.menu', '.navbar', '.breadcrumb']
        for selector in nav_selectors:
            nav_elem = soup.select_one(selector)
            if nav_elem:
                nav_links = nav_elem.find_all('a', href=True)
                for link in nav_links:
                    href = link.get('href')
                    link_text = link.get_text(strip=True).lower()
                    href_lower = href.lower()
                    
                    if any(keyword in link_text for keyword in course_keywords) or any(keyword in href_lower for keyword in course_keywords):
                        full_url = urljoin(base_url, href)
                        if urlparse(full_url).netloc == base_netloc:
                            course_links.append(full_url)
        
        # Look for Stanford-specific course patterns
        if 'stanford' in base_url.lower():
            # Look for course URLs in the page content
            page_text = soup.get_text()
            course_url_patterns = [
                r'/courses/[^"\s]+',
                r'/course/[^"\s]+',
                r'/program/[^"\s]+'
            ]
            
            for pattern in course_url_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    full_url = urljoin(base_url, match)
                    if urlparse(full_url).netloc == base_netloc:
                        course_links.append(full_url)
        
        logger.info(f"Found {len(course_links)} potential course links")
        return list(set(course_links))  # Remove duplicates
    
    def _extract_single_course(self, url, base_url):
        """Extract information from a single course page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Create a virtual container with the entire page
            container = soup.find('body') or soup
            course = self._extract_single_course_from_container(container, base_url)
            if course:
                course = self._apply_fallbacks(course, soup)
            return course
            
        except Exception as e:
            logger.warning(f"Failed to extract from {url}: {e}")
            return None

    def _apply_fallbacks(self, course_info, soup):
        """Apply page-level metadata fallbacks for missing fields"""
        try:
            # Institute fallback from og:site_name or title
            if course_info.get('institute_name') in (None, '', 'Not Available'):
                og_site = soup.find('meta', attrs={'property': 'og:site_name'})
                if og_site and og_site.get('content'):
                    course_info['institute_name'] = og_site['content'].strip()
                elif soup.title and soup.title.get_text(strip=True):
                    title_text = soup.title.get_text(strip=True)
                    for sep in ['|', '–', '-', '—', '·']:
                        if sep in title_text:
                            title_text = title_text.split(sep)[0].strip()
                            break
                    course_info['institute_name'] = title_text

            # Language fallback from html lang
            if course_info.get('language') in (None, '', 'Not Available'):
                html_tag = soup.find('html')
                lang = html_tag.get('lang') if html_tag else None
                if lang:
                    course_info['language'] = lang
        except Exception:
            pass
        return course_info

    def _apply_page_metadata(self, course_info, soup, base_url):
        """Apply page-level metadata to course information"""
        try:
            # Extract institute name from page content
            if course_info.get('institute_name') in (None, '', 'Not Available'):
                page_text = soup.get_text()
                institute_patterns = [
                    r'(LBS\s+Centre\s+for\s+Science\s+&\s+Technology)',
                    r'(LBS\s+Centre\s+for\s+Science\s+and\s+Technology)',
                    r'(LBS\s+Centre)',
                    r'(Stanford\s+University)',
                    r'(INSEAD)',
                    r'(HEC\s+Paris)',
                    r'(IMD\s+Business\s+School)'
                ]
                
                for pattern in institute_patterns:
                    match = re.search(pattern, page_text, re.I)
                    if match:
                        course_info['institute_name'] = match.group(1).strip()
                        break
            
            # Extract location from page content
            if course_info.get('location') in (None, '', 'Not Available'):
                page_text = soup.get_text()
                location_patterns = [
                    r'(Kerala,\s*India)',
                    r'(Thiruvananthapuram,\s*Kerala)',
                    r'(LBS\s+Centre,\s*Kerala)',
                    r'(Stanford,\s*CA)',
                    r'(Stanford,\s*California)',
                    r'(Fontainebleau,\s*France)',
                    r'(Singapore)',
                    r'(Abu\s+Dhabi)',
                    r'(Lausanne,\s*Switzerland)',
                    r'(Paris,\s*France)'
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, page_text, re.I)
                    if match:
                        course_info['location'] = match.group(1).strip()
                        break
            
            # Set default language for most university websites
            if course_info.get('language') in (None, '', 'Not Available'):
                course_info['language'] = 'English'
                
        except Exception as e:
            logger.warning(f"Error applying page metadata: {e}")
        
        return course_info

# Initialize the extractor
extractor = CourseExtractor()

@app.route('/api/extract', methods=['POST'])
def extract_courses():
    """Extract course information from provided URLs"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        results = []
        for url in urls:
            if url.strip():
                result = extractor.extract_course_info(url.strip())
                results.append(result)
        
        response = jsonify({
            'success': True,
            'results': results,
            'total_courses': sum(len(r.get('courses', [])) for r in results if r.get('success'))
        })
        return response
        
    except Exception as e:
        logger.error(f"Error in extract endpoint: {e}")
        error_response = jsonify({'error': str(e)})
        return error_response, 500

@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export extracted course data to CSV"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'No data to export'}), 400
        
        # Flatten all courses into a single list
        all_courses = []
        for result in results:
            if result.get('success') and result.get('courses'):
                for course in result['courses']:
                    course['source_url'] = result['url']
                    all_courses.append(course)
        
        if not all_courses:
            return jsonify({'error': 'No courses found to export'}), 400
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'courses_export_{timestamp}.csv'
        
        # Save to temporary CSV file
        temp_path = f'temp_{filename}'
        fieldnames = [
            'course_name', 'institute_name', 'location', 'format', 'faculty',
            'language', 'dates', 'duration', 'suitable_for', 'fees', 'availability',
            'source_url'
        ]
        with open(temp_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for course in all_courses:
                # Ensure all expected fields exist
                row = {key: course.get(key, 'Not Available') for key in fieldnames}
                writer.writerow(row)
        
        # Send file
        response = send_file(temp_path, as_attachment=True, download_name=filename)
        
        # Clean up temporary file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(temp_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error in CSV export: {e}")
        error_response = jsonify({'error': str(e)})
        return error_response, 500

@app.route('/api/export/excel', methods=['POST'])
def export_excel():
    """Export extracted course data to Excel"""
    try:
        data = request.get_json()
        results = data.get('results', [])
        
        if not results:
            return jsonify({'error': 'No data to export'}), 400
        
        # Flatten all courses into a single list
        all_courses = []
        for result in results:
            if result.get('success') and result.get('courses'):
                for course in result['courses']:
                    course['source_url'] = result['url']
                    all_courses.append(course)
        
        if not all_courses:
            return jsonify({'error': 'No courses found to export'}), 400
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'courses_export_{timestamp}.xlsx'
        
        # Save to temporary Excel file using openpyxl
        temp_path = f'temp_{filename}'
        headers = [
            'course_name', 'institute_name', 'location', 'format', 'faculty',
            'language', 'dates', 'duration', 'suitable_for', 'fees', 'availability',
            'source_url'
        ]
        wb = Workbook()
        ws = wb.active
        ws.title = 'Courses'
        ws.append([h.replace('_', ' ').title() for h in headers])
        for course in all_courses:
            row = [course.get(h, 'Not Available') for h in headers]
            ws.append(row)
        wb.save(temp_path)
        
        # Send file
        response = send_file(temp_path, as_attachment=True, download_name=filename)
        
        # Clean up temporary file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.remove(temp_path)
            except:
                pass
        
        return response
        
    except Exception as e:
        logger.error(f"Error in Excel export: {e}")
        error_response = jsonify({'error': str(e)})
        return error_response, 500

@app.route('/')
def index():
    """Main page"""
    response = make_response(render_template('index.html'))
    return response

@app.route('/sw.js')
def service_worker():
    response = send_from_directory('static', 'sw.js')
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    response = jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    return response



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

