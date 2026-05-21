from __future__ import annotations

from analysis.analyzers.base import BaseAnalyzer
from analysis.extractors import (
    deduplicate_offers,
    extract_multiple_structured_offers,
    extract_offers_from_text,
    extract_price_evidence,
    extract_structured_offer,
)
from analysis.models import (
    DocumentAnalysis,
    DocumentKind,
    DocumentMetadata,
    DownloadedDocument,
    ImageInfo,
)
from bs4 import BeautifulSoup


class HtmlAnalyzer(BaseAnalyzer):
    def analyze(self, document: DownloadedDocument) -> DocumentAnalysis:
        html = document.content.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "lxml")

        page_text = soup.get_text("\n", strip=True)
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        description = None
        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag:
            description = description_tag.get("content")

        images: list[ImageInfo] = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            images.append(
                ImageInfo(
                    url=src,
                    alt_text=img.get("alt"),
                )
            )

        links = [a.get("href") for a in soup.find_all("a", href=True)]
        offers = deduplicate_offers(
            self._extract_j51_menu_offers(html, document.url)
            + self._extract_structured_offers(soup, document.url)
            + self._extract_heading_sequence_offers(soup, document.url)
            + extract_offers_from_text(page_text, document.url, confidence=0.75)
        )
        detected_prices = extract_price_evidence(page_text, document.url, confidence=0.6)
        language = soup.html.get("lang") if soup.html else None

        return DocumentAnalysis(
            source_url=document.url,
            final_url=document.final_url,
            kind=DocumentKind.HTML,
            metadata=DocumentMetadata(
                title=title,
                description=description,
                language=language,
                content_type=document.content_type,
                status_code=document.status_code,
                headers=document.headers,
                discovered_links=[link for link in links if link],
            ),
            extracted_text=page_text,
            offers=offers,
            images=images,
            detected_prices=detected_prices,
            raw_signals={
                "has_schema_org_menu": "schema.org" in html.lower() and "menu" in html.lower(),
                "image_count": len(images),
                "link_count": len(links),
            },
        )

    def _extract_structured_offers(self, soup: BeautifulSoup, source_url: str):
        offers = []
        for item in soup.select("article.item"):
            text_nodes = [node.get_text(" ", strip=True) for node in item.find_all(["p", "span", "div"])]
            if len(text_nodes) < 2:
                continue

            # Many cafe menus render item name + price in sibling tags rather than one text line.
            # We keep the parent section heading so names like "French Vanilla" still count as coffee
            # when they appear under a "Coffee" section.
            section = item.find_parent("section")
            section_heading = None
            if section is not None:
                heading = section.find(["h1", "h2", "h3"])
                if heading is not None:
                    section_heading = heading.get_text(" ", strip=True)
            candidate = extract_structured_offer(
                name=text_nodes[0],
                price_text=text_nodes[-1],
                source_url=source_url,
                confidence=0.95,
                menu_context=section_heading,
            )
            if candidate is not None:
                offers.append(candidate)
        return offers

    def _extract_j51_menu_offers(self, html: str, source_url: str):
        import re

        pattern = re.compile(
            r'<h3[^>]*class="[^"]*j51_menu_item_title[^"]*"[^>]*>\s*(?P<name>[^<]*?)\s*</h3\s*>\s*'
            r'<div[^>]*class="[^"]*j51_menu_item_spacer[^"]*"[^>]*></div>\s*'
            r'<span[^>]*class="[^"]*j51_menu_item_price[^"]*"[^>]*>\s*(?P<price>[^<]*?)\s*</span\s*>',
            re.IGNORECASE | re.DOTALL,
        )

        offers = []
        section_heading = None
        for match in pattern.finditer(html):
            name = " ".join(match.group("name").split())
            price_text = " ".join(match.group("price").split())
            if not name:
                continue
            if not price_text:
                section_heading = name
                continue
            offers.extend(
                extract_multiple_structured_offers(
                    name=name,
                    price_text=price_text,
                    source_url=source_url,
                    confidence=0.98,
                    menu_context=section_heading,
                )
            )
        return offers

    def _extract_heading_sequence_offers(self, soup: BeautifulSoup, source_url: str):
        offers = []
        section_heading = None
        pending_name = None

        for node in soup.find_all(["h1", "h2", "h3", "h4", "h5"]):
            text = node.get_text(" ", strip=True)
            if not text:
                continue

            if node.name == "h5":
                section_heading = text
                pending_name = None
                continue

            if node.name == "h4":
                if "€" in text or "$" in text:
                    if pending_name:
                        offers.extend(
                            extract_multiple_structured_offers(
                                name=pending_name,
                                price_text=text,
                                source_url=source_url,
                                confidence=0.96,
                                menu_context=section_heading,
                            )
                        )
                        pending_name = None
                    continue

                pending_name = text

        return offers
