# Public records request: Belmont tax title and delinquent real estate accounts

Belmont does not publish its delinquent or tax-title list online. The Treasurer/Collector's own
FAQ says: "For the list of Tax Title properties, please contact the Treasurer/Collector's Office
via email." Send the request below; under the Massachusetts Public Records Law (M.G.L. c. 66, s. 10)
the town must respond within 10 business days.

**To:** treasurers@belmont-ma.gov
**Cc:** the Town Clerk / Records Access Officer, townclerk@belmont-ma.gov (optional)
**Subject:** Public records request - tax title accounts and delinquent real estate taxes

---

Dear Treasurer/Collector,

Under the Massachusetts Public Records Law, M.G.L. c. 66, s. 10, I request electronic copies
(Excel or CSV preferred) of the following records:

1. The current list of real estate **tax title accounts** held by the Town of Belmont, including
   for each account the parcel ID (map-lot), property address, assessed owner(s) of record, the
   fiscal years included, the date of the Instrument of Taking and its Middlesex South Registry
   book/page, and the current balance (tax, interest, fees) as of the date of the response.

2. A list of all real estate parcels with **unpaid real estate taxes** for fiscal years 2025 and
   2026 (any quarter past due as of the date of the response), including parcel ID, property
   address, owner of record, and amount past due.

3. Any **Notices of Tax Taking** and **advertisements of intent to take** issued by the Collector
   from January 1, 2023 to the present, and any list of parcels included in each taking.

4. Any record of **tax receivable assignments or tax lien sales** (M.G.L. c. 60, s. 2C / s. 52)
   made by the Town in the last five years, including the parcels involved.

If any portion of these records is withheld, please identify the specific exemption relied upon
and release the remainder, as the statute requires. If the fee will exceed $25, please send an
itemized estimate before proceeding. I am happy to receive the records in whatever electronic
format the Town's collection software (e.g., MUNIS) exports.

Thank you,

[Name]
[Mailing address]
[Phone] / [Email]

---

## What to do with the response

1. Save the list as `belmont/data/tax_delinquent_known.csv` using these columns:
   `parcel_id,property_address,owner_name,status,as_of_date,source_url,notes`
   (parcel_id must match the assessor map-lot format used in the workbook, e.g. `30-15` or `10-100-1`).
2. Re-run `python belmont/pipeline/build_lists.py`. Every matching parcel is flagged
   `tax_delinquent = YES`, gets +10 priority, and appears on the "Tax delinquent (known)" sheet.

## Independent cross-check: Middlesex South Registry of Deeds

Every completed tax taking is recorded, so the Registry is a public source that does not depend
on the town answering:

1. Go to https://www.masslandrecords.com/MiddlesexSouth/ and open Recorded Land > Search Criteria.
2. Search **Name**: `BELMONT TOWN OF` (also try `TOWN OF BELMONT`, `BELMONT TOWN`), party type
   *Grantee*, document types **TAKING** / **TAX TAKING** / **INSTRUMENT OF TAKING**, date range
   2015 to today. The grantor on each hit is the delinquent owner; the document lists the parcel
   address and amount.
3. Also search document type **LIEN** and **TAX LIEN** in Belmont for federal (IRS) and
   Massachusetts DOR liens on individuals, and **REDEMPTION** to remove parcels that have since paid.
4. For any parcel of interest, use the deed book/page in the workbook to pull the current deed and
   confirm the owner before making contact.
