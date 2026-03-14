# Genealogy Archive APIs and Databases Research

## Overview
This document provides comprehensive research on available genealogy archive APIs and databases that can be accessed programmatically, with a focus on French genealogy resources.

---

## 1. Free/Paid APIs for Genealogy Research

### A. FamilySearch API (FREE)
**Status:** Free for both individuals and organizations
**Type:** Nonprofit genealogy API
**Key Features:**
- Comprehensive REST API with dozens of resources
- Genealogies, Pedigree, Names, Search and Match, and Places endpoints
- Built on GEDCOM X specifications
- Community-driven development with FamilySearch Developer Forum

**Authentication:**
- OAuth 2.0 with 4 grant types:
  1. Authorization Code (for Web Apps, Desktop, Mobile)
  2. Unauthenticated Session (limited endpoints: Places, Date Authority, Person Search, Person Matches Query, Relationship Finder)
  3. Client Credentials (restricted to service accounts)
  4. Password Grant (requires approved developer keys)
- Access tokens obtained from developer portal at https://developers.familysearch.org

**API Endpoints:**
- Family Tree: Persons, relationships, sources, matches, notes, pedigrees, search, change history
- Memories: Memory management, artifacts, personas, comments
- Standards: Date standardization, places, names, vocabularies
- Users: Agent and user account information
- Genealogies: Separate genealogies data management
- User Trees: Groups and tree management

**Data Formats:** JSON with GEDCOM X schema compliance

**Rate Limits:**
- Per-user basis (or app key if unauthenticated)
- Up to 18 seconds of processing time per 1-minute window
- HTTP 429 (Service Unavailable) response when throttled
- Retry-After header indicates wait time
- Different endpoints may have different throttling windows based on load

**Documentation:** https://developers.familysearch.org/

---

### B. MyHeritage Family Graph API (FREE with approval)
**Type:** RESTful API
**Key Features:**
- Read-only API (no write/upload capabilities)
- JSON response format
- Access to genealogy data and family trees
- Creates data bridges between MyHeritage and other platforms

**Access Requirements:**
- No NDAs required
- No usage fees
- Must request application key and await approval
- No specific rate limits documented in public resources

**Current Capabilities:**
- Download genealogy data
- Read family tree information
- Cannot write or modify data (read-only)

**2026 Update:** MyHeritage announced Scribe AI for transcribing, translating, and interpreting historical documents

**Documentation:** https://www.familygraph.com/

---

### C. Geni API (FREE with registration)
**Type:** RESTful API
**Key Features:**
- Simple access to core genealogy features
- Supports both JSON and XML formats (JSON default)
- Public documentation available
- Developer-friendly

**Access Requirements:**
- Must register application at https://sandbox.geni.com
- Sandbox environment available for testing
- Can request approval for higher rate limits

**Rate Limits:**
- Default low rate limit for new/unapproved applications
- Higher limits available after approval request to project discussions

**Documentation & Resources:**
- Main API docs: http://dev.geni.com
- Test environment: https://sandbox.geni.com/platform/developer/api_explorer
- Community forum for support

---

### D. Geneanet (PARTIAL API)
**Status:** Freemium model
**Type:** Community genealogy platform (French-focused)

**Members:** 4-5 million members, 9 billion+ individuals in family trees

**Free Features:**
- Unlimited family tree creation
- Advanced search by first and last name (free since 2015)
- Access to community-submitted genealogies
- Non-tree collections available to all users

**API Access:**
- Offers a surname/origin API for surname information
- Free API access documented at: https://en.geneanet.org/genealogy/api/API
- Limited technical documentation on public API endpoints

**Premium Features:**
- Email alerts for new matches
- Access to genealogy library with 3 billion indexed individuals
- Enhanced content and archives
- Discount: -59% until March 14, 2026

**Free Premium Access:**
- Available through FamilySearch member access
- Available at no charge at all FamilySearch center locations
- LDS/Church members can access for free

**Archives Coverage:** Primarily French records (état civil, censuses, church records)

