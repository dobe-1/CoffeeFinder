export const COFFEE_SHOP_EXAMPLE = `{
  "name": "Kulturcafé", // overpassAPI: parsed from OSM name
  "coordinates": [
    51.4458619, // overpassAPI: parsed from OSM geometry
    7.2595206 // overpassAPI: parsed from OSM geometry
  ],
  "category": "Cafe", // overpassAPI: hardcoded in Coffeeshop Model creation
  "website": {
    "url": "https://asta-bochum.de/kulturcafe/", // overpassAPI: parsed from OSM website
    "extracted_at": "2026-07-08T17:51:28.630072Z", // overpassAPI: set when website URL is present
    "last_checked": "2026-07-08T17:57:17.112385Z", // webscraper: set after website crawl
    "accessible": true // webscraper: set after website crawl
  },
  "menu": {
    "menu_url": "https://asta-bochum.de/kulturcafe-preise/",
    // overpassAPI: initial candidate from website:menu
    // webscraper: otherwise candidate from discovered links
    // webscraper: overwritten for each tested candidate
    // final: first candidate with extracted items, else last tried
    "menu_url_last_checked": "2026-07-08T17:57:21.743621Z",
    // webscraper: set after each candidate request
    // final: timestamp of final attempted candidate
    "menu_url_accessible": true,
    // webscraper: set after each candidate request
    // final: status of final attempted candidate
    "currency": "EUR", // extractor: defaults to EUR if items found
    "extracted_at": "2026-07-08T17:57:21.743608Z", // extractor: set when extraction succesful
    "items": [
      {
        "name": "Cappuccino", // extractor: parsed from successful candidate
        "price": 2.4 // extractor: parsed from successful candidate
      }
    ]
  }
}`;
