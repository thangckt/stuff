// Logging visistors
// By Thang Nguyen
// Updated: 2026Mar06


// GoogleAppsScript function to handle CORS and save JSON to a sheet
function doPost(e) {
  try {
    const jsonData = JSON.parse(e.postData.contents); // Parse the incoming JSON data
    record_data(jsonData); // Record the data to the Sheet
  } catch (error) {
    Logger.log('Error in doPost: ' + error.message);
    // Return error response
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', 'message': error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}


// Filter visitors based on IP, ASN, or other fields
const blackListCrawler = [ // Define blacklist list-of-dictionaries
  { ip: '34.72.176.129', browser: 'Chrome-125', os: 'Linux-Unk' }, // google
  { ip: '34.123.170.104', browser: 'Chrome-125', os: 'Linux-Unk' }, // google
  { org: 'Tencent Building, Kejizhongyi Avenue', asn: 'AS132203', os: 'Windows-10.0' }, // Tencent
  { org: "Alibaba US Technology Co., Ltd.", asn: 'AS45102', browser: 'Chrome-125', os: 'macOS-10.15.7' }, // Alibaba
  { org: 'Facebook, Inc.', asn: 'AS32934', os: 'Windows-10.0' }, // Facebook
  { ip: '205.169.39.45', browser: 'Chrome-117', os: 'Windows-10.0' },
  { ip: '43.173.181.218', browser: 'Chrome-116', os: 'Windows-10.0' },
  { ip: '187.190.192.48', browser: 'Chrome-133', os: 'Windows-10.0' },
];

function checkIfCrawler(visitorInfo, blackList) {
  // Check if the visitor is in the blacklist
  for (const blockedInfo of blackList) {
    // Block only if ALL keys in the entry match (AND logic)
    const allMatch = Object.keys(blockedInfo).every(key => {
      const actual = visitorInfo[key]?.toString().trim();
      const expected = blockedInfo[key]?.toString().trim();
      return actual !== undefined && actual.includes(expected);
    });
    if (allMatch) return true;
  }
  return false;
}


// Function to write data to Google Sheet
function record_data(jsonData) {
  const lock = LockService.getDocumentLock();
  lock.waitLock(30000); // Wait for up to 30 seconds to avoid concurrent writes

  try {
    const doc = SpreadsheetApp.getActiveSpreadsheet();
    const isCrawler = checkIfCrawler(jsonData, blackListCrawler); // Check if visitor is a crawler
    const sheetName = isCrawler ? 'crawler' : 'visitor';
    const sheet = doc.getSheetByName(sheetName);

    if (!sheet) {
      throw new Error(`Sheet "${sheetName}" not found. Available sheets: ${doc.getSheets().map(s => s.getName()).join(', ')}`);
    }

    // Get current sheet headers (first row)
    const currentHeader = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const updatedHeader = currentHeader.slice(); // Copy current header to update later if necessary

    const row = [new Date()]; // Start new row with a timestamp

    // Loop through each key-value pair in form data
    for (var key in jsonData) {
      if (Object.prototype.hasOwnProperty.call(jsonData, key)) {
        var headerIndex = currentHeader.indexOf(key);

        if (headerIndex > -1) {
          // If key exists in header, ensure the row array is long enough
          row[headerIndex] = jsonData[key];
        } else {
          // Add new header if key is new
          updatedHeader.push(key);
          row.push(jsonData[key]); // Append new data to the row
        }
      }
    }

    // Append new row to sheet
    const nextRow = sheet.getLastRow() + 1;
    sheet.getRange(nextRow, 1, 1, row.length).setValues([row]);

    // Update header if new columns were added
    if (updatedHeader.length > currentHeader.length) {
      sheet.getRange(1, 1, 1, updatedHeader.length).setValues([updatedHeader]);
    }

  } catch (error) {
    Logger.log(`[record_data] ERROR: ${error.message}`);
    Logger.log(`[record_data] Stack: ${error.stack}`);
  } finally {
    lock.releaseLock(); // Release lock once done
  }
}