---

### E. Ancestry.com API (NOT PUBLIC)
**Status:** Private API (no public access as of 2026)
**Restriction:** Prohibits third-party tools and external API access in Terms and Conditions
**Note:** Family Tree Maker and MyHeritage API for Family Tree Builder remain private

---

### F. Filae (PREMIUM - French genealogy specialist)
**Type:** Premium genealogy database with French archives
**Collections:** 1+ billion digitized and transcribed genealogical records from France

**Records Available:**
- Civil registrations (births, marriages, deaths)
- Census records
- Church and military records
- Historical collections (20th-century tables of successions and absences)
- Recent additions: 1911, 1921, 1931 censuses; 1926 Paris census; 1936 Paris census

**Access Methods:**
- Premium subscription (with 59% discount until March 14, 2026)
- Free access for Church members (Latter-day Saints)
- Acquisition by MyHeritage (2021)

**API Status:** No documented public API; data accessed through web interface

---

## 2. French-Specific Archives

### A. Archives Nationales (National Archives)
**Coverage:** National-level historical documents
**Digitization:** Nearly 5 million images of various archives (photographs, texts, maps)

**Data Access:**
- Published through French Ministry of Culture data portal: https://data.culture.gouv.fr
- Descriptions available in XML-EAD format
- API Endpoints available through data.culture.gouv.fr

**Datasets:**
1. Corpus d'archives numérisées des Archives nationales
2. Grands documents et images de l'histoire de France

**Technical Implementation:**
- No dedicated SPARQL endpoint or RDF/XML format API
- Reference materials available (latest version 1.1 from June 2022)
- GitHub repository for referentiels: https://github.com/ArchivesNationalesFR/Referentiels

**Genealogy Records:**
- Civil registration, parish registers, population censuses
- Only civil status registers over 100 years old published online

---

### B. Archives Départementales (Departmental Archives)
**Coverage:** 96 departmental archives covering all of France's municipalities
**Digitization Rate:** 90% of 440 million documents digitized; 76% available online

**Records Available:**
- Parish registers (baptisms, marriages, burials before 1793)
- Civil registration records (births, marriages, deaths, divorces since 1793)
- Census records
- Military records
- Historical documents and maps

**Access Method:**
- Free online through individual departmental archive websites
- Approximately 95% of online archive consultations are for genealogical research
- Most departments have separate websites with digitized collections

**OpenDataSoft Integration:**
- Some departments use OpenDataSoft for API access
- Example: Hauts-de-Seine (92) provides maps and plans API
- Dataset: Cartes et plans anciens — Open Data Hauts-de-Seine
- Available at: https://hauts-de-seine.opendatasoft.com/

**Data Availability:**
- Civil records: Available online (over 100 years old published)
- Parish records: Digitized and online in most departments
- Census data: Digitized and online
- Military records: Available through various departments

**Portal:** https://www.archives-departementales.com/ (directory of online archives)

---

### C. Gallica - Bibliothèque Nationale de France (BnF) Digital Library (FREE)
**Type:** National digital library with genealogy resources
**Content:** Printed materials, graphic materials, sound recordings

**Genealogy Collections:**
- Dictionaries of important residents for 44 ancient French provinces (pre-1789)
- Regional dictionaries for other parts of France
- Historical documents, maps, engravings

**API Access:**
- BnF provides multiple API endpoints through https://api.bnf.fr
- Multiple APIs for different collections

**API Endpoints:**
1. API Document de Gallica - Extract metadata and documents
2. Gallica métadonnées - Collection metadata
3. Gallica documents in TEI format

**Data Formats:**
- CSV (UTF-8)
- JSON format available for archive metadata
- TEI (Text Encoding Initiative) format for encoded documents
- ARK persistent identifiers (begin with ark:/12148/)

**Rate Limits:** Not specifically documented in public resources

**Authentication:** Open access for most content (no API key required for basic queries)

**Documentation:** https://api.bnf.fr/en/

---

