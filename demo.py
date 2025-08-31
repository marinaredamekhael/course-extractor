#!/usr/bin/env python3
"""
Demo script for Course Extractor
Shows how to use the CourseExtractor class programmatically
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import CourseExtractor

def demo_extraction():
    """Demonstrate course extraction functionality"""
    print("🚀 Course Extractor Demo")
    print("=" * 50)
    
    # Initialize the extractor
    extractor = CourseExtractor()
    
    # Example URLs to test
    test_urls = [
        "https://www.coursera.org/courses",
        "https://www.edx.org/search?subject=Computer%20Science"
    ]
    
    print(f"Testing with {len(test_urls)} URLs...")
    print()
    
    for i, url in enumerate(test_urls, 1):
        print(f"🔍 Processing URL {i}: {url}")
        print("-" * 40)
        
        try:
            # Extract course information
            result = extractor.extract_course_info(url)
            
            if result['success']:
                print(f"✅ Success! Found {result['courses_found']} courses")
                
                # Show first few courses
                if result['courses']:
                    print("\n📚 Sample courses:")
                    for j, course in enumerate(result['courses'][:3], 1):
                        print(f"   {j}. {course.get('course_name', 'N/A')}")
                        print(f"      Institute: {course.get('institute_name', 'N/A')}")
                        print(f"      Format: {course.get('format', 'N/A')}")
                        print(f"      Duration: {course.get('duration', 'N/A')}")
                        print()
                else:
                    print("   No courses found on this page")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error processing {url}: {e}")
        
        print()
    
    print("🎉 Demo completed!")
    print("\nTo run the full web application:")
    print("1. python app.py")
    print("2. Open http://localhost:5000 in your browser")

def demo_single_url():
    """Demo with a single URL"""
    print("🎯 Single URL Demo")
    print("=" * 30)
    
    url = input("Enter a URL to test: ").strip()
    if not url:
        print("No URL provided. Using default...")
        url = "https://www.coursera.org/courses"
    
    extractor = CourseExtractor()
    
    print(f"\n🔍 Processing: {url}")
    print("-" * 40)
    
    try:
        result = extractor.extract_course_info(url)
        
        if result['success']:
            print(f"✅ Success! Found {result['courses_found']} courses")
            
            if result['courses']:
                print(f"\n📊 Summary:")
                print(f"   Total courses: {result['courses_found']}")
                
                # Count formats
                formats = {}
                for course in result['courses']:
                    fmt = course.get('format', 'Not Available')
                    formats[fmt] = formats.get(fmt, 0) + 1
                
                print(f"   Course formats:")
                for fmt, count in formats.items():
                    print(f"     {fmt}: {count}")
                
                # Show sample course
                sample = result['courses'][0]
                print(f"\n📚 Sample course details:")
                for key, value in sample.items():
                    print(f"   {key.replace('_', ' ').title()}: {value}")
            else:
                print("   No courses found on this page")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    print("Choose demo mode:")
    print("1. Multi-URL demo (recommended)")
    print("2. Single URL demo")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            demo_extraction()
            break
        elif choice == '2':
            demo_single_url()
            break
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
