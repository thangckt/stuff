// Logging visistors
// By Thang Nguyen


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
    { ip: '205.169.39.45', browser: 'Chrome-117', os: 'Windows-10.0' },
    { ip: '34.72.176.129', browser: 'Chrome-125', os: 'Linux-Unk' },
];

function checkIfBlocked(visitorInfo, blackList) {
    // Check if the visitor is in the blacklist
    for (const blockedInfo of blackList) {
        // Block only if ALL keys in the entry match (AND logic)
        const allMatch = Object.keys(blockedInfo).every(key => {
            const actual = visitorInfo[key]?.toString().trim();
            const expected = blockedInfo[key]?.toString().trim();
            return actual && expected && actual.includes(expected);
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
        const sheet = checkIfBlocked(jsonData, blackListCrawler)
            ? doc.getSheetByName('crawler')
            : doc.getSheetByName('visistor');

        if (!sheet) {
            throw new Error("No active sheet found.");
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
        Logger.log('Error in record_data: ' + error.message); // Log detailed error
    } finally {
        lock.releaseLock(); // Release lock once done
    }
}