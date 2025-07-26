"""Tests for sitemap functionality in crawl.py"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import requests

from src.webportal.get_skeleton.crawl import FastJSCrawler


# Sample sitemap XML content for testing
SAMPLE_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/</loc>
    </url>
    <url>
        <loc>https://example.com/page1</loc>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
    </url>
    <url>
        <loc>https://example.com/category/item1</loc>
    </url>
    <url>
        <loc>https://example.com/category/item2</loc>
    </url>
    <url>
        <loc>https://example.com/deep/nested/path/page</loc>
    </url>
    <url>
        <loc>https://example.com/static/style.css</loc>
    </url>
    <url>
        <loc>https://otherdomain.com/external</loc>
    </url>
</urlset>
"""

SIMPLE_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
    <url>
        <loc>https://example.com/</loc>
    </url>
    <url>
        <loc>https://example.com/simple</loc>
    </url>
</urlset>
"""


def test_load_sitemap_success():
    """Test successful sitemap loading"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    # Mock the requests.get call
    mock_response = Mock()
    mock_response.content = SAMPLE_SITEMAP_XML.encode('utf-8')
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        urls = crawler.load_sitemap()
        
        # Verify the request was made correctly
        mock_get.assert_called_once_with('https://example.com/sitemap.xml', timeout=10)
        mock_response.raise_for_status.assert_called_once()
        
        # Verify URLs were extracted correctly
        expected_urls = [
            'https://example.com/',
            'https://example.com/page1',
            'https://example.com/page2',
            'https://example.com/category/item1',
            'https://example.com/category/item2',
            'https://example.com/deep/nested/path/page',
            'https://example.com/static/style.css',
            'https://otherdomain.com/external'
        ]
        assert len(urls) == len(expected_urls)
        assert all(url in urls for url in expected_urls)


def test_load_sitemap_no_namespace():
    """Test sitemap loading without XML namespace"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    mock_response = Mock()
    mock_response.content = SIMPLE_SITEMAP_XML.encode('utf-8')
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        urls = crawler.load_sitemap()
        
        expected_urls = ['https://example.com/', 'https://example.com/simple']
        assert len(urls) == 2
        assert all(url in urls for url in expected_urls)


def test_load_sitemap_request_failure():
    """Test sitemap loading when request fails"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    with patch('requests.get', side_effect=requests.RequestException("Not found")):
        urls = crawler.load_sitemap()
        assert urls == []


def test_load_sitemap_invalid_xml():
    """Test sitemap loading with invalid XML"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    mock_response = Mock()
    mock_response.content = b"Not valid XML content"
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        urls = crawler.load_sitemap()
        assert urls == []


def test_filter_sitemap_urls_max_pages():
    """Test filtering respects max_pages limit"""
    crawler = FastJSCrawler("https://example.com", max_pages=3, use_sitemap=True)
    
    urls = [
        'https://example.com/page1',
        'https://example.com/page2', 
        'https://example.com/page3',
        'https://example.com/page4',
        'https://example.com/page5'
    ]
    
    filtered = crawler.filter_sitemap_urls(urls)
    assert len(filtered) == 3


def test_filter_sitemap_urls_static_assets():
    """Test filtering removes static assets"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    urls = [
        'https://example.com/page1',
        'https://example.com/static/style.css',
        'https://example.com/images/logo.png',
        'https://example.com/page2'
    ]
    
    filtered = crawler.filter_sitemap_urls(urls)
    expected = ['https://example.com/page1', 'https://example.com/page2']
    assert filtered == expected


def test_filter_sitemap_urls_different_domain():
    """Test filtering removes URLs from different domains"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    urls = [
        'https://example.com/page1',
        'https://otherdomain.com/external',
        'https://subdomain.example.com/sub',  # Should be allowed (subdomain)
        'https://example.com/page2'
    ]
    
    filtered = crawler.filter_sitemap_urls(urls)
    expected = [
        'https://example.com/page1',
        'https://subdomain.example.com/sub',
        'https://example.com/page2'
    ]
    assert filtered == expected


def test_filter_sitemap_urls_max_depth():
    """Test filtering respects max_depth limit"""
    crawler = FastJSCrawler("https://example.com/base", max_depth=2, use_sitemap=True)
    
    urls = [
        'https://example.com/base',           # depth 0 (relative to start)
        'https://example.com/base/level1',    # depth 1
        'https://example.com/base/l1/l2',     # depth 2
        'https://example.com/base/l1/l2/l3',  # depth 3 (should be filtered)
        'https://example.com/other'           # depth -1 (different base, should be kept)
    ]
    
    filtered = crawler.filter_sitemap_urls(urls)
    expected = [
        'https://example.com/base',
        'https://example.com/base/level1',
        'https://example.com/base/l1/l2',
        'https://example.com/other'
    ]
    assert filtered == expected


def test_sitemap_url_pattern_extraction():
    """Test that sitemap URLs are processed into templates correctly"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    # Mock successful sitemap loading
    mock_response = Mock()
    mock_response.content = SAMPLE_SITEMAP_XML.encode('utf-8')
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        # Test the full sitemap processing workflow
        sitemap_urls = crawler.load_sitemap()
        filtered_urls = crawler.filter_sitemap_urls(sitemap_urls)
        
        # Process URLs to build templates
        for url in filtered_urls:
            normalized_url = crawler.normalize_url(url)
            normalized_url = crawler._replace_with_generic_pattern_if_necessary(normalized_url)
            
            matching_template_index = crawler.matches_existing_template(normalized_url)
            if matching_template_index == -1:
                crawler.log_new_fixed_template(normalized_url)
        
        # Verify that templates were created
        assert len(crawler.pattern_templates) > 0
        
        # Check that similar URLs created variable templates
        # Both /category/item1 and /category/item2 should create a template with variable segment
        category_templates = [
            t for t in crawler.pattern_templates 
            if any(
                hasattr(seg, 'example') and seg.example == 'category' 
                for seg in t.segments
            )
        ]
        assert len(category_templates) > 0


def test_crawl_with_sitemap_sync():
    """Test sitemap workflow synchronously"""
    crawler = FastJSCrawler("https://example.com", max_pages=5, use_sitemap=True)
    
    # Mock successful sitemap loading
    mock_response = Mock()
    mock_response.content = SAMPLE_SITEMAP_XML.encode('utf-8')
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        # Test the sitemap loading and filtering workflow
        sitemap_urls = crawler.load_sitemap()
        filtered_urls = crawler.filter_sitemap_urls(sitemap_urls)
        
        # Process URLs to build templates (mimicking what crawl() does)
        for url in filtered_urls:
            normalized_url = crawler.normalize_url(url)
            normalized_url = crawler._replace_with_generic_pattern_if_necessary(normalized_url)
            
            matching_template_index = crawler.matches_existing_template(normalized_url)
            if matching_template_index == -1:
                crawler.log_new_fixed_template(normalized_url)
            
            crawler.visited.add(url)
        
        # Verify that URLs were processed
        assert len(crawler.visited) > 0
        assert len(crawler.pattern_templates) > 0
        
        # Verify max_pages was respected
        assert len(crawler.visited) <= 5


def test_sitemap_fallback_detection():
    """Test that crawler detects when sitemap fails"""
    crawler = FastJSCrawler("https://example.com", use_sitemap=True)
    
    # Mock failed sitemap loading
    with patch('requests.get', side_effect=requests.RequestException("Not found")):
        urls = crawler.load_sitemap()
        assert urls == []  # Should return empty list on failure