### D. FranceArchives Portal
**URL:** https://francearchives.gouv.fr/
**Type:** Central aggregator for French archives
**Content:** Links and descriptions of archival resources across France

**Data Available:**
- Statistics on archive services activity
- Directory of public archive services (updated ongoing)
- Annual reports ("Des Archives en France") from SIAF
- Descriptions of digitized archives

**Coverage:**
- 100 departmental archive services
- Approximately 500 municipal and intercommunal archive services
- Access to digitized holdings descriptions

---

## 3. Free APIs and Open Data

### Summary Table

| Service | Free Tier | API Type | Authentication | Format |
|---------|-----------|----------|----------------|--------|
| FamilySearch | Yes | REST | OAuth 2.0 | JSON (GEDCOM X) |
| MyHeritage Graph | Yes (approval) | REST | Application key | JSON |
| Geni | Yes (limited rate) | REST | App registration | JSON/XML |
| Geneanet | Yes (limited) | Partial | Free registration | JSON |
| Archives Nationales | Yes | Data portal | None (open) | XML-EAD |
| Archives Départementales | Yes | Web/OpenDataSoft | None (open) | JSON/CSV |
| Gallica (BnF) | Yes | REST | None (mostly open) | JSON/CSV/TEI |
| Filae | No (premium) | Web only | Subscription | HTML/PDF |
| Ancestry.com | No | Private | N/A | N/A |

---

## 4. Data Formats Returned

### GEDCOM X (FamilySearch standard)
**Specifications:**
- GEDCOM X JSON Serialization Format (official spec)
- GEDCOM X XML Serialization Format
- GEDCOM X file format (compressed zip with multiple files)

**Includes:**
- Person information (names, dates, places)
- Relationships (parent-child, spouse)
- Sources and source references
- Citations and evidence references
- Contributor metadata
- Media attachments (photos, documents, videos, audio)
- Notes and conclusions
- Place and date formats

**GitHub Specification:** https://github.com/FamilySearch/gedcomx

**Example Structure:**
```json
{
  "persons": [...],
  "relationships": [...],
  "sources": [...],
  "notes": [...],
  "media": [...]
}
```

### JSON Format
- **FamilySearch API:** GEDCOM X JSON schema
- **MyHeritage:** Native JSON responses
- **Geni:** JSON (default) with structured genealogy objects
- **Gallica/BnF:** JSON for metadata with ARK identifiers
- **Archives Départementales (OpenDataSoft):** JSON datasets

### CSV Format
- **Archives Nationales:** CSV (UTF-8) for datasets
- **Gallica/BnF:** CSV metadata exports
- **Departmental Archives:** CSV datasets where available

### XML Format
- **GEDCOM X:** XML serialization available
- **Geni API:** XML alternative format
- **Archives Nationales:** XML-EAD (archival metadata)
- **BnF:** TEI-XML for encoded documents

### Proprietary Formats
- **Filae:** HTML/PDF interface (no API)
- **Traditional GEDCOM:** Older genealogy format (.ged files)

---

## 5. Rate Limits and Restrictions

### FamilySearch API
- **Type:** Per-user throttling
- **Limit:** Up to 18 seconds of processing time per 1-minute window
- **Response:** HTTP 429 (Service Unavailable) when exceeded
- **Retry:** Retry-After header specifies wait time (in seconds)
- **Note:** Different endpoints may have different limits based on load

### MyHeritage Family Graph API
- **Type:** Per-application
- **Limit:** Not publicly specified (dependent on approval level)
- **Rate Limit Request:** Contact MyHeritage for details

### Geni API
- **Type:** Per-application
- **Default:** Very low rate limit for new/unapproved applications
- **Approval:** Can request higher limits through project discussions
- **Endpoint:** Post to API project discussions for approval request

### Geneanet API
- **Limit:** Not publicly documented
- **Type:** Likely per-application or per-user basis
- **Status:** Limited public documentation available

### Archives Nationales & Départementales
- **Type:** Open data (no authentication)
- **Limit:** None specified (web crawling restrictions may apply)
- **Note:** Individual departmental sites may have their own policies

