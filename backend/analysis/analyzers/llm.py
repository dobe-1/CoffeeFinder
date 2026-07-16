import base64
import json
import os

from openai import OpenAI

from backend.analysis.models import DocumentAnalysis
from backend.models.menu import Menu, MenuItem

from .base import BaseAnalyzer

# only for testing
import requests


PROMPT = """\
Analyze the following document. This document may or may not be a restaurant/ café menu.
Your task is to find the price of a "Cappuccino" on this menu if present.
Rules:
This document might not be a menu at all. It could be any webpage or document.
Only if you are completly confident that this is a menu and that a "Cappuccino" 
(or a close variant like "Capuccino") is listed, 
Do not guess, hallucinate or lie about the prices.
If you are unsure or it is not present, respond with found=false.
Respond only with JSON in this exact schema:
{
"found": <bool>,
"cappuccino_price": <float or null>,
"currency": <"EUR", "USD", or null>
}
The document:
"""


class LlmAnalyzer(BaseAnalyzer):
    def __init__(self, analyzer_type: str):
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE")
        self.model = os.environ.get("OPENAI_MODEL")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.analyzer_type = analyzer_type

    def build_prompt(self, data, content_type) -> list[dict]:

        base64_data = base64.b64encode(data).decode("ascii")
        match self.analyzer_type:
            case "image":
                prompt = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_data}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ]
            case "text":
                text_content = data.decode("utf-8")
                prompt = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {"type": "text", "text": text_content},
                        ],
                    }
                ]
            case "pdf":
                prompt = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_data}",
                                },
                            },
                        ],
                    }
                ]
            case _:
                # TODO error catching
                return None

        return prompt

    def call_llm(self, messages: list[dict]):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        #print(raw)
        # Strip markdown
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [l for l in lines[1:] if l.strip() != "```"]
            raw = "\n".join(lines).strip()
        # TODO enforce structured output over api
        return json.loads(raw)

    def analyze(
        self,
        data: bytes,
        content_type: str,
        source_url: str | None = None,
    ) -> DocumentAnalysis:
        warnings: list[str] = []

        prompt = self.build_prompt(data, content_type)
        if prompt is None:
            warnings.append(f"LLM analysis failed for {source_url or 'unknown source'}")
            return DocumentAnalysis(
                source_url=source_url,
                content_type=content_type,
                extracted_text=None,
                menu=None,
                warnings=warnings,
            )

        result = None
        try:
            result = self.call_llm(prompt)
        except Exception as exc:
            print(exc)
            warnings.append(f"LLM analysis failed for {source_url or 'unknown source'}: {exc}")

        items: list[MenuItem] = []
        if result and result.get("found") and result.get("cappuccino_price") is not None:
            items.append(MenuItem(name="Cappuccino", price=float(result["cappuccino_price"])))

        return DocumentAnalysis(
            source_url=source_url,
            content_type=content_type,
            extracted_text=None,
            menu=Menu(
                items=items,
                currency="EUR",
            ),
            warnings=warnings,
        )


# testing stuff
if __name__ == "__main__":
    print("PDF TESTING")
    url_text = "https://cafe-extrablatt.de/fileadmin/pdf/Speisekarten/Cafe-Extrablatt-Bochum-Speisekarte-Web.pdf?1779093393"
    response = requests.get(
        url_text,
        headers={"User-Agent": "CoffeeFinderBot"},
        timeout=15,
    )
    text_type = response.headers.get("Content-Type", "").lower().split(";")[0].strip()

    llm_pdf = LlmAnalyzer("pdf")
    text_res = llm_pdf.analyze(response.content, text_type)
    print(
        f"Extracted {text_res.menu.items[0].name} price {text_res.menu.items[0].price} {text_res.menu.currency}"
    )

    print("HTML TESTING")
    url_text = "https://oktober.cafe/speisekarte/"
    response = requests.get(
        url_text,
        headers={"User-Agent": "CoffeeFinderBot"},
        timeout=15,
    )
    text_type = response.headers.get("Content-Type", "").lower().split(";")[0].strip()

    llm_text = LlmAnalyzer("text")
    text_res = llm_text.analyze(response.content, text_type)
    print(
        f"Extracted {text_res.menu.items[0].name} price {text_res.menu.items[0].price} {text_res.menu.currency}"
    )
