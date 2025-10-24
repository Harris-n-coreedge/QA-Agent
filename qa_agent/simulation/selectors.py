"""
Robust element targeting and selector management.
"""
from playwright.async_api import Page, Locator
from typing import List, Dict, Any, Optional
import re


class SelectorManager:
    """Manages robust element targeting strategies."""
    
    def __init__(self):
        self.selector_strategies = [
            self._try_text_selector,
            self._try_role_selector,
            self._try_css_selector,
            self._try_xpath_selector,
            self._try_attribute_selector
        ]
    
    async def find_element(self, page: Page, selector: str) -> Locator:
        """Find element using multiple strategies."""
        for strategy in self.selector_strategies:
            try:
                element = await strategy(page, selector)
                if element and await element.count() > 0:
                    return element
            except Exception:
                continue
        
        raise ValueError(f"Could not find element with selector: {selector}")
    
    async def _try_text_selector(self, page: Page, selector: str) -> Optional[Locator]:
        """Try text-based selector."""
        if selector.startswith("text="):
            text = selector[5:]
            return page.locator(f"text={text}")
        return None
    
    async def _try_role_selector(self, page: Page, selector: str) -> Optional[Locator]:
        """Try role-based selector."""
        if selector.startswith("role="):
            role = selector[5:]
            return page.locator(f"[role='{role}']")
        return None
    
    async def _try_css_selector(self, page: Page, selector: str) -> Optional[Locator]:
        """Try CSS selector."""
        # Basic CSS selector patterns
        css_patterns = [
            r"^#[a-zA-Z][\w-]*$",  # ID selector
            r"^\.[a-zA-Z][\w-]*$",  # Class selector
            r"^[a-zA-Z][\w-]*$",    # Tag selector
            r"^\[.*\]$",            # Attribute selector
        ]
        
        for pattern in css_patterns:
            if re.match(pattern, selector):
                return page.locator(selector)
        
        return None
    
    async def _try_xpath_selector(self, page: Page, selector: str) -> Optional[Locator]:
        """Try XPath selector."""
        if selector.startswith("//") or selector.startswith("/"):
            return page.locator(f"xpath={selector}")
        return None
    
    async def _try_attribute_selector(self, page: Page, selector: str) -> Optional[Locator]:
        """Try attribute-based selector."""
        # Common attribute patterns
        attribute_patterns = [
            r"^name=",
            r"^id=",
            r"^class=",
            r"^data-",
            r"^aria-"
        ]
        
        for pattern in attribute_patterns:
            if re.match(pattern, selector):
                return page.locator(f"[{selector}]")
        
        return None
    
    def generate_fallback_selectors(self, element_info: Dict[str, Any]) -> List[str]:
        """Generate fallback selectors for an element."""
        selectors = []
        
        # ID selector
        if element_info.get("id"):
            selectors.append(f"#{element_info['id']}")
        
        # Class selector
        if element_info.get("class"):
            classes = element_info["class"].split()
            for cls in classes:
                selectors.append(f".{cls}")
        
        # Name attribute
        if element_info.get("name"):
            selectors.append(f"[name='{element_info['name']}']")
        
        # Text content
        if element_info.get("text"):
            text = element_info["text"].strip()
            if len(text) < 50:  # Avoid very long text selectors
                selectors.append(f"text={text}")
        
        # Role attribute
        if element_info.get("role"):
            selectors.append(f"[role='{element_info['role']}']")
        
        # Tag name
        if element_info.get("tag"):
            selectors.append(element_info["tag"])
        
        return selectors
    
    async def wait_for_element(
        self,
        page: Page,
        selector: str,
        timeout: int = 5000
    ) -> Locator:
        """Wait for element to be available."""
        element = await self.find_element(page, selector)
        await element.wait_for(timeout=timeout)
        return element
    
    async def is_element_visible(self, page: Page, selector: str) -> bool:
        """Check if element is visible."""
        try:
            element = await self.find_element(page, selector)
            return await element.is_visible()
        except Exception:
            return False
    
    async def get_element_info(self, page: Page, selector: str) -> Dict[str, Any]:
        """Get detailed information about an element."""
        element = await self.find_element(page, selector)
        
        return await page.evaluate("""
            (element) => {
                return {
                    tag: element.tagName.toLowerCase(),
                    id: element.id,
                    class: element.className,
                    name: element.name,
                    role: element.getAttribute('role'),
                    text: element.textContent?.trim(),
                    href: element.href,
                    type: element.type,
                    value: element.value
                };
            }
        """, element.first)