### Gallica (BnF) API
- **Type:** Open access (no authentication required)
- **Limit:** Not officially documented
- **Note:** Respectful crawling recommended for bulk requests

### Filae
- **Type:** Premium subscription
- **Limit:** No API access (web-based only)

---

## 6. Authentication Methods Summary

| Service | Method | Details |
|---------|--------|---------|
| FamilySearch | OAuth 2.0 Bearer Token | 4 grant types (Authorization Code, Unauthenticated, Client Credentials, Password) |
| MyHeritage | Application Key | Request and approval required |
| Geni | Application Registration | Sandbox testing available |
| Geneanet | Free Registration | Basic free access; premium for full features |
| Archives Nationales | None (Open) | Direct access to data portal |
| Archives Départementales | None (Open) | Direct access to individual department websites |
| Gallica (BnF) | None (Open) | Direct API access; no API key required |
| Filae | Subscription Login | Web-based authentication only |

---

## 7. Key Recommendations

### For Free, Comprehensive Access
1. **FamilySearch API** - Best for international genealogy and GEDCOM X standardization
2. **Archives Nationales + Départementales** - Best for French-specific records (free, open data)
3. **Gallica (BnF)** - Best for historical documents and French regional resources

### For French Genealogy Specifically
1. Start with Archives Départementales (free, comprehensive coverage)
2. Use Geneanet for community records and French specialists
3. Access Filae if premium content needed (via LDS/Church membership or subscription)
4. Supplement with Gallica for historical documents and regional information

### For API Integration
1. **FamilySearch:** Most mature, well-documented API with GEDCOM X support
2. **MyHeritage:** Good for family tree bridge applications (requires approval)
3. **OpenDataSoft (Hauts-de-Seine example):** Template for departmental archive APIs
4. **BnF API:** For historical documents and regional content

### Cost Analysis
- **Free tiers available:** FamilySearch, Geni, Geneanet (limited), Archives, Gallica
- **Approval-based free:** MyHeritage (requires review)
- **Premium only:** Filae (unless LDS membership), Ancestry
- **Total free research capability:** Quite comprehensive for French genealogy

---

## 8. Additional Resources

### Developer Portals
- FamilySearch: https://developers.familysearch.org/
- MyHeritage: https://www.familygraph.com/
- Geni: http://dev.geni.com
- BnF API: https://api.bnf.fr/
- French Data Portal: https://data.culture.gouv.fr/

### Documentation & Specifications
- GEDCOM X Spec: https://github.com/FamilySearch/gedcomx
- GEDCOM 7.0: https://gedcom.io/
- FamilySearch GitHub: https://github.com/FamilySearch
- Archives Nationales GitHub: https://github.com/ArchivesNationalesFR/

### French Genealogy Guides
- FamilySearch France Wiki: https://www.familysearch.org/en/wiki/France
- FranceGenWeb: https://www.worldgenweb.net/france/
- Making French Genealogy Easier: https://frenchgen.com/
- OnGenealogy French Resources: https://www.ongenealogy.com/

---

## 9. Implementation Notes

### Starting with FamilySearch API
```
1. Register at https://developers.familysearch.org/
2. Get OAuth 2.0 credentials
3. Request access token
4. Make REST calls to Family Tree endpoints
5. Parse GEDCOM X JSON responses
```

### Accessing French Archives
```
1. Determine target department(s)
2. Visit individual Archives Départementales website
3. Search digitized collections (mostly free)
4. Download documents as PDF
5. For bulk access: Check for OpenDataSoft APIs
```

### Using Open Data from BnF
```
1. Query https://api.bnf.fr/ endpoints
2. Request JSON or CSV metadata
3. Use ARK identifiers for persistence
4. No authentication required
5. Respect rate limits (uncongested but should be respectful)
```

---

## Document Version
- **Created:** March 13, 2026
- **Research Scope:** Comprehensive genealogy APIs with focus on French resources
- **Last Updated:** March 13, 2026
