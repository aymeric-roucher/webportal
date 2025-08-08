import random
import requests
from typing import Optional
import time


class ProxyManager:
    """Manages proxy rotation for stealth crawling"""
    
    def __init__(self):
        # Free proxy lists (for testing - consider premium services for production)
        self.free_proxy_sources = [
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        ]
        self.proxies = []
        self.working_proxies = []
        self.last_refresh = 0
        self.refresh_interval = 3600  # Refresh every hour
    
    def fetch_free_proxies(self) -> list[str]:
        """Fetch free proxies from various sources"""
        all_proxies = []
        
        for source in self.free_proxy_sources:
            try:
                response = requests.get(source, timeout=30)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    all_proxies.extend([p.strip() for p in proxies if p.strip()])
            except Exception as e:
                print(f"Failed to fetch proxies from {source}: {e}")
        
        return all_proxies
    
    def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip', 
                proxies=proxies, 
                timeout=timeout
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def refresh_proxies(self):
        """Refresh the proxy list and test them"""
        current_time = time.time()
        
        if current_time - self.last_refresh < self.refresh_interval:
            return
        
        print("Refreshing proxy list...")
        self.proxies = self.fetch_free_proxies()
        self.working_proxies = []
        
        # Test a subset of proxies (testing all would take too long)
        test_count = min(50, len(self.proxies))
        test_proxies = random.sample(self.proxies, test_count) if len(self.proxies) > test_count else self.proxies
        
        for proxy in test_proxies:
            if self.test_proxy(proxy, timeout=5):
                self.working_proxies.append(proxy)
                print(f"Working proxy found: {proxy}")
        
        print(f"Found {len(self.working_proxies)} working proxies out of {test_count} tested")
        self.last_refresh = current_time
    
    def get_random_proxy(self) -> Optional[dict]:
        """Get a random working proxy"""
        self.refresh_proxies()
        
        if not self.working_proxies:
            return None
        
        proxy = random.choice(self.working_proxies)
        return {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
    
    def get_proxy_for_selenium(self) -> Optional[str]:
        """Get proxy string formatted for Selenium"""
        proxy_dict = self.get_random_proxy()
        if proxy_dict:
            # Extract the proxy address from the dict
            proxy_url = proxy_dict['http']
            return proxy_url.replace('http://', '')
        return None


# Global proxy manager instance
_proxy_manager = None

def get_proxy_manager() -> ProxyManager:
    """Get singleton proxy manager instance"""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = ProxyManager()
    return _proxy_manager